using System.Collections;
using System.Collections.Concurrent;
using System.Linq.Expressions;
using {{ProjectName}}.Application.Abstractions;
using {{ProjectName}}.Application.Exceptions;

namespace {{ProjectName}}.Application.Mediator;

/// <summary>
/// In-process mediator that resolves the single handler registered for a
/// request and invokes it through a compiled delegate.
///
/// Dispatching concerns only: no domain rules, no application rules,
/// no persistence, no event publishing.
/// </summary>
public class SimpleMediator : IMediator
{
    private const string HandleMethodName = "Handle";

    private static readonly ConcurrentDictionary<(Type Request, Type? Response), Func<object, object, CancellationToken, object>> Invokers = new();

    private readonly IServiceProvider serviceProvider;

    public SimpleMediator(IServiceProvider serviceProvider)
    {
        this.serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
    }

    /// <summary>
    /// Sends a request that produces a response.
    /// </summary>
    public Task<TResponse> Send<TResponse>(IRequest<TResponse> request, CancellationToken cancellationToken = default)
    {
        if (request is null)
        {
            throw new MediatorException("A null request cannot be dispatched by the mediator.");
        }

        var requestType = request.GetType();
        var handlerContract = typeof(IRequestHandler<,>).MakeGenericType(requestType, typeof(TResponse));
        var handler = ResolveSingleHandler(handlerContract, requestType, typeof(TResponse));
        var invoke = GetInvoker(requestType, typeof(TResponse));

        return (Task<TResponse>)invoke(handler, request, cancellationToken);
    }

    /// <summary>
    /// Sends a request that produces no response and completes with the handler.
    /// </summary>
    public Task Send(IRequest request, CancellationToken cancellationToken = default)
    {
        if (request is null)
        {
            throw new MediatorException("A null request cannot be dispatched by the mediator.");
        }

        var requestType = request.GetType();
        var handlerContract = typeof(IRequestHandler<>).MakeGenericType(requestType);
        var handler = ResolveSingleHandler(handlerContract, requestType, responseType: null);
        var invoke = GetInvoker(requestType, responseType: null);

        return (Task)invoke(handler, request, cancellationToken);
    }

    /// <summary>
    /// Resolves the one and only handler registered for the contract.
    /// Resolution never happens through a single-service lookup, because the
    /// built-in container silently returns the last of several registrations.
    /// </summary>
    private object ResolveSingleHandler(Type handlerContract, Type requestType, Type? responseType)
    {
        var registrations = serviceProvider.GetService(typeof(IEnumerable<>).MakeGenericType(handlerContract)) as IEnumerable;
        var handlers = registrations is null
            ? Array.Empty<object>()
            : registrations.Cast<object>().Where(handler => handler is not null).ToArray();

        if (handlers.Length == 1)
        {
            return handlers[0];
        }

        var expected = responseType is null
            ? $"request '{requestType.Name}'"
            : $"request '{requestType.Name}' with response '{responseType.Name}'";

        throw handlers.Length > 1
            ? new MediatorException(
                $"Duplicate handler registration: {handlers.Length} handlers are registered for {expected}. "
                + "Dispatch requires exactly one matching handler.")
            : new MediatorException($"No handler is registered for {expected}.");
    }

    /// <summary>
    /// Builds (and caches) a compiled delegate that calls the handler's
    /// <c>Handle</c> method. A compiled delegate is used instead of
    /// <see cref="System.Reflection.MethodBase.Invoke(object, object[])"/> so a
    /// handler failure reaches the caller with its original exception type
    /// instead of a reflection-specific wrapper.
    /// </summary>
    private static Func<object, object, CancellationToken, object> GetInvoker(Type requestType, Type? responseType)
    {
        return Invokers.GetOrAdd(
            (requestType, responseType),
            key => BuildInvoker(key.Request, key.Response));
    }

    private static Func<object, object, CancellationToken, object> BuildInvoker(Type requestType, Type? responseType)
    {
        var handlerContract = responseType is null
            ? typeof(IRequestHandler<>).MakeGenericType(requestType)
            : typeof(IRequestHandler<,>).MakeGenericType(requestType, responseType);

        var handle = handlerContract.GetMethod(HandleMethodName)
            ?? throw new MediatorException(
                $"Handler contract '{handlerContract.Name}' does not expose a '{HandleMethodName}' method.");

        var handler = Expression.Parameter(typeof(object), "handler");
        var request = Expression.Parameter(typeof(object), "request");
        var cancellationToken = Expression.Parameter(typeof(CancellationToken), "cancellationToken");

        var call = Expression.Call(
            Expression.Convert(handler, handlerContract),
            handle,
            Expression.Convert(request, requestType),
            cancellationToken);

        return Expression
            .Lambda<Func<object, object, CancellationToken, object>>(
                Expression.Convert(call, typeof(object)),
                handler,
                request,
                cancellationToken)
            .Compile();
    }
}
