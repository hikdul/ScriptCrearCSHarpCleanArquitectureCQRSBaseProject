using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using {{ProjectName}}.Infrastructure;

namespace {{ProjectName}}.Infrastructure.Tests;

public class InfrastructureRegistrationTests
{
    [Fact]
    public void AddInfrastructure_Registers_DbContext()
    {
        var services = new ServiceCollection();
        services.AddInfrastructure("Server=localhost;Database=unused");

        using var provider = services.BuildServiceProvider();
        var context = provider.GetRequiredService<{{ProjectName}}DbContext>();

        context.Should().NotBeNull();
    }

    [Fact]
    public void AddInfrastructure_Registers_The_Selected_Database_Provider()
    {
        var services = new ServiceCollection();
        services.AddInfrastructure("Server=localhost;Database=unused");

        using var provider = services.BuildServiceProvider();
        using var context = provider.GetRequiredService<{{ProjectName}}DbContext>();

        context.Database.ProviderName.Should().Be("{{ProviderName}}");
    }
}