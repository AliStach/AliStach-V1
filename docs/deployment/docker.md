# Docker Deployment Guide

## Overview

Deploy the AliExpress Affiliate API Service using Docker containers.

## Prerequisites

- Docker installed
- Docker Compose (optional)
- AliExpress API credentials

## Quick Start

### Build and Run

```bash
# Build image
docker build -t aliexpress-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ALIEXPRESS_APP_KEY=your_key \
  -e ALIEXPRESS_APP_SECRET=your_secret \
  --name aliexpress-api \
  aliexpress-api
```

## Docker Compose

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ALIEXPRESS_APP_KEY=${ALIEXPRESS_APP_KEY}
      - ALIEXPRESS_APP_SECRET=${ALIEXPRESS_APP_SECRET}
      - ALIEXPRESS_TRACKING_ID=${ALIEXPRESS_TRACKING_ID}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY api/ ./api/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "src.api.main"]
```

## Production Considerations

### Multi-stage Build
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "src.api.main"]
```

### Environment Variables
Create `.env` file:
```
ALIEXPRESS_APP_KEY=your_key
ALIEXPRESS_APP_SECRET=your_secret
ALIEXPRESS_TRACKING_ID=your_tracking_id
```

## Verification

```bash
curl http://localhost:8000/health
```

---

*Last Updated: December 4, 2025*
