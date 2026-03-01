# Chama - Kenyan Savings Group Management Platform

## Comprehensive Technical Documentation

**Version:** 1.0.0  
**Last Updated:** March 2026  
**Repository:** https://github.com/gustavo-2026/chama

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [API Endpoints](#api-endpoints)
4. [Database Models](#database-models)
5. [Authentication & Security](#authentication--security)
6. [Features](#features)
7. [Integration](#integration)
8. [Getting Started](#getting-started)

---

## Overview

Chama is a comprehensive platform for managing Kenyan Savings Groups (Chamas). It provides a complete solution for group savings, loans, investments, and financial management with built-in compliance and reporting features.

### Core Capabilities
- Multi-member chama management
- Contribution tracking (M-Pesa, Cash, Bank)
- Loan management with guarantor support
- Treasury dashboard and financial reports
- Inter-chama lending (federations)
- Push, Email, and SMS notifications
- Compliance and audit trails

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 15 / SQLite (dev) |
| **Cache/Sessions** | Redis 7 |
| **Authentication** | JWT + OTP + 2FA |
| **SMS** | Africa's Talking |
| **Payments** | M-Pesa (Daraja API) |
| **Container** | Docker + Docker Compose |

---

## API Endpoints

### Total: 170+ Endpoints

#### Authentication & Profile (12 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register-password` | POST | Register with email/password |
| `/auth/login-password` | POST | Login with credentials |
| `/auth/change-password` | POST | Change password |
| `/auth/refresh` | POST | Refresh JWT token |
| `/auth/logout` | POST | Logout user |
| `/profile` | GET | Get current user profile |
| `/profile` | PATCH | Update profile |
| `/profile/photo` | POST | Upload profile photo |
| `/profile/login-history` | GET | View login history |
| `/profile/2fa/enable` | POST | Enable 2FA |
| `/profile/2fa/disable` | POST | Disable 2FA |
| `/profile/2fa/status` | GET | Check 2FA status |

#### Members Management (8 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/members` | GET | List all members |
| `/members` | POST | Add new member |
| `/members/{id}` | GET | Get member details |
| `/members/{id}` | PATCH | Update member |
| `/members/{id}` | DELETE | Remove member |
| `/import/members-csv` | POST | Bulk import from CSV |
| `/import/members-json` | POST | Bulk import from JSON |
| `/export/members` | GET | Export members |

#### Contributions (10 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/contributions` | GET | List contributions |
| `/contributions` | POST | Add contribution |
| `/contributions/{id}` | GET | Get contribution |
| `/contributions/summary` | GET | Contribution summary |
| `/contributions/by-member` | GET | By member |
| `/contributions/by-period` | GET | By time period |
| `/contributions/leaderboard` | GET | Top contributors |

#### Loans (15 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/loans` | GET | List loans |
| `/loans` | POST | Apply for loan |
| `/loans/{id}` | GET | Get loan details |
| `/loans/{id}/approve` | POST | Approve loan |
| `/loans/{id}/reject` | POST | Reject loan |
| `/loans/{id}/repay` | POST | Record repayment |
| `/loans/{id}/guarantors` | GET | List guarantors |
| `/loans/{id}/guarantors` | POST | Add guarantor |
| `/calculator/amortization` | GET | Loan amortization |
| `/calculator/eligibility` | GET | Check eligibility |

#### M-Pesa Integration (8 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mpesa/stk-push` | POST | STK Push payment |
| `/mpesa/b2c` | POST | B2C disbursement |
| `/mpesa/callback` | POST | M-Pesa webhook |
| `/mpesa/register-urls` | POST | Register callbacks |
| `/mpesa/transactions` | GET | Transaction history |

#### Treasury (6 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/treasury/summary` | GET | Treasury overview |
| `/treasury/cashflow` | GET | Cash flow report |
| `/treasury/outstanding-loans` | GET | Outstanding loans |

#### Proposals & Voting (8 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/proposals` | GET | List proposals |
| `/proposals` | POST | Create proposal |
| `/proposals/{id}` | GET | Get proposal |
| `/proposals/{id}/publish` | POST | Publish for voting |
| `/proposals/{id}/vote` | POST | Cast vote |
| `/proposals/{id}/results` | GET | Voting results |

#### Attendance (6 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/attendance/meetings` | GET | List meetings |
| `/attendance/meetings` | POST | Schedule meeting |
| `/attendance/checkin` | POST | Check in member |
| `/attendance/report` | GET | Attendance report |

#### Notifications (12 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/notifications` | GET | List notifications |
| `/notifications` | POST | Create notification |
| `/notifications/{id}/read` | POST | Mark as read |
| `/push/register` | POST | Register device token |
| `/push/send` | POST | Send push notification |
| `/email/send` | POST | Send email |
| `/sms/send` | POST | Send bulk SMS |
| `/scheduled-reports` | GET | List scheduled reports |
| `/scheduled-reports` | POST | Create scheduled report |

#### Reports (10 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reports/pdf` | GET | Generate PDF report |
| `/reports/tax` | GET | Tax report |
| `/reports/audit` | GET | Audit export |
| `/reports/annual` | GET | Annual statement |
| `/export/contributions` | GET | Export contributions |
| `/export/loans` | GET | Export loans |

#### Budget & Expenses (10 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/budget-categories` | GET | List categories |
| `/budget-categories` | POST | Create category |
| `/budgets` | GET | List budgets |
| `/budgets` | POST | Create budget |
| `/budgets/vs-actual` | GET | Budget vs Actual |
| `/expenses` | GET | List expenses |
| `/expenses` | POST | Submit expense |
| `/expenses/{id}/approve` | POST | Approve expense |
| `/expenses/{id}/reject` | POST | Reject expense |

#### Assets & Investments (12 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/assets` | GET | List assets |
| `/assets` | POST | Add asset |
| `/assets/{id}` | GET | Get asset |
| `/assets/{id}` | PATCH | Update asset |
| `/assets/summary` | GET | Asset summary |
| `/investments` | GET | List investments |
| `/investments` | POST | Add investment |
| `/investments/summary` | GET | Investment summary |
| `/investments/{id}/returns` | POST | Record return |
| `/investments/{id}/close` | POST | Close investment |

#### Federations & Inter-chama (12 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/federations` | GET | List federations |
| `/federations` | POST | Create federation |
| `/federations/{id}/join` | POST | Join federation |
| `/federations/{id}/members` | GET | Federation members |
| `/federations/{id}/treasury` | GET | Federation treasury |
| `/my-federations` | GET | My federations |
| `/inter-lending` | GET | List inter-chama loans |
| `/inter-lending` | POST | Request loan |
| `/inter-lending/{id}/approve` | POST | Approve loan |
| `/inter-lending/{id}/disburse` | POST | Disburse loan |
| `/inter-lending/{id}/repay` | POST | Repay loan |

#### Compliance & Audit (8 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/compliance/dashboard` | GET | Compliance dashboard |
| `/compliance/audit-trail` | GET | Audit trail |
| `/compliance/member-registers` | GET | Member register |
| `/compliance/financial-summary` | GET | Financial summary |
| `/audit-logs` | GET | Search audit logs |
| `/audit-logs/summary` | GET | Audit summary |
| `/audit-logs/export` | GET | Export audit logs |

#### Backup & Restore (4 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/backup` | GET | Create backup |
| `/backup/download` | GET | Download backup |
| `/restore` | POST | Restore from backup |
| `/restore/validate` | GET | Validate backup |

#### Analytics (6 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/overview` | GET | Dashboard overview |
| `/analytics/member-activity` | GET | Activity over time |
| `/analytics/retention` | GET | Retention metrics |
| `/analytics/top-contributors` | GET | Top contributors |
| `/analytics/financial-ratios` | GET | Financial ratios |

#### Search (1 endpoint)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET | Full-text search |

#### Security (10 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api-keys` | GET | List API keys |
| `/api-keys` | POST | Create API key |
| `/api-keys/{id}` | DELETE | Revoke key |
| `/api-keys/verify` | POST | Verify key |
| `/ip-whitelist` | GET | List IP whitelist |
| `/ip-whitelist` | POST | Add IP |
| `/ip-whitelist/{id}` | DELETE | Remove IP |
| `/2fa/status` | GET | 2FA status |
| `/2fa/enable` | POST | Enable 2FA |
| `/2fa/disable` | POST | Disable 2FA |

#### Templates & Organizations (6 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/templates` | GET | List templates |
| `/templates/{id}` | GET | Get template |
| `/templates` | POST | Create template |
| `/organizations` | GET | List organizations |
| `/organizations` | POST | Create organization |
| `/organizations/{id}` | GET | Get organization |

#### Other Endpoints (20+)

- Fines management (CRUD)
- Standing orders (auto-contributions)
- Next of kin (beneficiaries)
- Bulk disbursements
- Announcements
- Meeting notices
- Webhooks
- Uploads
- Health checks

---

## Database Models

### Core Models

| Model | Description |
|-------|-------------|
| `Organization` | Chama organization |
| `Member` | Member with profile |
| `Contribution` | Member contributions |
| `Loan` | Member loans |
| `LoanRepayment` | Loan repayments |
| `Proposal` | Group proposals |
| `Vote` | Proposal votes |

### Extended Models

| Model | Description |
|-------|-------------|
| `Meeting` | Scheduled meetings |
| `Attendance` | Meeting attendance |
| `Announcement` | Group announcements |
| `MeetingNotice` | Meeting reminders |
| `LoanGuarantor` | Loan guarantors |
| `BudgetCategory` | Budget categories |
| `Budget` | Monthly budgets |
| `Expense` | Expense claims |
| `Asset` | Group assets |
| `AssetValuation` | Asset valuations |
| `Investment` | Group investments |
| `InvestmentReturn` | Investment returns |
| `Federation` | Chama federation |
| `FederationMember` | Federation members |
| `InterChamaLoan` | Loans between chamas |
| `PushToken` | Device tokens |
| `ScheduledReport` | Auto-reports |
| `AuditLog` | Activity logs |
| `APIKey` | API keys |
| `IPWhitelist` | IP access control |
| `TwoFactorSetting` | 2FA settings |
| `LoginHistory` | Login tracking |
| `ChamaTemplate` | Organization templates |

---

## Authentication & Security

### Authentication Methods

1. **Password-based**
   - Registration with phone + password
   - Login with credentials
   - JWT access tokens (24h expiry)
   - Refresh tokens

2. **OTP-based (SMS)**
   - Phone login request
   - 6-digit OTP via SMS
   - Token generation on verify

3. **Two-Factor Authentication (2FA)**
   - TOTP (Time-based OTP)
   - QR code for authenticator apps
   - Backup codes support

### Security Features

| Feature | Implementation |
|---------|---------------|
| Password Hashing | bcrypt |
| Token Auth | JWT (HS256) |
| Rate Limiting | 100 requests/minute |
| Security Headers | X-Frame-Options, HSTS, etc. |
| API Keys | Service-to-service auth |
| IP Whitelisting | Per-organization |
| Audit Logging | All actions tracked |
| Data Encryption | Sensitive fields encrypted |

---

## Features

### Financial Management
- ✅ Contribution tracking (Cash, M-Pesa, Bank)
- ✅ Loan management with interest calculations
- ✅ Budget vs Actual tracking
- ✅ Expense management & approval
- ✅ Treasury dashboard

### Member Management
- ✅ Member registration & profiles
- ✅ Role-based access (Chair, Treasurer, Member, Agent)
- ✅ Contribution tiers (regular, silver, gold, platinum)
- ✅ Next of kin tracking
- ✅ Bulk import (CSV/JSON)

### Loans & Credit
- ✅ Loan applications & approvals
- ✅ Guarantor support
- ✅ Amortization calculator
- ✅ Loan eligibility checks
- ✅ Inter-chama lending

### Governance
- ✅ Proposal creation & voting
- ✅ Meeting scheduling & attendance
- ✅ Announcements & notices
- ✅ Minutes management

### Notifications
- ✅ Push notifications (Expo/FCM)
- ✅ Email notifications
- ✅ SMS (Africa's Talking)
- ✅ Scheduled reports

### Compliance
- ✅ Audit trails
- ✅ Tax reports
- ✅ Annual statements
- ✅ Member registers
- ✅ Data backup/restore

### Analytics
- ✅ Dashboard overview
- ✅ Member activity tracking
- ✅ Retention metrics
- ✅ Top contributors
- ✅ Financial ratios

### Platform Features
- ✅ Multi-chama federations
- ✅ White-label templates
- ✅ API key management
- ✅ IP whitelisting

---

## Integration

### M-Pesa (Daraja API)
- STK Push (Paybill)
- B2C (Disbursements)
- C2B (Receive payments)
- Transaction status queries

### Africa's Talking (SMS)
- OTP delivery
- Bulk SMS
- Delivery reports

### External Services
- Email (SendGrid, SES)
- Push (Expo, FCM)
- Cloud storage for files

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 15 or SQLite
- Redis 7 (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/gustavo-2026/chama.git
cd chama/backend

# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Docker Setup

```bash
cd chama/backend
docker-compose up -d
```

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | sqlite:///chama.db |
| `SECRET_KEY` | JWT signing key | (required) |
| `MPESA_ENV` | sandbox/production | sandbox |
| `MPESA_CONSUMER_KEY` | M-Pesa key | - |
| `MPESA_CONSUMER_SECRET` | M-Pesa secret | - |
| `AT_API_KEY` | Africa's Talking API key | - |
| `AT_USERNAME` | Africa's Talking username | - |
| `REDIS_URL` | Redis connection | localhost:6379 |

---

## License

MIT License

---

*Generated: March 2026*
