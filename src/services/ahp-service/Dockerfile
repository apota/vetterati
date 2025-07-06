FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy shared library first
COPY ["src/shared/dotnet/Vetterati.Shared.csproj", "shared/dotnet/"]
RUN dotnet restore "shared/dotnet/Vetterati.Shared.csproj"

# Copy project file and restore dependencies
COPY ["src/services/ahp-service/AhpService.csproj", "services/ahp-service/"]
RUN dotnet restore "services/ahp-service/AhpService.csproj"

# Copy source code
COPY src/shared/dotnet/ shared/dotnet/
COPY src/services/ahp-service/ services/ahp-service/

# Build the application
WORKDIR "/src/services/ahp-service"
RUN dotnet build "AhpService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AhpService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AhpService.dll"]
