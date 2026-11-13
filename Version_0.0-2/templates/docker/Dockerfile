FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

COPY src/{{ProjectName}}.Domain/{{ProjectName}}.Domain.csproj src/{{ProjectName}}.Domain/
COPY src/{{ProjectName}}.Security/{{ProjectName}}.Security.csproj src/{{ProjectName}}.Security/
COPY src/{{ProjectName}}.Application/{{ProjectName}}.Application.csproj src/{{ProjectName}}.Application/
COPY src/{{ProjectName}}.Infrastructure/{{ProjectName}}.Infrastructure.csproj src/{{ProjectName}}.Infrastructure/
COPY src/{{ProjectName}}.Api/{{ProjectName}}.Api.csproj src/{{ProjectName}}.Api/

RUN dotnet restore src/{{ProjectName}}.Api/{{ProjectName}}.Api.csproj

COPY src/ src/

RUN dotnet publish src/{{ProjectName}}.Api/{{ProjectName}}.Api.csproj \
    -c Release \
    --no-restore \
    -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final

WORKDIR /app

COPY --from=build /app/publish .

USER $APP_UID

ENTRYPOINT ["dotnet", "{{ProjectName}}.Api.dll"]