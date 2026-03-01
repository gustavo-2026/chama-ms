# ZION CHARMA SaaS — Product Requirements Document

## 1. Product Overview

**Product Name:** ChamaVault (working title — can be rebranded)

**Type:** White-label B2B SaaS (Mobile-first web + PWA)

**Core Summary:** A treasury management platform for chamas (informal savings groups) that handles contributions, loans, dividends, and payments via M-Pesa — with custom branding for each organization.

**Target Market:** Kenya (primary), East Africa (Uganda, Tanzania, Rwanda)

---

## 2. Problem Statement

Chamas face:
- **Cash leakage** — physical money gets lost, misused, or delayed
- **Manual tracking** — Excel/paper books are error-prone
- **No M-Pesa integration** — need third-party apps to move money
- **No credit history** — can't access formal banking
- **Brand inconsistency** — no professional tools that reflect their identity

---

## 3. Target Users

| Persona | Role | Needs |
|---------|------|-------|
| **Chama Chair** | Governance | Voting, proposals, transparency |
| **Treasurer** | Finance | Track contributions, manage loans, generate reports |
| **Member** | Contributor | View balance, contribute, apply for loans |
| **Admin/Agent** | Operations | Onboard chamas, resolve disputes, manage M-Pesa |

---

## 4. White-Label Architecture

### Multi-Tenant Design
- Each chama gets: `customdomain.chamavault.com` or `chamavault.com/[slug]`
- Custom logo, colors, name per organization
- Isolated data per tenant (companyId)
- Tiered pricing: Free → Growth → Enterprise

### Branding Config (per tenant)
- Organization name, logo, primary/secondary colors
- Custom welcome message
- Terms & conditions (editable)
- Email/SMS sender identity (whitelabel)

---

## 5. Core Features (MVP)

### 5.1 Authentication & Onboarding
- Phone-number based signup (Kenyan numbers)
- M-Pesa phone number as unique identifier
- Role assignment: Chair, Treasurer, Member, Agent
- Invitation via SMS link

### 5.2 Member Management
- Add/remove members
- Member profiles: name, phone, contribution tier
- Attendance tracking
- Role management with permissions

### 5.3 Contribution Tracking
- Record contributions (cash, M-Pesa, bank)
- Contribution cycles (monthly, weekly, custom)
- Contribution tiers (minimums,目标)
- Real-time balance display
- Contribution reminders (SMS)

### 5.4 Loan & Credit System
- Loan applications with purpose
- Interest calculation (configurable per chama)
- Loan limits based on contribution history
- Repayment tracking
- Automatic reminders
- Loan approval workflow (single/committee)

### 5.5 M-Pesa Integration
- **STK Push** — Member contributions via M-Pesa
- **C2B** — Receive payments from members
- **B2C** — Disburse loans, dividends, withdrawals
- Transaction reconciliation
- M-Pesa statement import
- Failed transaction handling

### 5.6 Treasury Dashboard
- Total capital
- Available vs. locked (loans)
- Monthly income/expense
- Dividend calculation
- Share value tracking
- Financial reports export

### 5.7 Dividends & Distribution
- Configure dividend periods
- Calculate based on: contributions, attendance, loan interest paid
- Auto-disburse via M-Pesa B2C
- Dividend history

### 5.8 Governance & Voting
- Proposal creation
- Voting periods (24h, 48h, 7 days)
- Yes/No/Abstain voting
- Quorum enforcement
- Vote results history

### 5.9 Notifications
- SMS (via M-Pesa or gateway)
- In-app notifications
- Reminders: contributions due, loan repayment, meetings

### 5.10 Reports & Exports
- Monthly statements
- Annual financial reports
- Member contribution history
- Loan portfolio
- Export to PDF/Excel

---

## 6. Technical Architecture

### Stack Recommendation
- **Backend:** FastAPI (Python 3.11) — fast, async, great for financial calculations
- **Frontend Web:** Next.js 14 (PWA)
- **Mobile:** Expo (React Native)
- **Database:** PostgreSQL (Supabase)
- **Auth:** Phone-based (custom) + JWT
- **Payments:** M-Pesa Daraja API
- **SMS:** Africa's Talking

### Database Schema (Core)
- Organizations (tenants)
- Members
- Contributions
- Loans
- LoanRepayments
- Transactions (M-Pesa log)
- Votes
- Proposals
- Notifications

### Security
- Role-based access control (RBAC)
- Phone number masking in UI
- Audit logs for treasury actions
- Two-factor for treasurers/admins (optional)

---

## 7. Non-MVP (v2+)

- **Offline mode** — sync when back online
- **Meeting minutes** — voice-to-text
- **Investment portal** — group investments
- **Insurance integration** — micro-insurance
- **Accounting integration** — QuickBooks, Xero
- **API for third-parties** — ERP, banking
- **Multi-chama federation** — networks of chamas

---

## 8. Pricing Tiers (White-label)

| Feature | Free | Growth (KES 3k/mo) | Enterprise (Custom) |
|---------|------|---------------------|---------------------|
| Members | Up to 10 | Unlimited | Unlimited |
| M-Pesa transactions | 50/mo | Unlimited | Unlimited |
| Custom branding | ❌ | ✅ | ✅ |
| SMS notifications | ❌ | ✅ | ✅ |
| Reports | Basic | Full | Custom |
| Support | Community | Email | Dedicated |

---

## 9. Success Metrics

- Chamas onboarded
- Transaction volume (KES)
- Member retention (monthly active)
- M-Pesa success rate
- Time to reconcile (target: <5 min)

---

## 10. Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| M-Pesa API failures | Queue + retry mechanism, fallback to manual |
| Data privacy | Tenant isolation, encryption at rest |
| Fraud | Audit logs, dual-approval for payouts |
| Adoption | Onboarding support, training videos |
| Competition | First-mover in white-label chama space |

---

## 11. Roadmap

### Phase 1 — MVP (6-8 weeks)
- Auth + member management
- Contributions (manual + M-Pesa)
- Basic treasury dashboard
- Basic reports

### Phase 2 — Loans + Governance (4-6 weeks)
- Full loan lifecycle
- Voting system
- Dividend distribution

### Phase 3 — Scale (4-6 weeks)
- White-label onboarding flow
- Multi-org admin panel
- Advanced reports

---

## 12. Open Questions

- [ ] Preferred domain? (chamavault.co.ke? something else?)
- [ ] Brand name: "ChamaVault" or other?
- [ ] M-Pesa credentials (will need Daraja API keys)
- [ ] Initial target: how many pilot chamas?
- [ ] Budget for SMS/notification credits?

---

*Draft v0.1 | Ready for review*
