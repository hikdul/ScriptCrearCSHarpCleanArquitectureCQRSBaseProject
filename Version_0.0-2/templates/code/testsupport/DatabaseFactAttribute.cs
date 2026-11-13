using Xunit;

namespace {{ProjectName}}.TestSupport;

/// <summary>
/// A fact that runs only when the configured database provider is reachable:
/// the gated test tier. It skips when the
/// <c>{{ConnectionStringVariable}}</c> environment variable is not set.
/// <para>
/// A skipped test is not a passing test. When a feature touches the schema,
/// a migration, the provider configuration or provider-specific behavior, a
/// green run with skips is not validation — set the environment variable and
/// require zero skips.
/// </para>
/// </summary>
public sealed class DatabaseFactAttribute : FactAttribute
{
    public const string ConnectionStringVariable = "{{ConnectionStringVariable}}";

    public DatabaseFactAttribute()
    {
        if (string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(ConnectionStringVariable)))
        {
            Skip = $"Set {ConnectionStringVariable} to run the gated database tests.";
        }
    }
}
