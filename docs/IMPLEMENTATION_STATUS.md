# Flowtab.Pro Monetization - Implementation Status

**Last Updated:** January 21, 2026
**Status:** Phase 1 & 2 Complete - Ready for Frontend Development

---

## ✅ Completed Implementation

### 1. Database Models & Schema (100%)
- ✅ `Subscription` - User subscription state (Stripe-managed)
- ✅ `FlowCopy` - Append-only copy event log
- ✅ `CreatorPayout` - Monthly aggregated payouts
- ✅ User table extensions (stripe_customer_id, stripe_connect_id, is_creator)
- ✅ Prompt table extensions (is_premium, featured, total_copies)

**Location:** [apps/api/models.py](../apps/api/models.py)

### 2. CRUD Operations (100%)
- ✅ Subscription CRUD (create, read, update, cancel)
- ✅ Copy tracking (record, count, enforce duplicates)
- ✅ Payout calculations and retrieval
- ✅ Creator earnings aggregation

**Location:** [apps/api/crud.py](../apps/api/crud.py) (lines 458-680)

### 3. Schemas/DTOs (100%)
- ✅ SubscriptionCreate, SubscriptionRead, SubscriptionStatusResponse
- ✅ FlowCopyRequest, FlowCopyResponse, FlowCopyRead
- ✅ CreatorPayoutRead, CreatorEarningsResponse, CreatorAccountResponse
- ✅ UserReadWithBalance (extended user info)

**Location:** [apps/api/schemas.py](../apps/api/schemas.py) (lines 348-469)

### 4. Stripe Integration (100%)
- ✅ StripeClient with subscription management methods
- ✅ Webhook signature verification
- ✅ Subscription event handlers (created, updated, deleted)
- ✅ Stripe Connect account management for creators
- ✅ Payment intent and transfer creation

**Location:** [apps/api/stripe_utils.py](../apps/api/stripe_utils.py)

### 5. API Endpoints (100%)

#### Webhooks
- ✅ `POST /v1/webhooks/stripe` - Stripe event receiver

#### Subscriptions
- ✅ `GET /v1/subscriptions/me` - Get user's subscription status
- ✅ `POST /v1/subscriptions/checkout` - Create checkout session

#### Copy Tracking & Monetization
- ✅ `POST /v1/flows/{flow_id}/copy` - Record flow copy with limits enforced

#### Creator Features
- ✅ `GET /v1/creators/me/earnings` - View creator earnings and account balance
- ✅ `POST /v1/creators/me/connect` - Start Stripe Connect onboarding

**Location:** [apps/api/router.py](../apps/api/router.py) (lines 1540-1831)

### 6. Configuration (100%)
- ✅ Stripe settings in settings.py
- ✅ Environment variables in .env.example
- ✅ Frontend URL configuration for redirects

**Location:**
- [apps/api/settings.py](../apps/api/settings.py) (lines 34-41)
- [apps/api/.env.example](../apps/api/.env.example)

---

## 📊 System Architecture

### Copy Tracking & Revenue Model

```
User Subscribe ($10/month) → Stripe Creates Subscription
                              ↓
User Views Flow → Click "Copy" → POST /flows/{flow_id}/copy
                                  ↓
                        Check: Active Subscription?
                        Check: Already copied this month?
                        Check: Under 100 copies this month?
                                  ↓
                        Record Copy Event (flow_copies table)
                        Update Flow total_copies counter
                                  ↓
                        Return: copies_remaining, payout_earned
                        (payout_earned = 7 cents if under limit, 0 if over)
```

### Revenue Distribution

```
$10.00 Monthly Subscription per User
├─ Creator Pool: $7.00 maximum
│  └─ Distributed as: $0.07 per qualified copy (max 100 copies)
│
└─ Platform Fee: $3.00 (kept if user copies < 100 flows)
   └─ If user copies > 100: Platform keeps surplus
   └─ Example: 50 copies = $3.50 to creators + $6.50 to platform
```

### Payout System

```
Monthly (automated job):
1. Aggregate flow_copies by creator_id where counted_for_payout=True
2. Calculate: copy_count * 7 cents = amount
3. Create CreatorPayout record (status: pending)
4. Transfer funds via Stripe Connect (status: processing → paid)
5. Send notification to creator
```

---

## 🔌 API Endpoints Summary

### Authentication Required
All monetization endpoints require JWT authentication (existing `Authorization: Bearer {token}` header).

### Key Endpoints

#### 1. Subscription Status
```
GET /v1/subscriptions/me

Response:
{
  "is_subscriber": true,
  "subscription": {
    "id": "...",
    "status": "active",
    "current_period_start": "2026-01-01T00:00:00",
    "current_period_end": "2026-02-01T00:00:00",
    "...": "..."
  },
  "copies_remaining": 87
}
```

