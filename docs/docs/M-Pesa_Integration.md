# M-Pesa Integration Guide

## Daraja API Overview

M-Pesa provides two main APIs:
1. **C2B** (Customer to Business) — Members pay TO the chama
2. **B2C** (Business to Customer) — Chama pays TO members (dividends, withdrawals)

## Required Credentials

Get these from Safaricom Developer Portal:
- `Consumer Key`
- `Consumer Secret`
- `Business Shortcode` (Paybill number)
- `Passkey` (for STK Push)

## Transaction Types

| Type | Use Case | API |
|------|----------|-----|
| STK Push | Member contributes via phone prompt | `stk_push` |
| C2B Register | Register callback URL | `c2b_register` |
| C2B Sim Tool | Test C2B | `c2b_simulate` |
| B2C | Send to member (loans, dividends) | `b2c_payment` |
| Balance | Check account balance | `account_balance` |
| Transaction Status | Check if payment succeeded | `transaction_status` |

## Flow: Member Contribution

1. Member opens app → taps "Contribute"
2. Enters amount → confirms
3. App calls STK Push API
4. Member gets M-Pesa prompt on phone
5. Member enters PIN
6. Safaricom calls our callback with result
7. App updates contribution record

## Flow: Dividend Disbursement

1. Chair triggers dividend payout
2. System calculates amounts per member
3. For each member with M-Pesa linked:
   - Call B2C API
   - Send funds to phone number
4. Record transaction status
5. Notify member via SMS

## Webhook/Callback Setup

Register callback URL:
```
POST /api/mpesa/c2b/register
Body: {
  "ShortCode": "600000",
  "ResponseType": "Completed",
  "ConfirmationURL": "https://yourdomain.com/api/mpesa/c2b/confirmation",
  "ValidationURL": "https://yourdomain.com/api/mpesa/c2b/validation"
}
```

## Security

- All M-Pesa callbacks must be verified with signature
- Store credentials in environment variables (never in code)
- Use HTTPS only
- Implement idempotency (don't process same transaction twice)

## Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Insufficient Funds |
| 2 | Less than minimum |
| 17 | Exceeded daily limit |
| 2001 | Invalid PIN |
| 2019 | Duplicate transaction |

## Testing

Use M-Pesa Sandbox:
- https://developer.safaricom.co.ke/

Test credentials provided in sandbox portal.
