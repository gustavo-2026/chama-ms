# Daraja API Integration Guide

This guide explains how the Safaricom Daraja API is integrated into the Chama platform and what you need to do to take it from the Sandbox to Production.

## How it Works (The Flow)

1. **Trigger Payment**: The frontend (or automated loan engine) calls `POST /mpesa/stk-push` with an amount and phone number.
2. **Access Token**: The backend uses your `Consumer Key` and `Consumer Secret` to generate a temporary OAuth access token from Daraja.
3. **Password Generation**: The backend generates a temporary password using your `Shortcode`, `Passkey`, and a `Timestamp`.
4. **Push to Phone**: The backend sends the STK Push request to Safaricom. Safaricom sends an M-Pesa PIN prompt to the user's phone.
5. **Pending State**: The backend records the `CheckoutRequestID` in the `transactions` table with a status of `PENDING`.
6. **The Callback**: Once the user enters their PIN (or cancels), Safaricom sends a JSON payload to your `CallBackURL`.
7. **Reconciliation**: The `POST /mpesa/callback` endpoint receives the payload, extracts the status code. If successful (Code `0`), it updates the database with the `MpesaReceiptNumber` (e.g., `QAB12345`) and changes the status to `SUCCESS`.

## 1. Sandbox Setup (Testing)

To test this on your local machine, you need a public URL for Safaricom to send the callback to.

### Step 1: Get Daraja Sandbox Credentials
1. Go to the [Safaricom Daraja Portal](https://developer.safaricom.co.ke/).
2. Create an account and create a new App.
3. Note your **Consumer Key** and **Consumer Secret**.
4. Go to the "Simulate" tab -> "M-Pesa Express" (STK Push) to get the test **Shortcode** and **Passkey**.

### Step 2: Set up a Local Tunnel (ngrok)
Safaricom cannot reach `localhost:8003`. You need a tunnel like `ngrok` or `localtunnel`.
```bash
# Example using ngrok
ngrok http 8003
```
This will give you a URL like `https://a1b2c3d4.ngrok.app`.

### Step 3: Configure Environment Variables
Update the `.env` file in your `payments-service` directory:

```env
MPESA_ENV=sandbox
MPESA_SHORTCODE=174379 # Standard Sandbox Paybill
MPESA_CONSUMER_KEY=your_sandbox_consumer_key
MPESA_CONSUMER_SECRET=your_sandbox_consumer_secret
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919 # Standard Sandbox Passkey
MPESA_CALLBACK_URL=https://your-ngrok-url.app/mpesa/callback
```

### Step 4: Test it out
Restart the `payments-service`. Go to the Admin Dashboard and click **Simulate STK Push**. The push will be sent to the test phone number, and the callback will hit your local server via ngrok and appear in the "Ledger of Truth".

---

## 2. Going Live (Production)

To go live, you need a registered Paybill/Till number with Safaricom and complete the Go-Live process.

1. Create a "Production" App on the Daraja portal.
2. Upload the required business documents (CR12, Directors IDs, etc.) to get your Live Credentials.
3. Once approved, update your `.env` file on your production server:

```env
MPESA_ENV=production
MPESA_SHORTCODE=your_real_paybill_number
MPESA_CONSUMER_KEY=your_production_key
MPESA_CONSUMER_SECRET=your_production_secret
MPESA_PASSKEY=your_production_passkey_from_email
MPESA_CALLBACK_URL=https://api.yourdomain.com/payments/mpesa/callback
```

You are now ready to collect real funds!
