using FluentAssertions;
using {{ProjectName}}.Domain;

namespace {{ProjectName}}.Domain.Tests;

public class EntityIdTests
{
    [Fact]
    public void New_returns_a_uuid_version_7()
    {
        var id = EntityId.New();

        id.ToString()[14].Should().Be('7');
    }

    [Fact]
    public void New_identifiers_are_unique()
    {
        var first = EntityId.New();
        var second = EntityId.New();

        first.Should().NotBe(second);
    }

    [Fact]
    public void New_identifiers_created_in_sequence_have_non_decreasing_timestamps()
    {
        var first = EntityId.New();
        Thread.Sleep(2); // force a new millisecond tick
        var second = EntityId.New();

        string.CompareOrdinal(TimestampPrefix(first), TimestampPrefix(second))
            .Should().BeLessThanOrEqualTo(0);
    }

    // RFC 9562 UUIDv7: the first 48 bits are a big-endian Unix-epoch
    // millisecond timestamp. In the "n" format the leading 12 hex digits
    // carry it, so a lexicographic comparison orders by creation time.
    private static string TimestampPrefix(Guid id) => id.ToString("n")[..12];
}
