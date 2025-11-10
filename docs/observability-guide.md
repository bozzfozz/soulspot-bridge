# Observability & Monitoring Guide

This guide explains how to use the observability and monitoring features in SoulSpot Bridge.

## Table of Contents

- [Overview](#overview)
- [Structured Logging](#structured-logging)
- [Metrics](#metrics)
- [Distributed Tracing](#distributed-tracing)
- [Health Checks](#health-checks)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

## Overview

SoulSpot Bridge includes comprehensive observability features to help you monitor, debug, and optimize your application:

- **Structured Logging**: JSON-formatted logs with correlation IDs for request tracking
- **Prometheus Metrics**: HTTP, business, and system metrics for performance monitoring
- **OpenTelemetry Tracing**: Distributed tracing for understanding request flows
- **Health Checks**: Liveness and readiness probes with dependency monitoring
- **Circuit Breakers**: Automatic protection against cascading failures

## Structured Logging

### Features

- **Correlation IDs**: Automatic request tracking across logs
- **JSON Format**: Machine-readable logs for production (optional)
- **Contextual Information**: Automatic inclusion of metadata (timestamp, level, module)
- **Request/Response Logging**: Automatic logging of all HTTP requests

### Configuration

Configure logging in your `.env` file:

```env
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable JSON format for production
OBSERVABILITY__LOG_JSON_FORMAT=true
```

### Correlation IDs

Every request gets a unique correlation ID that's included in all logs. The ID is:
- Generated automatically if not provided
- Can be provided via `X-Correlation-ID` header
- Returned in the response `X-Correlation-ID` header
- Included in all logs during request processing

Example log output (text format):
```
2025-11-10 14:00:00 - INFO - soulspot.api.routers.tracks - [abc-123-def] - Fetching track details
```

Example log output (JSON format):
```json
{
  "timestamp": "2025-11-10 14:00:00",
  "level": "INFO",
  "logger": "soulspot.api.routers.tracks",
  "correlation_id": "abc-123-def",
  "message": "Fetching track details"
}
```

### Usage in Code

```python
import logging
from soulspot.infrastructure.observability.logging import get_correlation_id

logger = logging.getLogger(__name__)

# Logs automatically include correlation ID
logger.info("Processing request", extra={"user_id": 123})

# Get current correlation ID
correlation_id = get_correlation_id()
```

## Metrics

### Available Metrics

#### HTTP Metrics
- `http_requests_total`: Total number of HTTP requests by method, endpoint, and status
- `http_request_duration_seconds`: Request duration histogram
- `http_requests_in_progress`: Current number of in-flight requests

#### Business Metrics
- `downloads_started_total`: Downloads initiated
- `downloads_completed_total`: Downloads completed by status
- `downloads_failed_total`: Failed downloads by reason
- `downloads_in_progress`: Current active downloads
- `playlist_imports_total`: Playlist imports by source
- `external_api_calls_total`: External API calls by service

#### Database Metrics
- `database_connections_active`: Active database connections
- `database_query_duration_seconds`: Query duration histogram
- `database_errors_total`: Database errors by type

#### Job Queue Metrics
- `job_queue_length`: Jobs in queue
- `jobs_processed_total`: Jobs processed by status
- `job_processing_duration_seconds`: Job processing duration

### Accessing Metrics

Metrics are exposed at the `/metrics` endpoint in Prometheus text format:

```bash
curl http://localhost:8000/metrics
```

### Configuration

Enable/disable metrics collection:

```env
# Enable metrics collection (default: true)
OBSERVABILITY__ENABLE_METRICS=true
```

### Prometheus Integration

Add this scrape config to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'soulspot-bridge'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Recording Custom Metrics

```python
from soulspot.infrastructure.observability.metrics import (
    downloads_started_total,
    download_duration_seconds,
)

# Increment counter
downloads_started_total.labels(source="slskd").inc()

# Record timing
with download_duration_seconds.labels(source="slskd").time():
    # Your download logic
    pass
```

## Distributed Tracing

### Features

- OpenTelemetry-based distributed tracing
- Automatic FastAPI instrumentation
- Automatic HTTPX client instrumentation
- OTLP export support
- Console export for debugging

### Configuration

```env
# Enable tracing (default: false)
OBSERVABILITY__ENABLE_TRACING=true

# OTLP endpoint for trace export (e.g., Jaeger, Tempo)
OBSERVABILITY__OTLP_ENDPOINT=http://localhost:4317

# Enable console trace export for debugging (default: false)
OBSERVABILITY__ENABLE_CONSOLE_TRACE_EXPORTER=true
```

### Jaeger Setup

Run Jaeger all-in-one for development:

```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Access Jaeger UI at http://localhost:16686

### Custom Spans

```python
from soulspot.infrastructure.observability.tracing import get_tracer

tracer = get_tracer(__name__)

with tracer.start_as_current_span("process_download") as span:
    span.set_attribute("download.id", download_id)
    span.set_attribute("download.source", "slskd")
    # Your logic here
```

## Health Checks

### Endpoints

#### Liveness Probe (`/live`)
Checks if the application is running:

```bash
curl http://localhost:8000/live
# {"status": "alive"}
```

#### Readiness Probe (`/ready`)
Checks if the application is ready to serve traffic:

```bash
curl http://localhost:8000/ready
```

Response:
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "slskd": {
      "status": "healthy",
      "message": "slskd service is accessible"
    },
    "spotify": {
      "status": "healthy",
      "message": "Spotify API is accessible"
    },
    "musicbrainz": {
      "status": "healthy",
      "message": "MusicBrainz API is accessible"
    }
  }
}
```

Status values:
- `healthy`: All checks passed
- `degraded`: Some checks failed but service is operational
- `unhealthy`: Critical checks failed

### Configuration

```env
# Enable dependency health checks (default: true)
OBSERVABILITY__ENABLE_DEPENDENCY_HEALTH_CHECKS=true

# Health check timeout in seconds (default: 5.0)
OBSERVABILITY__HEALTH_CHECK_TIMEOUT=5.0
```

### Kubernetes Integration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: soulspot-bridge
spec:
  containers:
  - name: app
    image: soulspot-bridge:latest
    livenessProbe:
      httpGet:
        path: /live
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
```

## Circuit Breakers

Circuit breakers automatically protect against cascading failures when external services are unavailable.

### How It Works

1. **Closed State**: Normal operation, requests go through
2. **Open State**: After threshold failures, circuit opens and blocks requests
3. **Half-Open State**: After timeout, circuit allows test requests

### Configuration

Circuit breakers are automatically created for each external service with:
- **Failure Threshold**: 5 consecutive failures
- **Timeout**: 60 seconds before retry

### Monitoring

Circuit breaker status is included in health checks:

```json
{
  "status": "degraded",
  "checks": {
    "slskd": {
      "status": "degraded",
      "message": "Circuit breaker open, service temporarily unavailable"
    }
  }
}
```

## Configuration

### Complete Environment Variables

```env
# Application
APP_ENV=production
LOG_LEVEL=INFO

# Observability - Logging
OBSERVABILITY__LOG_JSON_FORMAT=true

# Observability - Metrics
OBSERVABILITY__ENABLE_METRICS=true

# Observability - Tracing
OBSERVABILITY__ENABLE_TRACING=true
OBSERVABILITY__OTLP_ENDPOINT=http://localhost:4317
OBSERVABILITY__ENABLE_CONSOLE_TRACE_EXPORTER=false

# Observability - Health Checks
OBSERVABILITY__ENABLE_DEPENDENCY_HEALTH_CHECKS=true
OBSERVABILITY__HEALTH_CHECK_TIMEOUT=5.0
```

## Best Practices

### Logging

1. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages for potential issues
   - ERROR: Error messages for failures
   - CRITICAL: Critical issues requiring immediate attention

2. **Include context**: Use `extra` parameter to add structured data:
   ```python
   logger.info("User action completed", extra={
       "user_id": user.id,
       "action": "download",
       "duration_ms": duration
   })
   ```

3. **Avoid logging sensitive data**: Never log passwords, tokens, or personal information

### Metrics

1. **Use labels wisely**: Keep cardinality low (avoid high-cardinality labels like user IDs)
2. **Normalize paths**: Use path templates instead of actual IDs (e.g., `/tracks/{id}` not `/tracks/123`)
3. **Monitor trends**: Track metrics over time to identify patterns

### Tracing

1. **Add meaningful attributes**: Include relevant context in spans
2. **Keep spans focused**: One span per logical operation
3. **Use sampling**: In production, sample traces to reduce overhead

### Health Checks

1. **Set appropriate timeouts**: Balance responsiveness with false positives
2. **Monitor health check latency**: Slow health checks indicate problems
3. **Use readiness for dependencies**: Liveness for application health only

---

For more information, see:
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
