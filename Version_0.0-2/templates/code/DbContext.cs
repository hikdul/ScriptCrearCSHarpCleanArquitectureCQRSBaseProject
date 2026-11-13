using Microsoft.EntityFrameworkCore;

namespace {{ProjectName}}.Infrastructure;

/// <summary>
/// The application database context.
/// <para>
/// The schema is created and changed by committed EF Core migrations, never by
/// the host at start-up. Entity configurations are discovered from this
/// assembly so the model stays split into small, focused classes.
/// </para>
/// </summary>
public sealed class {{ProjectName}}DbContext(DbContextOptions<{{ProjectName}}DbContext> options)
    : DbContext(options)
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(typeof({{ProjectName}}DbContext).Assembly);
    }
}
