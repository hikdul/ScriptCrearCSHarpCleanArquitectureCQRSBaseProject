using Xunit;

namespace {{ProjectName}}.TestSupport;

/// <summary>
/// A theory that runs only when the configured database provider is reachable.
/// See <see cref="DatabaseFactAttribute"/>.
/// </summary>
public sealed class DatabaseTheoryAttribute : TheoryAttribute
{
    public DatabaseTheoryAttribute()
    {
        if (string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(DatabaseFactAttribute.ConnectionStringVariable)))
        {
            Skip = $"Set {DatabaseFactAttribute.ConnectionStringVariable} to run the gated database tests.";
        }
    }
}
