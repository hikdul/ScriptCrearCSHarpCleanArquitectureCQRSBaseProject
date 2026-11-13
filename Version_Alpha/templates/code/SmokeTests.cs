using {{ProjectName}}.{{Layer}};

namespace {{ProjectName}}.{{TestLayer}};

public class SmokeTests
{
    [Fact]
    public void {{Layer}}_assembly_is_available()
    {
        Assert.NotNull(typeof(AssemblyMarker).Assembly);
    }
}
