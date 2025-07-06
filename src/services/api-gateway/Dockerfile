FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy shared project
COPY ["../../shared/dotnet/Vetterati.Shared.csproj", "shared/dotnet/"]

# Copy main project
COPY ["ApiGateway.csproj", "api-gateway/"]

# Restore dependencies
RUN dotnet restore "api-gateway/ApiGateway.csproj"

# Copy source code
COPY . api-gateway/
COPY ../../shared/dotnet/ shared/dotnet/

WORKDIR "/src/api-gateway"
RUN dotnet build "ApiGateway.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ApiGateway.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ApiGateway.dll"]
