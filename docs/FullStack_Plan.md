# Chama Full Stack Architecture

## Overview
White-label SaaS for chamas with web + mobile + FastAPI backend

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Web Frontend** | Next.js 15 (App Router) |
| **Mobile** | Expo (React Native) |
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL (Supabase) |
| **Payments** | M-Pesa Daraja API |
| **SMS** | Africa's Talking |

---

## Project Structure

```
chama/
├── web/                 # Next.js 15 (PWA)
│   ├── src/app/       # App Router pages
│   ├── src/components/
│   ├── src/lib/
│   └── public/
│
├── mobile/              # Expo (React Native)
│   ├── app/           # Expo Router screens
│   ├── src/
│   └── assets/
│
├── backend/             # FastAPI
│   ├── app/
│   │   ├── api/      # Routes
│   │   ├── core/     # Config
│   │   ├── db/       # Database
│   │   ├── models/   # SQLAlchemy
│   │   ├── schemas/  # Pydantic
│   │   └── services/ # Business logic
│   ├── alembic/
│   └── requirements.txt
│
└── docs/
    ├── PRD.md
    ├── Database_Schema.md
    └── M-Pesa_Integration.md
```

---

## API Endpoints (FastAPI)

### Auth
- `POST /api/v1/auth/login` — Phone + OTP
- `POST /api/v1/auth/verify-phone`
- `POST /api/v1/auth/refresh`

### Members
- `GET/POST /api/v1/members`
- `GET/PATCH/DELETE /api/v1/members/{id}`

### Contributions
- `GET/POST /api/v1/contributions`
- `GET /api/v1/contributions/summary`

### Loans
- `GET/POST /api/v1/loans`
- `PATCH /api/v1/loans/{id}/approve|reject`
- `POST /api/v1/loans/{id}/repay`

### M-Pesa
- `POST /api/v1/mpesa/stk-push`
- `POST /api/v1/mpesa/callback/c2b`
- `POST /api/v1/mpesa/callback/b2c`
- `POST /api/v1/mpesa/b2c`

### Treasury
- `GET /api/v1/treasury/summary`
- `POST /api/v1/treasury/disburse`

### Voting
- `GET/POST /api/v1/proposals`
- `POST /api/v1/proposals/{id}/vote`

---

## Database Schema

### Core Tables
- `organizations` — Multi-tenant (each chama)
- `members` — Phone-based identity
- `contributions` — Track payments
- `loans` — Loan lifecycle
- `transactions` — M-Pesa log
- `proposals` — Voting
- `notifications` — SMS/In-app

---

## MVP Features

### Phase 1
1. Phone auth
2. Member management
3. Contribution tracking (cash + M-Pesa)
4. Treasury dashboard
5. Basic reports

### Phase 2
1. Loan system (apply, approve, repay)
2. M-Pesa STK Push
3. Dividend distribution
4. Voting/Proposals

### Phase 3
1. White-label customization
2. SMS notifications
3. Advanced reports

---

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web
```bash
cd web
npm install
npm run dev
```

### Mobile
```bash
cd mobile
npx expo start
```

---

## M-Pesa Setup (Kenya)

1. Register on https://developer.safaricom.co.ke
2. Create app to get Consumer Key + Secret
3. Get Business Shortcode (Paybill)
4. Set up callback URLs
5. Test in sandbox first

---

## White-Label

Each organization gets:
- Custom subdomain: `{slug}.chama.app`
- Custom logo + colors
- Custom terms

---

*Full Stack Plan v0.1*
