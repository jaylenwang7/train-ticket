FROM openjdk:8-jre

# Set up timezone
WORKDIR /app
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

# Download and add OpenTelemetry Java agent
RUN mkdir -p /otel-agent && \
    curl -L https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar -o /otel-agent/opentelemetry-javaagent.jar

# Copy application jar
COPY ./target/*.jar app.jar

# Expose port
EXPOSE 8080

# Set default environment variables for OpenTelemetry
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=ts-admin-user-service"
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://opentelemetry-collector-deployment:4317"
ENV OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
ENV OTEL_METRICS_EXPORTER="otlp"
ENV OTEL_TRACES_EXPORTER="otlp"
ENV OTEL_LOGS_EXPORTER="otlp"

# Run with OpenTelemetry agent
CMD ["java", "-javaagent:/otel-agent/opentelemetry-javaagent.jar", "-Dotel.instrumentation.common.experimental.controller-telemetry.enabled=true", "-Xmx200m", "-jar", "app.jar"]

