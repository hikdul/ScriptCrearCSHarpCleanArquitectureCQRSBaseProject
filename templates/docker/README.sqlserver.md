# Development Environment — SQL Server

The project ships with a full Docker setup: **SQL Server 2022** (Developer
edition), a multi-stage production image of the API, and a hot-reload
development container.

Deploying SQL Server locally requires a strong `MSSQL_SA_PASSWORD`, stored in
`docker/.env` (generated at project generation time and gitignored).

## Start everything (database + API)

```bash
docker compose --env-file docker/.env up -d --build
```

Services:

| Service | URL | Description |
| --- | --- | --- |
| `{{ProjectNameLower}}-sqlserver` | `localhost:1433` | SQL Server 2022 Developer (database `{{ProjectNameLower}}`, user `sa`) |
| `{{ProjectNameLower}}-api` | `http://localhost:8080` | Published API (multi-stage `Dockerfile` at project root) |
| `{{ProjectNameLower}}-api-dev` | `http://localhost:8081` | `dotnet watch` API: `./src` mounted into the container, restarts on change |

Only the database:

```bash
docker compose --env-file docker/.env up -d {{ProjectNameLower}}-sqlserver
```

To run a compose file directly from the `docker/` folder:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.sqlserver.yml up -d --build
```

## Dockerfiles

- `Dockerfile` — multi-stage build: SDK 10 restores/publishes, then the
  ASP.NET 10 runtime image runs the published `{{ProjectName}}.Api` (non-root
  `$APP_UID`).
- `Dockerfile.dev` — SDK image running `dotnet watch` against
  `src/{{ProjectName}}.Api`, with `bin`/`obj` and the NuGet cache on named
  volumes so host filesystem writes stay out of the container.

Both files sit at the project root so the compose `build:` context resolves.

## Connection string

```text
Server=localhost,1433;Database={{ProjectNameLower}};User Id=sa;Password=<see docker/.env>;TrustServerCertificate=True
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. In containers it is injected as
the `ConnectionStrings__Default` environment variable pointing at the
`{{ProjectNameLower}}-sqlserver` service.

## Switching to PostgreSQL

The `docker/` folder also contains `docker-compose.postgres.yml` for
PostgreSQL 17. To switch providers, regenerate the project with:

```bash
python3 generate_project.py {{ProjectName}} --database postgres
```

and start the PostgreSQL containers with the PostgreSQL instructions below.

---

# Development Environment — PostgreSQL (alternative)

## Start everything (database + API)

```bash
docker compose -f docker/docker-compose.postgres.yml up -d --build
```

Services:

| Service | URL | Description |
| --- | --- | --- |
| `{{ProjectNameLower}}-postgres` | `localhost:5432` | PostgreSQL 17 (database `{{ProjectNameLower}}`, user `postgres`, trust auth — local development only) |
| `{{ProjectNameLower}}-api` | `http://localhost:8080` | Published API (multi-stage `Dockerfile` at project root) |
| `{{ProjectNameLower}}-api-dev` | `http://localhost:8081` | `dotnet watch` API: `./src` mounted into the container, restarts on change |

Only the database:

```bash
docker compose -f docker/docker-compose.postgres.yml up -d {{ProjectNameLower}}-postgres
```

## Connection string

```text
Host=localhost;Port=5432;Database={{ProjectNameLower}};Username=postgres
```

The API reads it from `ConnectionStrings:Default` in
`src/{{ProjectName}}.Api/appsettings.json`. In containers it is injected as
the `ConnectionStrings__Default` environment variable pointing at the
`{{ProjectNameLower}}-postgres` service.