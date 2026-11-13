using NetArchTest.Rules;

namespace {{ProjectName}}.Architecture.Tests;

public class ArchitectureTests
{
    private const string DomainNamespace = "{{ProjectName}}.Domain";
    private const string SecurityNamespace = "{{ProjectName}}.Security";
    private const string ApplicationNamespace = "{{ProjectName}}.Application";
    private const string InfrastructureNamespace = "{{ProjectName}}.Infrastructure";
    private const string ApiNamespace = "{{ProjectName}}.Api";

    [Fact]
    public void Domain_Should_Not_Depend_On_Application()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApplicationNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Domain_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Domain_Should_Not_Depend_On_Api()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApiNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Domain_Should_Not_Depend_On_Security()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(SecurityNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Security_Should_Not_Depend_On_Domain()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Security.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(DomainNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Security_Should_Not_Depend_On_Application()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Security.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApplicationNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Security_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Security.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Security_Should_Not_Depend_On_Api()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Security.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApiNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Application_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Application.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Application_Should_Not_Depend_On_Api()
    {
        var result = Types
            .InAssembly(typeof({{ProjectName}}.Application.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApiNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }
}
