# ChamaVault Technical Architecture

## Overview
White-label SaaS for chamas ( Kenyan savings groups) with:
- **Web App** (PWA)
- **Mobile App** (iOS + Android via Expo)
- **Fast API Backend** (Python FastAPI)

---

## Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **Backend** | FastAPI (Python 3.11) | Fast, async, great for financial calc, easy M-Pesa integration |
| **Database** | PostgreSQL (Supabase) | Multi-tenant, JSON support, built-in auth |
| **ORM** | SQLAlchemy 2.0 + Pydantic | Type safety, migrations |
| **Web Frontend** | Next.js 14 (App Router) | PWA ready, SSR, our existing expertise |
| **Mobile** | Expo (React Native) | Cross-platform, our existing expertise |
| **Auth** | Phone-based (custom) + JWT | M-Pesa phone = identity |
| **Payments** | M-Pesa Daraja API | STK Push, C2B, B2C |
| **SMS** | Africa's Talking | Notifications |
| **Hosting** | Railway / Render / Supabase | Easy scaling |

---

## Project Structure

```
chamavault/
├── backend/              # FastAPI
│   ├── app/
│   │   ├── api/        # Routes
│   │   ├── core/       # Config, security
│   │   ├── db/         # Database
│   │   ├── models/     # SQLAlchemy
│   │   ├── schemas/    # Pydantic
│   │   └── services/   # Business logic
│   ├── alembic/        # Migrations
│   └── requirements.txt
│
├── web/                 # Next.js
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
│
├── mobile/              # Expo
│   ├── app/
│   ├── src/
│   └── assets/
│
└── docs/
```

---

## API Design (FastAPI)

### Base URL
- Development: `http://localhost:8000`
- Production: `https://api.chamavault.com`

### Authentication
```
POST /api/v1/auth/login
POST /api/v1/auth/verify-phone
POST /api/v1/auth/refresh
```

### Members
```
GET    /api/v1/members
POST   /api/v1/members
GET    /api/v1/members/{id}
PATCH  /api/v1/members/{id}
DELETE /api/v1/members/{id}
```

### Contributions
```
GET    /api/v1/contributions
POST   /api/v1/contributions
GET    /api/v1/contributions/{id}
GET    /api/v1/contributions/summary
```

### Loans
```
GET    /api/v1/loans
POST   /api/v1/loans
GET    /api/v1/loans/{id}
PATCH  /api/v1/loans/{id}/approve
PATCH  /api/v1/loans/{id}/reject
POST   /api/v1/loans/{id}/repay
```

### M-Pesa
```
POST   /api/v1/mpesa/stk-push
POST   /api/v1/mpesa/callback/c2b
POST   /api/v1/mpesa/callback/b2c
POST   /api/v1/mpesa/b2c
GET    /api/v1/mpesa/transactions
```

### Treasury
```
GET    /api/v1/treasury/summary
GET    /api/v1/treasury/dividends
POST   /api/v1/treasury/disburse
```

### Voting
```
GET    /api/v1/proposals
POST   /api/v1/proposals
GET    /api/v1/proposals/{id}
POST   /api/v1/proposals/{id}/vote
```

### Organizations (White-label)
```
GET    /api/v1/organization
PATCH  /api/v1/organization
GET    /api/v1/organization/branding
PATCH  /api/v1/organization/branding
```

---

## Web App Features (PWA)

### Pages
- `/` — Landing page (public)
- `/login` — Phone + OTP
- `/dashboard` — Treasury overview
- `/members` — Member list
- `/contributions` — Contribution tracking
- `/loans` — Loan management
- `/proposals` — Voting/proposals
- `/reports` — Financial reports
- `/settings` — Organization settings

### PWA Capabilities
- Offline support
- Installable
- Push notifications
- Background sync

---

## Mobile App Features

### Screens (Expo)
- Splash + Onboarding
- Phone Login
- Home (dashboard)
- Contribute (STK Push)
- Members List
- My Loans
- Proposals / Voting
- Profile
- (Admin only) Organization Settings

---

## M-Pesa Integration Flow

### STK Push (Contribution)
```
1. Member enters amount
2. App → API: POST /contributions (pending)
3. API → M-Pesa: STK Push request
4. Member gets M-Pesa prompt → enters PIN
5. M-Pesa → API: Callback with receipt
6. API updates contribution → COMPLETED
7. App polls / checks status → shows success
```

### B2C (Dividend/Loan Disbursement)
```
1. Admin triggers payout
2. API queues recipients
3. For each: POST /b2c
4. M-Pesa processes
5. Callback updates transaction status
6. SMS notification sent
```

---

## Security

### Multi-tenant Isolation
- `organization_id` on ALL tables
- Row-level security (RLS) in PostgreSQL
- API validates org membership

### Financial Safeguards
- All money operations in transactions
- Audit log table
- Dual approval for payouts > threshold
- Phone number masking in logs

### API Security
- JWT tokens (15 min expiry)
- Refresh token rotation
- Rate limiting (100 req/min)
- HTTPS only in production

---

## Deployment

### Development
```
Backend:  uvicorn app.main:app --reload
Web:      npm run dev
Mobile:   npx expo start
```

### Production
```
Backend:  Docker → Railway/Render/Supabase Edge Functions
Web:      Vercel
Mobile:   EAS Build → App Store / Play Store
```

---

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Web
cd web
npm install
npm run dev

# Mobile
cd mobile
npx expo start
```

---

*Architecture v0.1*
