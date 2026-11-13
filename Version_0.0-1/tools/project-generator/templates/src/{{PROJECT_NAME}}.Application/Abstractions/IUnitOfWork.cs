namespace Asispass.Application;

/// <summary>
/// Commits the persistence changes staged during one application operation.
/// The contract is provider independent: Application must not reference
/// a concrete context, a database technology or a transaction type.
/// </summary>
public interface IUnitOfWork
{
	/// <summary>
	/// Persists every change staged in the current scope as one atomic unit.
	/// Repositories stage changes; committing is the caller's decision.
	/// </summary>
	Task CommitAsync(CancellationToken cancellationToken = default);
}
