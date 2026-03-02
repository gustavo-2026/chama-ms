# Chama Microservices Architecture

## Overview

This is a **microservices version** of the Chama platform. See the main `chama` directory for the monolith version.

## Services

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Nginx load balancer |
| Core | 8001 | Members, Contributions, Loans |
| Marketplace | 8002 | Listings, Orders, Reviews |
| Payments | 8003 | M-Pesa, Pesapal, Wallet |
| Notifications | 8004 | Push, SMS, Email |
| Messaging | 8005 | Real-time WebSocket chat |

## Quick Start

```bash
cd docker
docker-compose up
```

## Architecture

```
                    ┌──────────────┐
                    │ API Gateway  │
                    │   (Nginx)    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│     Core      │ │  Marketplace  │ │   Payments    │
│   Service     │ │   Service     │ │   Service     │
└───────────────┘ └───────────────┘ └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  PostgreSQL    │ │    Redis      │ │  Notification │
│   (Shared)    │ │  (Pub/Sub)    │ │    Service    │
└───────────────┘ └───────────────┘ └───────────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │   Messaging    │
                    │   (WebSocket) │
                    └───────────────┘
```

## Key Features

- **Real-time Messaging**: WebSocket-based chat
- **Event-Driven**: Services communicate via events (RabbitMQ/Kafka ready)
- **Independent Scaling**: Each service scales separately
- **Technology**: FastAPI, PostgreSQL, Redis, Nginx

## Environment

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/chama
REDIS_URL=redis://redis:6379
```

## Development

```bash
# Run individual service
cd services/messaging-service
python main.py
```
