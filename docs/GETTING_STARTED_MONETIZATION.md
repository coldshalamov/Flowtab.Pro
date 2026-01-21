# Getting Started with Monetization

**Quick start guide for implementing the subscription monetization system.**

## What Was Built

This repository now includes a complete monetization framework:

### 📄 Documentation

1. **[MONETIZATION.md](../MONETIZATION.md)** - Business model, revenue projections, and economic analysis
2. **[docs/SUBSCRIPTION_ARCHITECTURE.md](SUBSCRIPTION_ARCHITECTURE.md)** - Technical implementation details
3. **[CREATOR_GUIDE.md](../CREATOR_GUIDE.md)** - Guide for content creators
4. **[docs/IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Step-by-step development plan

### 💾 Database Schema

New tables added via migration [20260121_0949_add_subscription_monetization.py](../apps/api/alembic/versions/20260121_0949_add_subscription_monetization.py):

- `subscriptions` - User subscription state
- `flow_copies` - Append-only copy event log
- `creator_payouts` - Monthly creator earnings

New fields added to existing tables:
- `users`: `stripe_customer_id`, `is_creator`
- `prompts`: `is_premium`, `featured`, `total_copies`

### 🧩 Code Updates

- **[apps/api/models.py](../apps/api/models.py)** - Added `Subscription`, `FlowCopy`, `CreatorPayout` models
- **[README.md](../README.md)** - Updated with monetization overview

---

## Quick Start

### 1. Apply Database Migration

```bash
cd apps/api
alembic upgrade head
```

**Verify:**
```sql
-- Check tables were created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('subscriptions', 'flow_copies', 'creator_payouts');
```

### 2. Set Up Stripe (Development)

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get API keys from Dashboard → Developers → API Keys
3. Create a product and price:
   - Product name: "Flowtab.Pro Premium"
   - Price: $10/month recurring
   - Copy the Price ID (e.g., `price_1AbCdEfGhIjKlMnO`)

4. Add to `apps/api/.env`:
```bash
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...  # Get from webhooks section
STRIPE_PRICE_ID_PREMIUM=price_1AbCdEfGhIjKlMnO
```

### 3. Install Stripe SDK

```bash
cd apps/api
pip install stripe

cd ../web
npm install @stripe/stripe-js stripe
```

### 4. Next Steps

Follow the [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) to build out:

1. **Phase 1:** CRUD operations for subscriptions and copy tracking
2. **Phase 2:** Stripe Checkout and webhook handlers
3. **Phase 3:** Frontend copy button and protected Flow display
4. **Phase 4:** Creator dashboard and earnings analytics
5. **Phase 5:** Background jobs for payouts
6. **Phase 6:** Testing
7. **Phase 7:** Deployment

---

## Key Concepts

### Revenue Model (At a Glance)

```
User pays $10/month
├─ Platform keeps $3.00 (30%)
└─ Creators earn $7.00 (70%)
   ├─ Distributed based on copies
   ├─ $0.07 per qualifying copy
   └─ Max 100 paid copies per user/month
```

### Copy Tracking Logic

```python
# Pseudocode
if user.is_premium and user.copies_this_month < 100:
    if not already_copied_this_flow_this_month:
        creator.earn(0.07)
        user.copies_this_month += 1
    return prompt_text
else:
    raise PremiumRequired()
```

### Monthly Payout Process

```
1. Calculate (1st of month, 00:00 UTC)
   └─ Aggregate copies by creator for previous month

2. Transfer (via Stripe Connect)
   └─ Minimum $10 payout
   └─ Transfer to creator's bank account

3. Update records
   └─ Mark payouts as 'paid'
   └─ Send email notifications
```

---

## File Structure Overview

```
Flowtab.Pro/
├── MONETIZATION.md                     # Business model
├── CREATOR_GUIDE.md                    # Creator handbook
├── README.md                           # Updated with monetization info
│
├── docs/
│   ├── SUBSCRIPTION_ARCHITECTURE.md    # Technical spec
│   ├── IMPLEMENTATION_ROADMAP.md       # Dev plan
│   └── GETTING_STARTED_MONETIZATION.md # This file
│
├── apps/api/
│   ├── models.py                       # Database models (updated)
│   ├── crud.py                         # Database operations (to be extended)
│   ├── router.py                       # API endpoints (to be extended)
│   │
│   ├── alembic/versions/
│   │   └── 20260121_0949_add_subscription_monetization.py
│   │
│   └── jobs/                           # Background jobs (to be created)
│       ├── calculate_payouts.py
│       └── update_analytics.py
│
└── apps/web/
    ├── app/(app)/
    │   ├── pricing/page.tsx            # To be created
    │   ├── account/subscription/       # To be created
    │   └── creator/dashboard/          # To be created
    │
    └── components/
        ├── FlowCopyButton.tsx          # To be created
        └── ProtectedFlowDisplay.tsx    # To be created
```

---

## Common Tasks

### Testing Copy Tracking Locally

```python
# In Python shell or test script
from apps.api.crud import track_flow_copy
from apps.api.database import SessionLocal

db = SessionLocal()
result = track_flow_copy(
    db=db,
    user_id="user-uuid-here",
    flow_id="flow-uuid-here"
)

print(result)
# {
#   "success": True,
#   "counted_for_payout": True,
#   "user_copies_this_month": 1,
#   "copies_remaining": 99,
#   "creator_earned_cents": 7
# }
```

### Manually Trigger Payout Calculation

```bash
cd apps/api
python -m jobs.calculate_payouts
```

### Test Stripe Webhooks Locally

```bash
# Terminal 1: Start API server
cd apps/api
uvicorn main:app --reload

# Terminal 2: Forward webhooks
stripe listen --forward-to localhost:8000/webhooks/stripe

# Terminal 3: Trigger test event
stripe trigger customer.subscription.created
```

---

## Monitoring & Debugging

### Check Subscription Status

```sql
SELECT
  u.email,
  s.status,
  s.current_period_end,
  s.cancel_at_period_end
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id
WHERE u.email = 'user@example.com';
```

### Check Copy Activity

```sql
SELECT
  fc.copied_at::date as date,
  COUNT(*) as total_copies,
  SUM(CASE WHEN counted_for_payout THEN 1 ELSE 0 END) as paid_copies
FROM flow_copies fc
WHERE fc.copied_at >= NOW() - INTERVAL '7 days'
GROUP BY date
ORDER BY date DESC;
```

### Check Creator Earnings

```sql
SELECT
  u.username,
  cp.billing_month,
  cp.copy_count,
  cp.amount_cents / 100.0 as amount_usd,
  cp.status
FROM creator_payouts cp
JOIN users u ON u.id = cp.creator_id
ORDER BY cp.billing_month DESC, cp.amount_cents DESC;
```

---

## Troubleshooting

### Issue: Migration fails with "relation already exists"

**Solution:**
```bash
# Rollback and reapply
alembic downgrade -1
alembic upgrade head
```

### Issue: Stripe webhook signature verification fails

**Cause:** Incorrect `STRIPE_WEBHOOK_SECRET`

**Solution:**
1. Go to Stripe Dashboard → Webhooks
2. Click on your webhook endpoint
3. Click "Reveal" next to "Signing secret"
4. Update `.env` with correct value

### Issue: Copy count not updating

**Check:**
1. User has active subscription (`subscriptions.status = 'active'`)
2. Unique constraint isn't blocking insert (check `flow_copies` table)
3. API endpoint is returning success response

---

## Security Checklist

Before deploying to production:

- [ ] Use Stripe live keys (not test keys)
- [ ] Enable webhook signature verification
- [ ] Set up HTTPS for webhook endpoint
- [ ] Add rate limiting to copy endpoint (100 req/min per user)
- [ ] Validate user authentication on all protected endpoints
- [ ] Encrypt sensitive data at rest (database encryption)
- [ ] Set up Stripe fraud detection (Radar)
- [ ] Implement CORS restrictions on API
- [ ] Add input validation for all API endpoints
- [ ] Set up monitoring for failed payments and chargebacks

---

## Performance Optimization

As the platform grows, consider:

1. **Caching subscription status** (Redis, 1-hour TTL)
2. **Denormalized copy counts** (already done in `prompts.total_copies`)
3. **Partition `flow_copies` table** by month
4. **Materialized views** for analytics dashboards
5. **CDN caching** for public Flow metadata
6. **Batch Stripe transfers** (50 at a time to avoid rate limits)

---

## Resources

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Connect Guide:** https://stripe.com/docs/connect
- **Stripe Webhooks:** https://stripe.com/docs/webhooks
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **SQLModel Documentation:** https://sqlmodel.tiangolo.com
- **Alembic Tutorial:** https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## Support

For questions or issues:

1. Check the [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)
2. Review the [Subscription Architecture](SUBSCRIPTION_ARCHITECTURE.md)
3. Open a GitHub issue with the label `monetization`
4. Contact: dev@flowtab.pro

---

**Ready to build?** Start with [Phase 1 of the Implementation Roadmap](IMPLEMENTATION_ROADMAP.md#phase-1-foundation-week-1-2).
