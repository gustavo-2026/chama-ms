# Chama API Contracts

## Overview

**Base URL:** `http://localhost:8000`  
**Version:** 1.0.0  
**OpenAPI:** 3.1.0

---

## Authentication

All protected endpoints require Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Register User

**Endpoint:** `POST /auth/register-password`

**Request Body:**
```json
{
  "phone": "254712345678",
  "name": "John Doe",
  "password": "password123",
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### Login User

**Endpoint:** `POST /auth/login-password`

**Request Body:**
```json
{
  "username": "254712345678",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### Get Profile

**Endpoint:** `GET /profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "mem_123abc",
  "phone": "254712345678",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "MEMBER",
  "contribution_tier": "regular",
  "bio": null,
  "date_of_birth": null,
  "gender": null,
  "location": "Nairobi",
  "occupation": "Developer",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "254723456789",
  "profile_photo_url": null,
  "mpesa_linked": false,
  "created_at": "2026-03-01T10:00:00"
}
```

---

### Update Profile

**Endpoint:** `PATCH /profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "John Updated",
  "bio": "Software developer",
  "location": "Mombasa",
  "occupation": "Senior Developer",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "254723456789"
}
```

**Response (200):**
```json
{
  "id": "mem_123abc",
  "phone": "254712345678",
  "name": "John Updated",
  "email": "john@example.com",
  "role": "MEMBER",
  "contribution_tier": "regular",
  "bio": "Software developer",
  "location": "Mombasa",
  "occupation": "Senior Developer",
  ...
}
```

---

### Change Password

**Endpoint:** `POST /auth/change-password`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Password changed"
}
```

---

## Members

### List Members

**Endpoint:** `GET /members`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "id": "mem_123abc",
    "phone": "254712345678",
    "name": "John Doe",
    "role": "MEMBER",
    "contribution_tier": "regular",
    "mpesa_linked": false,
    "created_at": "2026-03-01T10:00:00"
  }
]
```

---

### Create Member

