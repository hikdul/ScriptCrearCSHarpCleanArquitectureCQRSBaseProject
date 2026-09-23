# Database — SQL Server

The API uses **SQL Server 2022** (Developer edition) for local development.

Deploying SQL Server locally requires a strong `MSSQL_SA_PASSWORD`, stored in
`docker/.env` (generated at project generation time and gitignored).

## Start the database

```bash
docker compose up -d
```

This starts `{{ProjectNameLower}}-sqlserver` on `localhost:1433`
(database `{{ProjectNameLower}}`, user `sa`).

To run this compose file directly from the `docker/` folder:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.sqlserver.yml up -d
```

## Connection string

```text
Server=localhost,1433;Database={{ProjectNameLower}};User Id=sa;Password=<see docker/.env>;TrustServerCertificate=True
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. Override it in any environment
with the `ConnectionStrings__Default` environment variable.

## Switching to PostgreSQL

The `docker/` folder also contains `docker-compose.postgres.yml` for
PostgreSQL 17. To switch providers, regenerate the project with:

```bash
python3 generate_project.py {{ProjectName}} --database postgres
```

and start the PostgreSQL container with the PostgreSQL instructions below.

---

# Database — PostgreSQL (alternative)

## Start the database

```bash
docker compose -f docker/docker-compose.postgres.yml up -d
```

This starts `{{ProjectNameLower}}-postgres` on `localhost:5432`
(database `{{ProjectNameLower}}`, user `postgres`, trust auth for local
development only).

## Connection string

```text
Host=localhost;Port=5432;Database={{ProjectNameLower}};Username=postgres
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. Override it in any environment
with the `ConnectionStrings__Default` environment variable.