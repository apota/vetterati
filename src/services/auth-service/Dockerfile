FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy all necessary project files first
COPY ["src/shared/dotnet/Vetterati.Shared.csproj", "src/shared/dotnet/"]
COPY ["src/services/auth-service/AuthService.csproj", "src/services/auth-service/"]

# Restore dependencies
RUN dotnet restore "src/services/auth-service/AuthService.csproj" --verbosity normal

# Copy all source code
COPY src/shared/dotnet/ src/shared/dotnet/
COPY src/services/auth-service/ src/services/auth-service/

# Build the application
WORKDIR "/src/src/services/auth-service"
RUN dotnet build "AuthService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AuthService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Note: Running as non-root user (app user is default in aspnet image)

ENTRYPOINT ["dotnet", "AuthService.dll"]
