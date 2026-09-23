using Microsoft.EntityFrameworkCore;

namespace {{ProjectName}}.Infrastructure;

public sealed class {{ProjectName}}DbContext : DbContext
{
    public {{ProjectName}}DbContext(DbContextOptions<{{ProjectName}}DbContext> options)
        : base(options)
    {
    }
}