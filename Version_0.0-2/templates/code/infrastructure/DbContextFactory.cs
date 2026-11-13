using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace {{ProjectName}}.Infrastructure;

/// <summary>
/// Creates the design-time context used by <c>dotnet ef</c>.
/// <para>
/// The connection string comes from the environment so no credential is stored
/// in the repository. The host never uses this factory: it composes the context
/// from configuration at runtime.
/// </para>
/// </summary>
public sealed class {{ProjectName}}DbContextFactory : IDesignTimeDbContextFactory<{{ProjectName}}DbContext>
{
    public const string ConnectionStringVariable = "{{ConnectionStringVariable}}";

    public {{ProjectName}}DbContext CreateDbContext(string[] args)
    {
        var connectionString = Environment.GetEnvironmentVariable(ConnectionStringVariable);
        if (string.IsNullOrWhiteSpace(connectionString))
        {
            throw new InvalidOperationException(
                $"Set {ConnectionStringVariable} before running Entity Framework Core tooling.");
        }

        var options = new DbContextOptionsBuilder<{{ProjectName}}DbContext>()
            .{{ProviderMethod}}(connectionString)
            .Options;

        return new {{ProjectName}}DbContext(options);
    }
}
