FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy all necessary project files first
COPY ["src/shared/dotnet/Vetterati.Shared.csproj", "src/shared/dotnet/"]
COPY ["src/services/ahp-service/AhpService.csproj", "src/services/ahp-service/"]

# Restore dependencies
RUN dotnet restore "src/services/ahp-service/AhpService.csproj"

# Copy all source code
COPY src/shared/dotnet/ src/shared/dotnet/
COPY src/services/ahp-service/ src/services/ahp-service/

# Build the application
WORKDIR "/src/src/services/ahp-service"
RUN dotnet build "AhpService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AhpService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AhpService.dll"]
