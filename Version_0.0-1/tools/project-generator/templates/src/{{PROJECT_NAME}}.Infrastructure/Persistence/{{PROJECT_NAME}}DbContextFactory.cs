using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace {{PROJECT_NAME}}.Infrastructure.Persistence;

/// <summary>
/// Creates the design-time context used by <c>dotnet ef</c>.
/// <para>
/// The connection string comes from the environment so no credential is stored
/// in the repository. The host never uses this factory: it composes the context
/// from configuration at runtime.
/// </para>
/// </summary>
public sealed class {{PROJECT_NAME}}DbContextFactory : IDesignTimeDbContextFactory<{{PROJECT_NAME}}DbContext>
{
	public const string ConnectionStringVariable = "{{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING";

	public {{PROJECT_NAME}}DbContext CreateDbContext(string[] args)
	{
		var connectionString = Environment.GetEnvironmentVariable(ConnectionStringVariable);
		if (string.IsNullOrWhiteSpace(connectionString))
		{
			throw new InvalidOperationException(
				$"Set {ConnectionStringVariable} before running Entity Framework Core tooling.");
		}

		var options = new DbContextOptionsBuilder<{{PROJECT_NAME}}DbContext>()
			.UseSqlServer(connectionString)
			.Options;

		return new {{PROJECT_NAME}}DbContext(options);
	}
}
