# Implementation Roadmap - Subscription Monetization

This document outlines the step-by-step implementation plan for the Flowtab.Pro subscription monetization system.

## Overview

**Goal:** Launch a subscription-based marketplace where creators earn 70% of revenue based on Flow copy usage.

**Timeline:** 6-8 weeks for MVP

**Key Metric:** Revenue = $10/subscriber/month, distributed as 70% to creators ($7 max per subscriber) + 30% platform fee ($3).

---

## Phase 1: Foundation (Week 1-2)

### Database Schema ✅

- [x] Create migration: `20260121_0949_add_subscription_monetization.py`
- [x] Add models: `Subscription`, `FlowCopy`, `CreatorPayout`
- [x] Update `User` model with subscription fields
- [x] Update `Prompt` model with premium/featured flags

**Files Modified:**
- [apps/api/models.py](../apps/api/models.py)
- [apps/api/alembic/versions/20260121_0949_add_subscription_monetization.py](../apps/api/alembic/versions/20260121_0949_add_subscription_monetization.py)

### Apply Migration

```bash
cd apps/api
alembic upgrade head
```

### CRUD Operations

Create new CRUD functions in [apps/api/crud.py](../apps/api/crud.py):

- [ ] `get_active_subscription(user_id)` - Check if user has active premium subscription
- [ ] `track_flow_copy(user_id, flow_id)` - Log copy event and return payout status
- [ ] `get_user_copy_count(user_id, billing_month)` - Count copies for current month
- [ ] `get_creator_earnings(creator_id, start_date, end_date)` - Aggregate earnings
- [ ] `get_flow_copy_stats(flow_id, start_date, end_date)` - Per-Flow analytics

**Estimated Time:** 8 hours

---

## Phase 2: Stripe Integration (Week 2-3)

### Stripe Setup

1. **Create Stripe Account** (if not exists)
   - Sign up at stripe.com
   - Enable test mode for development

2. **Create Products & Prices**
   ```bash
   # Via Stripe Dashboard or API
   Product: "Flowtab.Pro Premium"
   Price: $10/month recurring
   Price ID: price_premium_monthly_10usd
   ```

3. **Set Up Webhook Endpoint**
   - URL: `https://api.flowtab.pro/webhooks/stripe`
   - Events: `customer.subscription.*`

### Backend Implementation

Create [apps/api/router.py](../apps/api/router.py) endpoints:

#### Subscription Endpoints

- [ ] `POST /api/v1/subscriptions/checkout` - Create Stripe Checkout session
- [ ] `GET /api/v1/subscriptions/me` - Get current user's subscription status
- [ ] `POST /api/v1/subscriptions/cancel` - Cancel subscription at period end
- [ ] `POST /api/v1/subscriptions/resume` - Resume canceled subscription

#### Webhook Handler

- [ ] `POST /webhooks/stripe` - Handle Stripe events
  - `customer.subscription.created` → Create `Subscription` record
  - `customer.subscription.updated` → Update status
  - `customer.subscription.deleted` → Mark as canceled

#### Copy Tracking

- [ ] `POST /api/v1/flows/:flowId/copy` - Log copy event and return prompt text