**Endpoint:** `POST /members`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "phone": "254712345679",
  "name": "Jane Smith",
  "role": "MEMBER",
  "contribution_tier": "gold",
  "mpesa_linked": true,
  "mpesa_phone": "254712345679"
}
```

**Response (201):**
```json
{
  "id": "mem_456def",
  "phone": "254712345679",
  "name": "Jane Smith",
  "role": "MEMBER",
  "contribution_tier": "gold",
  "mpesa_linked": true,
  "created_at": "2026-03-01T10:00:00"
}
```

---

### Get Member

**Endpoint:** `GET /members/{member_id}`

**Response (200):**
```json
{
  "id": "mem_456def",
  "phone": "254712345679",
  "name": "Jane Smith",
  "role": "MEMBER",
  "contribution_tier": "gold",
  ...
}
```

---

### Delete Member

**Endpoint:** `DELETE /members/{member_id}`

**Response (200):**
```json
{
  "message": "Member deleted"
}
```

---

## Contributions

### List Contributions

**Endpoint:** `GET /contributions`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `member_id` (optional): Filter by member
- `status` (optional): PENDING, COMPLETED, FAILED

**Response (200):**
```json
[
  {
    "id": "con_123",
    "member_id": "mem_123",
    "amount": "5000.00",
    "method": "MPESA",
    "status": "COMPLETED",
    "period_month": "03",
    "period_year": "2026",
    "note": "Monthly contribution",
    "created_at": "2026-03-01T10:00:00"
  }
]
```

---

### Create Contribution

**Endpoint:** `POST /contributions`

**Request Body:**
```json
{
  "member_id": "mem_123",
  "amount": "5000.00",
  "method": "MPESA",
  "status": "COMPLETED",
  "period_month": "03",
  "period_year": "2026",
  "note": "Monthly contribution"
}
```

**Response (201):**
```json
{
  "id": "con_456",
  "member_id": "mem_123",
  "amount": "5000.00",
  "method": "MPESA",
  "status": "COMPLETED",
  ...
}
```

---

### Contribution Summary

**Endpoint:** `GET /contributions/summary`

**Response (200):**
```json
{
  "total": 150000.00,
  "this_month": 50000.00,
  "member_count": 25,
  "average": 6000.00
}
```

---

## Loans

### List Loans

**Endpoint:** `GET /loans`

**Query Parameters:**
- `status` (optional): PENDING, APPROVED, REJECTED, ACTIVE, PAID

**Response (200):**
```json
[
  {
    "id": "lon_123",
    "member_id": "mem_123",
    "amount": "50000.00",
    "interest_rate": "10.00",
    "status": "ACTIVE",
    "purpose": "Business expansion",
    "created_at": "2026-03-01T10:00:00"
  }
]
```

---

### Apply for Loan

**Endpoint:** `POST /loans`

**Request Body:**
```json
{
  "member_id": "mem_123",
  "amount": "50000.00",
  "interest_rate": "10.00",
  "purpose": "Business expansion",
  "duration_months": 6
}
```

**Response (201):**
```json
{
  "id": "lon_456",
  "member_id": "mem_123",
  "amount": "50000.00",
  "interest_rate": "10.00",
  "status": "PENDING",
  "purpose": "Business expansion",
  "created_at": "2026-03-01T10:00:00"
}
```

---

### Approve Loan

**Endpoint:** `POST /loans/{loan_id}/approve`

**Response (200):**
```json
{
  "message": "Loan approved"
}
```

---

### Reject Loan

**Endpoint:** `POST /loans/{loan_id}/reject`

**Response (200):**
```json
{
  "message": "Loan rejected"
}
```

---

### Repay Loan

**Endpoint:** `POST /loans/{loan_id}/repay`

**Request Body:**
```json
{
  "amount": "10000.00",
  "method": "MPESA"
}
```

**Response (200):**
```json
{
  "message": "Repayment recorded",
  "remaining_balance": 45000.00
}
```

---

### Loan Calculator - Amortization

**Endpoint:** `GET /calculator/amortization`

**Query Parameters:**
- `principal`: Loan amount (required)
- `rate`: Annual interest rate (required)
- `months`: Duration in months (required)

**Response (200):**
```json
{
  "monthly_payment": 8765.00,
  "total_interest": 2590.00,
  "total_payment": 52590.00,
  "schedule": [
    {
      "month": 1,
      "payment": 8765.00,
      "principal": 7448.00,
      "interest": 1317.00,
      "balance": 45000.00
    }
  ]
}
```

---

## Treasury

### Treasury Summary

**Endpoint:** `GET /treasury/summary`

**Response (200):**
```json
{
  "total_contributions": 500000.00,
  "total_loans_disbursed": 200000.00,
  "totalstanding": 150000.00,
_loans_out  "available_funds": 350000.00,
  "member_count": 25,
  "active_loans": 10
}
```

---

## Proposals

### List Proposals

**Endpoint:** `GET /proposals`

**Response (200):**
```json
[
  {
    "id": "prp_123",
    "title": "Annual Trip",
    "description": "Plan for annual team building",
    "proposal_type": "EVENT",
    "status": "VOTING",
    "created_at": "2026-03-01T10:00:00"
  }
]
```

---

### Create Proposal

**Endpoint:** `POST /proposals`

**Request Body:**
```json
{
  "title": "Annual Trip",
  "description": "Plan for annual team building",
  "proposal_type": "EVENT",
  "voting_days": 7
}
```

**Response (201):**
```json
{
  "id": "prp_456",
  "title": "Annual Trip",
  "description": "Plan for annual team building",
  "proposal_type": "EVENT",
  "status": "DRAFT",
  ...
}
```

---

### Publish Proposal

**Endpoint:** `POST /proposals/{proposal_id}/publish`

**Response (200):**
```json
{
  "message": "Proposal published for voting"
}
```

---

### Vote on Proposal

**Endpoint:** `POST /proposals/{proposal_id}/vote`

**Request Body:**
```json
{
  "choice": "yes"
}
```

**Response (200):**
```json
{
  "message": "Vote recorded"
}
```

---

## Notifications

### List Notifications

**Endpoint:** `GET /notifications`

**Response (200):**
```json
[
  {
    "id": "notif_123",
    "type": "GENERAL",
    "title": "New Announcement",
    "message": "Meeting scheduled for next week",
    "is_read": false,
    "created_at": "2026-03-01T10:00:00"
  }
]
```

---

### Mark as Read

**Endpoint:** `POST /notifications/{notification_id}/read`

**Response (200):**
```json
{
  "message": "Notification marked as read"
}
```

---

## Analytics

### Overview

**Endpoint:** `GET /analytics/overview`

**Response (200):**
```json
{
  "total_members": 25,
  "participation_rate": 85.0,
  "total_contributions": 500000.00,
  "active_loans": 10,
  "total_outstanding": 150000.00,
  "available": 350000.00
}
```

---

### Member Activity

**Endpoint:** `GET /analytics/member-activity`

**Query Parameters:**
- `days`: Number of days (default: 30)

**Response (200):**
```json
{
  "contributions": [
    {"date": "2026-03-01", "count": 15, "total": 75000.00}
  ],
  "loans": [
    {"date": "2026-03-01", "count": 2, "total": 100000.00}
  ]
}
```

---

## Compliance

### Dashboard

**Endpoint:** `GET /compliance/dashboard`

**Response (200):**
```json
{
  "report_date": "2026-03-01T10:00:00",
  "member_compliance": {
    "total_registered_members": 25,
    "status": "compliant"
  },
  "financial_compliance": {
    "total_contributions": 500000.00,
    "status": "compliant"
  },
  "overall_status": "compliant"
}
```

---

### Member Registers

**Endpoint:** `GET /compliance/member-registers`

**Response (200):**
```json
{
  "organization_id": "org_123",
  "total_members": 25,
  "register": [
    {
      "member_id": "mem_123",
      "name": "John Doe",
      "phone": "254712345678",
      "role": "MEMBER",
      "total_contributed": 50000.00,
      "status": "active"
    }
  ]
}
```

---

## Search

### Global Search

**Endpoint:** `GET /search`

**Query Parameters:**
- `q`: Search query (required, min 2 chars)

**Response (200):**
```json
{
  "members": [
    {"id": "mem_123", "name": "John Doe", "phone": "254712345678"}
  ],
  "contributions": [],
  "loans": [],
  "proposals": []
}
```

---

## 2FA

### Enable 2FA

**Endpoint:** `POST /profile/2fa/enable`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_uri": "otpauth://totp/John%20Doe?secret=JBSWY3DPEHPK3PXP&issuer=Chama"
}
```

---

### Disable 2FA

**Endpoint:** `POST /profile/2fa/disable`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "code": "123456"
}
```

**Response (200):**
```json
{
  "message": "2FA disabled"
}
```

---

## Health

### Health Check

**Endpoint:** `GET /health`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-01T10:00:00",
  "version": "1.0.0"
}
```

---

### Readiness Check

**Endpoint:** `GET /health/ready`

**Response (200):**
```json
{
  "status": "ready",
  "database": "ready",
  "timestamp": "2026-03-01T10:00:00"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Data Types

### Enums

| Enum | Values |
|------|--------|
| MemberRole | MEMBER, TREASURER, CHAIR, AGENT |
| ContributionMethod | CASH, MPESA, BANK |
| TransactionStatus | PENDING, COMPLETED, FAILED, CANCELLED |
| LoanStatus | PENDING, APPROVED, REJECTED, ACTIVE, PAID |
| ProposalStatus | DRAFT, PUBLISHED, VOTING, PASSED, REJECTED |

---

*Generated: March 2026*
