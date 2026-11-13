using {{ProjectName}}.Application.Mediator;

namespace {{ProjectName}}.Application.Abstractions;

/// <summary>
/// Dispatches a request to exactly one Application handler.
/// The mediator is a dispatch mechanism only: it holds no business rules,
/// performs no persistence and knows nothing about HTTP.
/// </summary>
public interface IMediator
{
    /// <summary>
    /// Sends a request that produces a response and returns the handler response.
    /// </summary>
    Task<TResponse> Send<TResponse>(IRequest<TResponse> request, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a request without a response and completes when the handler completes.
    /// </summary>
    Task Send(IRequest request, CancellationToken cancellationToken = default);
}
