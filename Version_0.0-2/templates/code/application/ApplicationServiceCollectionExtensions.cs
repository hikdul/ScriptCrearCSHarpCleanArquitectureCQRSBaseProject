using System.Reflection;
using {{ProjectName}}.Application.Abstractions;
using {{ProjectName}}.Application.Mediator;
using Microsoft.Extensions.DependencyInjection;

namespace {{ProjectName}}.Application;

/// <summary>
/// Registers the Application layer: every closed
/// <see cref="IRequestHandler{TRequest, TResponse}"/> and
/// <see cref="IRequestHandler{TRequest}"/> implementation found in this
/// assembly is registered against its handler contract, and the mediator
/// itself is wired. This makes the CQRS pipeline functional without any
/// manual per-handler registration.
/// </summary>
public static class ApplicationServiceCollectionExtensions
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        RegisterHandlers(services, typeof(ApplicationServiceCollectionExtensions).Assembly);
        services.AddTransient<IMediator, SimpleMediator>();
        return services;
    }

    private static void RegisterHandlers(IServiceCollection services, Assembly assembly)
    {
        foreach (var type in assembly.GetTypes())
        {
            if (type.IsAbstract || type.IsInterface || type.IsGenericTypeDefinition)
            {
                continue;
            }

            foreach (var handlerContract in type.GetInterfaces())
            {
                if (!handlerContract.IsGenericType)
                {
                    continue;
                }

                var definition = handlerContract.GetGenericTypeDefinition();
                if (definition == typeof(IRequestHandler<,>)
                    || definition == typeof(IRequestHandler<>))
                {
                    services.AddTransient(handlerContract, type);
                }
            }
        }
    }
}
