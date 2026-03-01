# Chama Backend

FastAPI-based REST API for Community Treasury Management

## Quick Start

### Using Docker

```bash
# Clone and run
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## API Endpoints

### Core
| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | Request OTP |
| `POST /api/v1/auth/verify-phone` | Get JWT token |
| `POST /api/v1/organizations` | Create chama |
| `GET/PATCH/DELETE /api/v1/members` | Member CRUD |

### Financial
| Endpoint | Description |
|----------|-------------|
| `GET/POST /api/v1/contributions` | Contributions |
| `GET/POST /api/v1/loans` | Loans |
| `POST /api/v1/loans/{id}/approve` | Approve loan |
| `POST /api/v1/fines` | Manage fines |
| `GET/POST /api/v1/standing-orders` | Auto-contributions |

### M-Pesa
| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/mpesa/stk-push` | STK Push |
| `POST /api/v1/mpesa/b2c` | Send to member |
| `POST /api/v1/bulk-disbursement` | Batch payouts |

### Reports
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/treasury/summary` | Treasury dashboard |
| `GET /api/v1/reports/report/treasury` | PDF report |
| `GET /api/v1/export/contributions` | CSV export |

### Members
| Endpoint | Description |
|----------|-------------|
| `GET/POST /api/v1/next-of-kin` | Beneficiaries |
| `GET/POST /api/v1/attendance/meetings` | Meeting attendance |

### Settings
| Endpoint | Description |
|----------|-------------|
| `GET/POST /api/v1/notifications` | Notifications |
| `GET/POST /api/v1/webhooks` | External integrations |
| `POST /api/v1/calculator/loan-calculator` | Loan amortization |

## Docker

```bash
# Production
docker-compose up -d

# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Environment Variables

```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
```

## Security

- JWT authentication
- Role-based access
- Rate limiting (100/min)
- Security headers
- Audit logging
- Data encryption

## License

MIT
