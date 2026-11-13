using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using {{ProjectName}}.Application.Abstractions;
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
        using var scope = provider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<{{ProjectName}}DbContext>();

        context.Should().NotBeNull();
    }

    [Fact]
    public void AddInfrastructure_Registers_The_Selected_Database_Provider()
    {
        var services = new ServiceCollection();
        services.AddInfrastructure("Server=localhost;Database=unused");

        using var provider = services.BuildServiceProvider();
        using var scope = provider.CreateScope();
        using var context = scope.ServiceProvider.GetRequiredService<{{ProjectName}}DbContext>();

        context.Database.ProviderName.Should().Be("{{ProviderName}}");
    }

    [Fact]
    public void AddInfrastructure_Registers_UnitOfWork()
    {
        var services = new ServiceCollection();
        services.AddInfrastructure("Server=localhost;Database=unused");

        using var provider = services.BuildServiceProvider();
        using var scope = provider.CreateScope();
        var unitOfWork = scope.ServiceProvider.GetRequiredService<IUnitOfWork>();

        unitOfWork.Should().NotBeNull();
    }
}
