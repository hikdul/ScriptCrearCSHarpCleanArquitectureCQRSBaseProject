using {{ProjectName}}.Application.Abstractions;
using Microsoft.EntityFrameworkCore;

namespace {{ProjectName}}.Infrastructure;

/// <summary>
/// Entity Framework Core implementation of the Application Unit of Work.
/// It commits through the scoped context, so EF Core's implicit transaction
/// makes one command's changes atomic.
/// </summary>
public sealed class UnitOfWork : IUnitOfWork
{
    private readonly {{ProjectName}}DbContext context;

    public UnitOfWork({{ProjectName}}DbContext context)
    {
        this.context = context;
    }

    public Task CommitAsync(CancellationToken cancellationToken = default) =>
        context.SaveChangesAsync(cancellationToken);
}
