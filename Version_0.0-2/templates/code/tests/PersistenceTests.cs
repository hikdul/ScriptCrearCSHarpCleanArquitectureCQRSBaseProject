using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using {{ProjectName}}.Infrastructure;
using {{ProjectName}}.TestSupport;

namespace {{ProjectName}}.Infrastructure.Tests;

public class PersistenceTests
{
    [Fact]
    public void DbContext_model_builds_and_can_ensure_created_on_sqlite()
    {
        var options = SqliteDatabase.CreateOptions<{{ProjectName}}DbContext>(out var connection);

        using (connection)
        {
            using var context = new {{ProjectName}}DbContext(options);

            context.Database.EnsureCreated().Should().BeTrue();
        }
    }

    [DatabaseFact]
    public void Configured_provider_can_open_connection()
    {
        var connectionString = Environment.GetEnvironmentVariable(
            DatabaseFactAttribute.ConnectionStringVariable);

        var services = new ServiceCollection();
        services.AddInfrastructure(connectionString!);

        using var provider = services.BuildServiceProvider();
        using var scope = provider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<{{ProjectName}}DbContext>();

        context.Database.CanConnect().Should().BeTrue();
    }
}
