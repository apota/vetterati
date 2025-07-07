FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy all necessary project files first
COPY ["src/shared/dotnet/Vetterati.Shared.csproj", "src/shared/dotnet/"]
COPY ["src/services/api-gateway/ApiGateway.csproj", "src/services/api-gateway/"]

# Restore dependencies
RUN dotnet restore "src/services/api-gateway/ApiGateway.csproj"

# Copy all source code
COPY src/shared/dotnet/ src/shared/dotnet/
COPY src/services/api-gateway/ src/services/api-gateway/

# Build the application
WORKDIR "/src/src/services/api-gateway"
RUN dotnet build "ApiGateway.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ApiGateway.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ApiGateway.dll"]
