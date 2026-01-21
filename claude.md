# Flowtab.Pro - Claude Project Context

**Status:** Monetization system designed and documented (ready for Phase 1 implementation)

---

## 🎯 Project Overview

Flowtab.Pro is a **community-driven marketplace for browser automation Flows (prompts) with creator revenue sharing**.

### Key Features
- Developers discover and share battle-tested browser automation workflows
- Premium subscribers ($10/month) get full library access
- Creators earn 70% of subscription revenue based on actual usage
- Self-balancing economic model prevents revenue dilution

### Tech Stack
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS v4, shadcn/ui
- **Backend:** FastAPI, SQLModel, PostgreSQL, Alembic
- **Deployment:** Vercel (frontend), Render.com (backend)
- **Payments:** Stripe (subscriptions + Stripe Connect for payouts)

---

## 💰 Monetization System (IMPLEMENTED - DESIGN PHASE)

### Economic Model (Self-Balancing)

```
Per Subscriber Per Month:
$10.00  Total Revenue
├─ $7.00  Creator Pool (distributed based on usage)
└─ $3.00  Platform Fee (30%)
```

### Copy Tracking & Anti-Gaming

**User Limits:**
- Each premium subscriber gets **100 paid copies/month** cap
- Copies 1-100: $0.07 payout per copy to creator
- Copies 101+: Free (better UX, no payout)
- Result: Max payout per user = $7.00 (exactly matches creator pool)

**Unique Copy Constraint:**
- One copy per `(user_id, flow_id, billing_month)` combo
- Prevents users from spamming same Flow
- Prevents accidental double-counting

**Edge Cases Handled:**
| User Type | Copies | Creator Payout | Platform Keeps |
|-----------|--------|----------------|----------------|
| Power user | 100 | $7.00 | $3.00 |
| Moderate | 50 | $3.50 | $6.50 |
| Light | 10 | $0.70 | $9.30 |
| Heavy (250+) | 100 (capped) | $7.00 | $3.00 |

Platform benefits from users copying <100 Flows (expected majority).

### Creator Earnings

**Payout Formula:** `Copies × $0.07` (monthly)

**Example Scenarios:**
- 500 copies in month = $35.00
- 1,200 copies in month = $84.00
- Popular Flow (5,000 copies across all users) = $350.00

---

## 📊 Database Schema (Migration Created)

### New Tables

**`subscriptions`** - Stripe-managed subscription state
```python
- user_id (FK users)
- stripe_subscription_id (unique)
- stripe_customer_id
- status: active|canceled|past_due|unpaid
- current_period_start/end
- cancel_at_period_end
```

**`flow_copies`** - Append-only copy event log (for payout calculation)
```python
- user_id (FK users)
- flow_id (FK prompts)
- creator_id (denormalized for speed)
- counted_for_payout: boolean
- copied_at: timestamp
- billing_month: DATE (YYYY-MM-01 format)
- UNIQUE (user_id, flow_id, billing_month) # Prevents duplicates
```

**`creator_payouts`** - Monthly aggregated earnings
```python
- creator_id (FK users)
- billing_month: DATE
- copy_count: int
- amount_cents: int (copy_count * 7)
- status: pending|processing|paid|failed
- stripe_transfer_id (for audit trail)
- paid_at: timestamp
```

### Schema Updates to Existing Tables

**`users` additions:**
- `stripe_customer_id` (for subscriptions)
- `stripe_connect_id` (for Stripe Connect payouts)
- `is_creator` (boolean flag)

**`prompts` (Flows) additions:**
- `is_premium` (boolean - premium-only Flows)
- `featured` (boolean - featured in marketplace)
- `total_copies` (denormalized counter for analytics)

---

## 🔧 Implementation Roadmap (7 Phases, 6-8 weeks)

### Phase 1: Database & CRUD (Week 1-2)
- [x] Create migration: `20260121_0949_add_subscription_monetization.py`
- [ ] Apply migration: `alembic upgrade head`
- [ ] Add SQLModel models for Subscription, FlowCopy, CreatorPayout
- [ ] Implement CRUD endpoints for copy tracking
- [ ] Write tests for copy limit enforcement

### Phase 2: Stripe Integration (Week 2-3)
- [ ] Create Stripe account & get API keys
- [ ] Set up webhook receiver at `POST /webhooks/stripe`
- [ ] Implement subscription creation flow
- [ ] Handle webhooks: `customer.subscription.created/updated/deleted`
- [ ] Store Stripe IDs in database
- [ ] Implement subscription status checks

### Phase 3: Frontend Components (Week 3-4)
- [ ] Create subscription payment form (Stripe Elements)
- [ ] Build subscription management page (upgrade/downgrade/cancel)
- [ ] Add "Copy Flow" button with copy counter
- [ ] Display copy limit UI (e.g., "15/100 copies used")
- [ ] Show creator earnings dashboard