#### 2. Start Subscription
```
POST /v1/subscriptions/checkout

Response:
{
  "sessionId": "cs_live_..."  // For frontend Stripe checkout
}
```

#### 3. Record Copy (Main Action)
```
POST /v1/flows/{flow_id}/copy

Response:
{
  "id": "copy-uuid",
  "copied_at": "2026-01-15T10:30:00",
  "copies_this_month": 15,
  "copies_remaining": 85,
  "payout_earned": 7  // cents
}
```

#### 4. Creator Earnings
```
GET /v1/creators/me/earnings

Response:
{
  "user_id": "...",
  "is_creator": true,
  "account_balance_cents": 4207,  // $42.07
  "account_balance_dollars": 42.07,
  "total_earnings_cents": 8914,
  "total_earnings_dollars": 89.14,
  "monthly_earnings": [
    {
      "billing_month": "2026-01-01",
      "copy_count": 42,
      "amount_cents": 294,
      "amount_dollars": 2.94,
      "status": "paid"
    },
    ...
  ]
}
```

#### 5. Creator Onboarding
```
POST /v1/creators/me/connect

Response:
{
  "onboarding_url": "https://connect.stripe.com/onboarding/..."
}
```

---

## 🚀 What Works Now (Backend)

### ✅ Complete Flow

1. **User Registration** → Already works
2. **Start Subscription** → `POST /subscriptions/checkout` → Redirects to Stripe
3. **Stripe Webhook** → `POST /webhooks/stripe` → Creates subscription record
4. **View Prompts** → Already works
5. **Copy Flow** → `POST /flows/{flow_id}/copy` → Records with anti-gaming protections
6. **Check Earnings** → `GET /creators/me/earnings` → Shows balance
7. **Onboard Creator** → `POST /creators/me/connect` → Stripe Connect flow

### Anti-Gaming Protections

✅ **Unique Copy Constraint**
- User can only copy each Flow once per billing month
- Database enforces with UNIQUE(user_id, flow_id, billing_month) constraint

✅ **100-Copy Monthly Limit**
- First 100 copies earn $0.07 payout to creator
- Copies 101+ are free (no payout)
- Prevents revenue dilution

✅ **Subscription Verification**
- All copy operations require active subscription
- Stripe webhooks update subscription status in real-time

✅ **Creator Verification**
- Creators must complete Stripe Connect onboarding
- Only creators with verified accounts receive payouts

---

## ⏳ Not Yet Implemented (Frontend & Jobs)

### Frontend Components Needed

1. **Subscription UI**
   - "Upgrade to Premium" button
   - Stripe checkout modal/redirect
   - Subscription management (view status, cancel)
   - Copy counter display (X/100)

2. **Prompt Display**
   - Render prompts as non-copyable format (image-like or styled container)
   - Copy button that triggers `POST /flows/{flow_id}/copy`
   - Show copy result (remaining, payout info)

3. **Creator Dashboard**
   - Earnings graph/chart
   - Monthly breakdown table
   - Payout history
   - Creator onboarding link

4. **User Account**
   - Show subscription status
   - Manage subscription
   - Copies used this month

### Background Jobs Needed

1. **Monthly Payout Processing** (runs on 1st of month)
   - Query all flow_copies for previous month
   - Group by creator_id
   - Calculate payouts
   - Create CreatorPayout records (status: pending)
   - Transfer via Stripe Connect (status: processing)
   - Update status to paid
   - Send creator emails

2. **Subscription Renewal Check** (daily)
   - Check for subscriptions ending today
   - Send renewal reminders

3. **Failed Payout Retry** (daily)
   - Find payouts with status=failed
   - Retry transfers
   - Update status if successful

---

## 🔧 Configuration Checklist

Before going live, you need to:

### 1. Stripe Setup
- [ ] Create Stripe account (stripe.com)
- [ ] Create product "Premium Access"
- [ ] Create price "Premium Monthly" ($10/month recurring)
- [ ] Copy price ID to `STRIPE_PREMIUM_PRICE_ID`
- [ ] Get API keys: Secret Key and Publishable Key
- [ ] Set webhook endpoint to `https://your-api.com/v1/webhooks/stripe`
- [ ] Add webhook events: `customer.subscription.created`, `.updated`, `.deleted`
- [ ] Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

### 2. Environment Variables
```bash
# .env or Render environment
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PREMIUM_PRICE_ID=price_...
FRONTEND_URL=https://flowtab.pro
```

### 3. Database Migration
```bash
cd apps/api
alembic upgrade head
```

This creates:
- `subscriptions` table
- `flow_copies` table
- `creator_payouts` table
- Updates to `users` and `prompts` tables

---