**Reference:** [docs/SUBSCRIPTION_ARCHITECTURE.md](SUBSCRIPTION_ARCHITECTURE.md#api-endpoints)

**Estimated Time:** 16 hours

### Environment Variables

Add to [apps/api/.env](../apps/api/.env):
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PREMIUM=price_premium_monthly_10usd
```

---

## Phase 3: Frontend Components (Week 3-4)

### Pricing Page

Create [apps/web/app/(app)/pricing/page.tsx](../apps/web/app/(app)/pricing/page.tsx):

- [ ] Free tier feature list
- [ ] Premium tier feature list ($10/month)
- [ ] "Upgrade Now" button (redirects to Stripe Checkout)
- [ ] FAQ section

### Copy Button Component

Create [apps/web/components/FlowCopyButton.tsx](../apps/web/components/FlowCopyButton.tsx):

- [ ] Check user subscription status
- [ ] Show "Upgrade to Copy" for free users
- [ ] Show "Copy Prompt" for premium users
- [ ] Display copy feedback (counted/not counted, copies remaining)
- [ ] Copy to clipboard functionality

### Protected Flow Display

Create [apps/web/components/ProtectedFlowDisplay.tsx](../apps/web/components/ProtectedFlowDisplay.tsx):

- [ ] Show blurred/truncated preview for free users
- [ ] Show full prompt text for premium users
- [ ] Canvas-based rendering for obfuscation (optional)

### Subscription Management

Create [apps/web/app/(app)/account/subscription/page.tsx](../apps/web/app/(app)/account/subscription/page.tsx):

- [ ] Current plan details
- [ ] Billing history
- [ ] Cancel/resume subscription
- [ ] Payment method update (Stripe Customer Portal)

**Estimated Time:** 20 hours

---

## Phase 4: Creator Features (Week 4-5)

### Creator Dashboard

Create [apps/web/app/(app)/creator/dashboard/page.tsx](../apps/web/app/(app)/creator/dashboard/page.tsx):

- [ ] Lifetime earnings summary
- [ ] Current month pending earnings
- [ ] Recent payouts table
- [ ] Top-performing Flows
- [ ] Earnings chart (daily/monthly)

### Analytics API

Add to [apps/api/router.py](../apps/api/router.py):

- [ ] `GET /api/v1/creator/earnings` - Summary of earnings and payouts
- [ ] `GET /api/v1/creator/analytics` - Detailed analytics with filters
- [ ] `GET /api/v1/creator/flows/:flowId/stats` - Per-Flow performance

### Stripe Connect Onboarding

Create [apps/web/app/(app)/creator/setup/page.tsx](../apps/web/app/(app)/creator/setup/page.tsx):

- [ ] "Connect Stripe" button
- [ ] Redirect to Stripe Connect onboarding
- [ ] Handle return URL and save `stripe_connect_id`

**Backend:**
- [ ] `POST /api/v1/creator/connect-stripe` - Create Stripe Connect account link

**Estimated Time:** 16 hours

---

## Phase 5: Background Jobs (Week 5-6)

### Payout Calculation Job

Create [apps/api/jobs/calculate_payouts.py](../apps/api/jobs/calculate_payouts.py):

- [ ] Aggregate copies by creator for previous month
- [ ] Insert/update `creator_payouts` records
- [ ] Trigger Stripe transfers for creators with `stripe_connect_id`
- [ ] Update payout status (pending → paid/failed)
- [ ] Send email notifications to creators

### Cron Setup

Use a job scheduler (e.g., Render Cron Jobs, Heroku Scheduler, or systemd):

```bash
# Run on 1st of each month at 00:00 UTC
0 0 1 * * cd /app && python -m apps.api.jobs.calculate_payouts
```

### Analytics Update Job

Create [apps/api/jobs/update_analytics.py](../apps/api/jobs/update_analytics.py):

- [ ] Update `prompts.total_copies` cached counts
- [ ] Generate daily analytics snapshots (optional)

```bash
# Run daily at 02:00 UTC
0 2 * * * cd /app && python -m apps.api.jobs.update_analytics
```

**Estimated Time:** 12 hours

---

## Phase 6: Testing & Quality Assurance (Week 6)

### Unit Tests

- [ ] Test copy tracking logic (100-copy cap, unique constraint)
- [ ] Test payout calculation (edge cases, rounding)
- [ ] Test subscription status checks
- [ ] Test Stripe webhook handling

### Integration Tests

- [ ] End-to-end subscription flow (checkout → copy → payout)
- [ ] Stripe Connect onboarding flow
- [ ] Webhook event handling (use Stripe CLI)

### Manual Testing Checklist

- [ ] Free user cannot copy Flows
- [ ] Premium user can copy Flows
- [ ] Copy count updates correctly
- [ ] Payout calculation is accurate
- [ ] Stripe transfers succeed
- [ ] Creator dashboard shows correct data
- [ ] Subscription cancellation works

**Estimated Time:** 16 hours

---

## Phase 7: Deployment & Launch (Week 7-8)

### Pre-Launch Checklist

- [ ] Database migrations applied to production
- [ ] Environment variables set (Stripe keys, webhook secret)
- [ ] Background jobs scheduled (cron)
- [ ] Monitoring/alerting configured (Sentry, DataDog)
- [ ] Legal documents updated (ToS, Privacy Policy)
- [ ] Pricing page live
- [ ] Creator onboarding flow tested

### Staging Deployment

1. Deploy to staging environment
2. Run full end-to-end tests
3. Test with Stripe test mode
4. Invite beta creators to test

### Production Deployment

1. Switch Stripe to live mode
2. Deploy to production
3. Monitor error logs for 24 hours
4. Announce launch to existing users

### Post-Launch Monitoring

**Key Metrics to Track:**
- Subscription conversion rate (free → premium)
- Monthly churn rate
- Creator payout ratio (should average ~70%)
- Average copies per subscriber
- Top-performing Flows

**Estimated Time:** 16 hours

---

## Development Commands

### Database Migration

```bash
cd apps/api
alembic upgrade head  # Apply migrations
alembic downgrade -1  # Rollback one migration
alembic revision --autogenerate -m "description"  # Create new migration
```

### Test Stripe Webhooks Locally

```bash
# Install Stripe CLI
stripe login
stripe listen --forward-to localhost:8000/webhooks/stripe

# Trigger test events
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
```

### Run Background Jobs Manually

```bash
cd apps/api
python -m jobs.calculate_payouts  # Monthly payout calculation
python -m jobs.update_analytics   # Update cached metrics
```

### Frontend Development

```bash
cd apps/web
npm run dev  # Start Next.js dev server
npm run build  # Production build
npm run lint  # Check for errors
```

---

## Success Criteria

### MVP Launch Requirements

- ✅ Users can subscribe via Stripe Checkout
- ✅ Premium users can copy Flows with one click
- ✅ Copy events are tracked accurately
- ✅ Creators can connect Stripe and receive payouts
- ✅ Background job calculates payouts correctly
- ✅ Creator dashboard shows earnings

### Post-Launch Goals (Month 1-3)

- 100 premium subscribers
- 50 active creators
- 1,000+ Flows in library
- $1,000 MRR (Monthly Recurring Revenue)
- <5% monthly churn rate

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| Stripe webhook failures | Implement retry logic, monitor webhook delivery in Stripe Dashboard |
| Copy tracking race conditions | Use database unique constraints, idempotent operations |
| Payout calculation errors | Extensive unit tests, dry-run mode for first month |
| Database performance at scale | Add indexes, use materialized views, implement caching |

### Business Risks

| Risk | Mitigation |
|------|------------|
| Low creator adoption | Lower minimum payout to $5, offer launch bonuses |
| Low subscriber conversion | Free trial (7 days), better value messaging, testimonials |
| Content quality issues | Manual review for first 100 Flows, community reporting system |
| Legal/compliance | Clear ToS, creator content guidelines, DMCA takedown process |

---

## Resources

- **Monetization Model:** [MONETIZATION.md](../MONETIZATION.md)
- **Technical Architecture:** [SUBSCRIPTION_ARCHITECTURE.md](SUBSCRIPTION_ARCHITECTURE.md)
- **Creator Guide:** [CREATOR_GUIDE.md](../CREATOR_GUIDE.md)
- **Stripe Documentation:** https://stripe.com/docs
- **Next.js Documentation:** https://nextjs.org/docs
- **FastAPI Documentation:** https://fastapi.tiangolo.com

---

## Next Steps

1. **Review this roadmap** with the team
2. **Create GitHub issues** for each major task
3. **Set up project board** (Kanban or sprint planning)
4. **Begin Phase 1** (database migration and CRUD operations)
5. **Schedule weekly standups** to track progress

**Questions or need clarification?** Open an issue or contact the team lead.