### Phase 4: Creator Features (Week 4-5)
- [ ] Set up Stripe Connect integration
- [ ] Creator onboarding flow (bank account, tax info)
- [ ] Creator dashboard showing earnings
- [ ] Payout history and status tracking
- [ ] Creator settings (enable/disable monetization)

### Phase 5: Background Jobs (Week 5-6)
- [ ] Daily job: Calculate pending payouts
- [ ] Monthly job: Mark copies as "counted_for_payout"
- [ ] Monthly job: Transfer funds via Stripe Connect
- [ ] Monthly job: Send creator payout emails
- [ ] Alert system for failed payouts

### Phase 6: Testing & QA (Week 6)
- [ ] End-to-end subscription tests
- [ ] Copy limit enforcement tests
- [ ] Payout calculation accuracy tests
- [ ] Stripe webhook validation tests
- [ ] Multi-user concurrency tests

### Phase 7: Deployment & Monitoring (Week 7-8)
- [ ] Deploy to Render backend
- [ ] Deploy to Vercel frontend
- [ ] Set up monitoring/alerting for Stripe webhooks
- [ ] Set up logging for payout jobs
- [ ] Production Stripe account configuration
- [ ] Go live with MVP

---

## 📁 Key Files & Locations

### Documentation
- [MONETIZATION.md](MONETIZATION.md) - Full economic model (2,700+ lines)
- [docs/SUBSCRIPTION_ARCHITECTURE.md](docs/SUBSCRIPTION_ARCHITECTURE.md) - Technical spec (1,000+ lines)
- [CREATOR_GUIDE.md](CREATOR_GUIDE.md) - Creator onboarding (600+ lines)
- [docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) - Detailed phase breakdown

### Code
- [apps/api/models.py](apps/api/models.py) - SQLModel definitions (updated)
- [apps/api/crud.py](apps/api/crud.py) - Database operations (updated)
- [apps/api/alembic/versions/20260121_0949_add_subscription_monetization.py](apps/api/alembic/versions/20260121_0949_add_subscription_monetization.py) - Migration
- [apps/web/src/lib/api.ts](apps/web/src/lib/api.ts) - Frontend API client (updated)

### Configuration
- `.env` - Backend (requires: `DATABASE_URL`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`)
- `vercel.json` - Frontend deployment

---

## 🔐 Security & Performance Notes

### Anti-Gaming Protections
1. **Unique Copy Constraint** - One copy per (user, flow, month)
2. **100-Copy Cap** - Prevents unlimited value dilution
3. **Verified Subscriptions** - Check Stripe webhook signature on every copy event
4. **Creator Verification** - Only verified creators receive payouts

### Performance Optimizations
1. **Denormalized Fields** - `creator_id` in flow_copies, `total_copies` in prompts
2. **Partial Indexes** - Query only uncounted copies: `WHERE counted_for_payout = FALSE`
3. **Batch Processing** - Aggregate payouts in nightly jobs (not real-time)
4. **Stripe Caching** - Cache subscription status for 5 min to reduce API calls

### Monitoring Queries
```sql
-- Daily: Pending payouts
SELECT creator_id, SUM(amount_cents) FROM creator_payouts
WHERE status='pending' AND billing_month=CURRENT_DATE;

-- Check for duplicate copies (should be 0)
SELECT user_id, flow_id, billing_month, COUNT(*)
FROM flow_copies GROUP BY user_id, flow_id, billing_month HAVING COUNT(*) > 1;

-- Creator earnings this month
SELECT creator_id, COUNT(*) as copies, COUNT(*)*7 as cents
FROM flow_copies WHERE billing_month=DATE_TRUNC('month', NOW())
AND counted_for_payout=TRUE GROUP BY creator_id ORDER BY cents DESC;
```

---

## 🚀 Getting Started (For Context)

### Local Development
```bash
# Backend
cd apps/api
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
cp .env.example .env
# Edit .env with DATABASE_URL
alembic upgrade head
python seed.py
uvicorn main:app --reload

# Frontend (in another terminal)
cd apps/web
npm install
npm run dev
```

### Next Steps
1. Apply migration: `alembic upgrade head`
2. Set up Stripe account (get API keys)
3. Start Phase 1 implementation (copy tracking CRUD)

---

## 📝 Notes for Claude

- **Current Status:** Design complete, ready for Phase 1 (database CRUD)
- **Critical Path:** Get copy tracking working first (foundation for all other features)
- **Revenue Math:** Always verify: platform_revenue + creator_payouts = $10 per subscriber
- **Stripe:** Webhooks must be verified; never trust client-side subscription claims
- **Testing:** Write tests BEFORE implementation (especially payout calculations)
- **Creator Protection:** Never process payouts without verified Stripe Connect account

---

**Last Updated:** 2026-01-21
**Monetization Design:** Complete
**Implementation Status:** Ready for Phase 1