## 📝 Database Schema Quick Reference

### subscriptions
```python
id: UUID
user_id: UUID (FK users)
stripe_subscription_id: str (unique)
stripe_customer_id: str
status: str  # active, canceled, past_due, unpaid
plan_id: str  # premium_monthly
current_period_start: datetime
current_period_end: datetime
cancel_at_period_end: bool
created_at: datetime
updated_at: datetime
```

### flow_copies (Append-only log)
```python
id: UUID
user_id: UUID (FK users)
flow_id: UUID (FK prompts)
creator_id: UUID (denormalized)
counted_for_payout: bool
copied_at: datetime
billing_month: datetime  # 2026-01-01 format
UNIQUE(user_id, flow_id, billing_month)
```

### creator_payouts
```python
id: UUID
creator_id: UUID (FK users)
billing_month: datetime
copy_count: int
amount_cents: int  # copy_count * 7
status: str  # pending, processing, paid, failed
stripe_transfer_id: str (nullable)
paid_at: datetime (nullable)
created_at: datetime
updated_at: datetime
UNIQUE(creator_id, billing_month)
```

---

## 🧪 Testing Endpoints Locally

### 1. Start Backend
```bash
cd apps/api
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Register & Login
```bash
# Register
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123"
  }'

# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePassword123"

# Store the access_token
TOKEN="eyJhbGc..."
```

### 3. Check Subscription Status
```bash
curl -X GET http://localhost:8000/v1/subscriptions/me \
  -H "Authorization: Bearer $TOKEN"
# Response: is_subscriber=false (since we're not subscribed yet)
```

### 4. Create Test Subscription (Stripe Test Mode)
Use Stripe test card: `4242 4242 4242 4242`

```bash
curl -X POST http://localhost:8000/v1/subscriptions/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
# Response: sessionId for Stripe checkout
```

### 5. Simulate Webhook (after subscription)
Stripe will send webhooks automatically. In test mode, you can use Stripe dashboard.

### 6. Record Copy
```bash
# First, get a flow ID from GET /v1/prompts
FLOW_ID="..."

curl -X POST http://localhost:8000/v1/flows/$FLOW_ID/copy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response: copy details, remaining copies, payout
```

### 7. Check Creator Earnings
```bash
curl -X GET http://localhost:8000/v1/creators/me/earnings \
  -H "Authorization: Bearer $TOKEN"
# Response: earnings summary
```

---

## 🐛 Troubleshooting

### Copy endpoint returns 403 "Premium subscription required"
- Ensure subscription is active in Stripe
- Check that Stripe webhook is being received
- Verify `subscription.status == "active"` in database

### Copy endpoint returns 409 "Already copied this flow"
- This is expected - users can only copy each flow once per month
- They can copy again in the next month

### Webhook not being triggered
- Check Stripe dashboard for webhook delivery logs
- Verify webhook signing secret is correct
- Ensure ngrok/tunnel is set up for local testing
- Use Stripe CLI: `stripe listen` and `stripe trigger`

---

## 📚 Files Modified/Created

### Created
- [stripe_utils.py](../stripe_utils.py) - Stripe integration utilities
- [docs/IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - This file

### Modified
- [models.py](../apps/api/models.py) - Added Subscription, FlowCopy, CreatorPayout
- [crud.py](../apps/api/crud.py) - Added monetization CRUD functions
- [schemas.py](../apps/api/schemas.py) - Added monetization schemas
- [router.py](../apps/api/router.py) - Added monetization endpoints
- [settings.py](../apps/api/settings.py) - Added Stripe configuration
- [.env.example](../apps/api/.env.example) - Added Stripe env variables

---

## 📈 Metrics to Track

Once implemented, monitor these KPIs:

1. **Subscriber Acquisition**: New subscriptions per day/week
2. **Copy Rate**: Average copies per subscriber per month
3. **Creator Activation**: % of creators who set up Stripe Connect
4. **Payout Distribution**: How revenue splits between creators/platform
5. **Churn Rate**: Subscription cancellations
6. **LTV**: Creator lifetime earnings

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Set up Stripe account and get API keys
2. ✅ Create price ID for $10/month subscription
3. ✅ Update .env with Stripe credentials
4. ✅ Run database migration: `alembic upgrade head`
5. ✅ Test webhook in Stripe dashboard

### Short Term (Next 2 Weeks)
1. Build frontend subscription UI
2. Create prompt copy UI with counter
3. Build creator dashboard
4. Set up Stripe test mode testing

### Medium Term (Next Month)
1. Implement monthly payout job
2. Add creator onboarding flow UI
3. Build creator earnings analytics
4. Set up monitoring and alerts

---

**Questions?** Refer to the main [MONETIZATION.md](../MONETIZATION.md) for business logic details.
