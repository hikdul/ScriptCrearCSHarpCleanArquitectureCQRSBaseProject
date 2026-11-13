using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace {{ProjectName}}.TestSupport;

/// <summary>
/// Creates an in-memory SQLite database that lives as long as the returned
/// connection stays open. Used by the default test tier: persistence tests
/// run everywhere, without any database service.
/// </summary>
public static class SqliteDatabase
{
    public static DbContextOptions<TContext> CreateOptions<TContext>(out SqliteConnection connection)
        where TContext : DbContext
    {
        connection = new SqliteConnection("DataSource=:memory:");
        connection.Open();

        return new DbContextOptionsBuilder<TContext>()
            .UseSqlite(connection)
            .Options;
    }
}
