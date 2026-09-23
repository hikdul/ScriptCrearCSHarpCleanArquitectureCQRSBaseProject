# Database — PostgreSQL

The API uses **PostgreSQL 17** for local development.

## Start the database

```bash
docker compose up -d
```

This starts `{{ProjectNameLower}}-postgres` on `localhost:5432`
(database `{{ProjectNameLower}}`, user `postgres`, trust auth for local
development only).

To run this compose file directly from the `docker/` folder:

```bash
docker compose -f docker/docker-compose.postgres.yml up -d
```

## Connection string

```text
Host=localhost;Port=5432;Database={{ProjectNameLower}};Username=postgres
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. Override it in any environment
with the `ConnectionStrings__Default` environment variable.

## Switching to SQL Server

The `docker/` folder also contains `docker-compose.sqlserver.yml` for SQL
Server. To switch providers, regenerate the project with:

```bash
python3 generate_project.py {{ProjectName}} --database sqlserver
```

and start the SQL Server container with the SQL Server instructions below.

---

# Database — SQL Server (alternative)

Deploying SQL Server locally requires a strong `MSSQL_SA_PASSWORD`, stored
in `docker/.env` (generated and gitignored).

## Start the database

```bash
docker compose --env-file docker/.env up -d
```

or directly:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.sqlserver.yml up -d
```

This starts `{{ProjectNameLower}}-sqlserver` on `localhost:1433`
(database `{{ProjectNameLower}}`, user `sa`).

## Connection string

```text
Server=localhost,1433;Database={{ProjectNameLower}};User Id=sa;Password=<see docker/.env>;TrustServerCertificate=True
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. Override it in any environment
with the `ConnectionStrings__Default` environment variable.