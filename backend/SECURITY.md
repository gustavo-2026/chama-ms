# Security Configuration Guide

## Current Security Measures

### 1. Authentication
- ✅ JWT tokens (HS256)
- ✅ Access + Refresh token flow
- ✅ Token expiry (24h access, 30 days refresh)
- ✅ Password hashing (bcrypt)

### 2. Authorization
- ✅ Role-based access control (RBAC)
- ✅ Dependency injection for auth checks
- ✅ Chair/Treasurer permission checks

### 3. Rate Limiting
- ✅ 100 requests per minute per IP
- ✅ Configurable limits
- ✅ Exempts health checks

### 4. Input Validation
- ✅ Pydantic schemas for all inputs
- ✅ Type checking
- ✅ SQL injection prevention (ORM)

### 5. Security Headers
- ✅ X-Content-Type-Options
- ✅ X-Frame-Options (DENY)
- ✅ X-XSS-Protection
- ✅ Strict-Transport-Security
- ✅ Referrer-Policy
- ✅ Permissions-Policy

### 6. Request Limits
- ✅ Max request body size: 1MB
- ✅ File upload: 5MB limit
- ✅ Allowed file types

### 7. Audit Logging
- ✅ All CRUD operations tracked
- ✅ IP address logging
- ✅ Phone masking for privacy

### 8. Data Encryption
- ✅ Sensitive data encryption utilities
- ✅ Phone/email masking functions

## Recommended Production Settings

### CORS (main.py)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting
```python
# Increase for production if needed
app.add_middleware(RateLimitMiddleware, calls=1000, period=60)
```

### Environment Variables Required
```
DATABASE_URL=postgresql://...
SECRET_KEY=<32-char-random-string>
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
```

### Security Checklist Before Production
- [ ] Change SECRET_KEY to random 32+ character string
- [ ] Configure CORS to specific origins
- [ ] Set up SSL/HTTPS
- [ ] Configure database connection pooling
- [ ] Set up log monitoring
- [ ] Configure backup strategy
- [ ] Test rate limiting
- [ ] Verify audit logs working

## Known Limitations (v1)
- OTP stored in-memory (use Redis for production)
- Webhook secrets stored in-memory (use database)
- File uploads local (use S3 for production)
- No 2FA yet

## Future Security Enhancements
- Two-factor authentication (2FA)
- Biometric login
- Session management (force logout)
- API keys for service-to-service
- DDOS protection (Cloudflare)
- WAF (Web Application Firewall)
