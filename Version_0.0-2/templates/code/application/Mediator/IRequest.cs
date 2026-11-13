namespace {{ProjectName}}.Application.Mediator;

/// <summary>
/// A request that produces a response of type <typeparamref name="TResponse"/>.
/// </summary>
public interface IRequest<TResponse>
{
}

/// <summary>
/// A request that produces no response.
/// </summary>
public interface IRequest
{
}
