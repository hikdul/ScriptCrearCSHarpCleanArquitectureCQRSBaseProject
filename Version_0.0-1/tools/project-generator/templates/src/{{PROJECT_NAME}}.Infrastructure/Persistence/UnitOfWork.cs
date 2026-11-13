using {{PROJECT_NAME}}.Application;
using Microsoft.EntityFrameworkCore;

namespace {{PROJECT_NAME}}.Infrastructure.Persistence;

/// <summary>
/// Entity Framework Core implementation of the Application Unit of Work.
/// It commits through the scoped context, so EF Core's implicit transaction
/// makes one command's changes atomic.
/// </summary>
public sealed class UnitOfWork : IUnitOfWork
{
	private readonly {{PROJECT_NAME}}DbContext context;

	public UnitOfWork({{PROJECT_NAME}}DbContext context)
	{
		this.context = context;
	}

	public Task CommitAsync(CancellationToken cancellationToken = default) =>
		context.SaveChangesAsync(cancellationToken);
}
