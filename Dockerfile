# Étape de build
FROM maven:3.8.5-openjdk-17 AS builder

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY pom.xml .
COPY src ./src

# Build de l'application
RUN mvn clean package -DskipTests

# Étape d'exécution
FROM openjdk:17-jdk-slim

# Installer curl pour les health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r spring && useradd -r -g spring spring

# Définir le répertoire de travail
WORKDIR /app

# Copier le JAR depuis l'étape de build
COPY --from=builder /app/target/*.jar app.jar

# Changer les propriétaires des fichiers
RUN chown -R spring:spring /app

# Passer à l'utilisateur non-root
USER spring

# Exposer le port
EXPOSE 8080

# Variables d'environnement
ENV SPRING_PROFILES_ACTIVE=prod
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Point d'entrée
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]