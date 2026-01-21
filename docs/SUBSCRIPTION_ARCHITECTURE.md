# Subscription Architecture - Technical Specification

## System Overview

This document defines the technical implementation of Flowtab.Pro's subscription-based monetization system with creator revenue sharing.

## Database Schema

### New Tables

#### `flow_copies`
Append-only log of all copy events, used for payout calculation and anti-fraud.

```sql
CREATE TABLE flow_copies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  flow_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
  creator_id UUID NOT NULL, -- Denormalized for faster aggregation

  counted_for_payout BOOLEAN NOT NULL DEFAULT FALSE,
  copied_at TIMESTAMP NOT NULL DEFAULT NOW(),
  billing_month DATE NOT NULL, -- YYYY-MM-01 for grouping

  CONSTRAINT uq_copy_user_flow_month UNIQUE (user_id, flow_id, billing_month)
);

CREATE INDEX idx_copies_billing ON flow_copies(billing_month, counted_for_payout);
CREATE INDEX idx_copies_creator ON flow_copies(creator_id, billing_month) WHERE counted_for_payout = TRUE;
CREATE INDEX idx_copies_user_month ON flow_copies(user_id, billing_month) WHERE counted_for_payout = TRUE;
```

**Key Design Decisions:**
- `UNIQUE` constraint prevents duplicate copy events
- `billing_month` normalized to first day of month (e.g., `2026-01-01`) for clean aggregation
- `creator_id` denormalized to avoid JOINs during payout calculations
- Partial indexes on `counted_for_payout` for query performance

#### `creator_payouts`
Monthly aggregated payouts for creators.

```sql
CREATE TABLE creator_payouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  billing_month DATE NOT NULL,

  copy_count INT NOT NULL DEFAULT 0,
  amount_cents INT NOT NULL DEFAULT 0, -- copy_count * 7 cents

  status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, paid, failed
  stripe_transfer_id TEXT,
  paid_at TIMESTAMP,

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT uq_payout_creator_month UNIQUE (creator_id, billing_month)
);

CREATE INDEX idx_payouts_status ON creator_payouts(status, billing_month);
CREATE INDEX idx_payouts_creator ON creator_payouts(creator_id, billing_month DESC);
```

#### `subscriptions`
User subscription state (managed by Stripe webhooks).

```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  stripe_subscription_id TEXT NOT NULL UNIQUE,
  stripe_customer_id TEXT NOT NULL,

  status VARCHAR(20) NOT NULL, -- active, canceled, past_due, unpaid
  plan_id VARCHAR(50) NOT NULL DEFAULT 'premium_monthly', -- Future: support multiple tiers

  current_period_start TIMESTAMP NOT NULL,
  current_period_end TIMESTAMP NOT NULL,
  cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT uq_subscription_user UNIQUE (user_id)
);

CREATE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### Schema Modifications to Existing Tables

#### `users` table additions

```sql
ALTER TABLE users ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE users ADD COLUMN stripe_connect_id TEXT; -- For creator payouts
ALTER TABLE users ADD COLUMN is_creator BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX idx_users_stripe_connect ON users(stripe_connect_id) WHERE stripe_connect_id IS NOT NULL;
```

#### `prompts` table additions

```sql
ALTER TABLE prompts ADD COLUMN is_premium BOOLEAN DEFAULT TRUE; -- FALSE = free tier accessible
ALTER TABLE prompts ADD COLUMN featured BOOLEAN DEFAULT FALSE; -- Show in free tier preview
ALTER TABLE prompts ADD COLUMN total_copies INT DEFAULT 0; -- Cached copy count

CREATE INDEX idx_prompts_premium ON prompts(is_premium, featured);
```

## API Endpoints

### Copy Tracking

#### `POST /api/v1/flows/:flowId/copy`

**Authentication:** Required (premium subscription)

**Request:**
```json
{}
```

**Response (200 OK):**
```json
{
  "success": true,
  "copied": true,
  "counted_for_payout": true,
  "user_copies_this_month": 47,
  "copies_remaining": 53,
  "creator_earned_cents": 7,
  "already_copied": false,
  "prompt_text": "Your browser automation prompt text here..."
}
```

**Response (403 Forbidden - Not Premium):**
```json
{
  "error": "premium_required",
  "message": "Upgrade to premium to copy Flows",
  "upgrade_url": "/pricing"
}
```

**Response (200 OK - Already Copied):**
```json
{
  "success": true,
  "copied": true,
  "counted_for_payout": false,
  "already_copied": true,
  "prompt_text": "Your browser automation prompt text here..."
}
```

**Response (200 OK - Cap Reached):**
```json
{
  "success": true,
  "copied": true,
  "counted_for_payout": false,
  "user_copies_this_month": 100,
  "copies_remaining": 0,
  "cap_reached": true,
  "prompt_text": "Your browser automation prompt text here..."
}
```

**Backend Logic:**
```python
from datetime import datetime
from sqlalchemy import select, func, and_

async def copy_flow(
    db: AsyncSession,
    user_id: str,
    flow_id: str
) -> dict:
    # Check subscription status
    subscription = await get_active_subscription(db, user_id)
    if not subscription or subscription.status != 'active':
        raise HTTPException(status_code=403, detail="premium_required")

    # Get Flow and creator_id
    flow = await get_flow_by_id(db, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    billing_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Count user's paid copies this month
    user_copy_count = await db.scalar(
        select(func.count()).select_from(flow_copies).where(
            and_(
                flow_copies.c.user_id == user_id,
                flow_copies.c.billing_month == billing_month,
                flow_copies.c.counted_for_payout == True
            )
        )
    )

    # Determine if this copy counts toward payout
    counted = user_copy_count < 100

    # Insert copy event (ON CONFLICT DO NOTHING)
    stmt = insert(flow_copies).values(
        user_id=user_id,
        flow_id=flow_id,
        creator_id=flow.author_id,
        counted_for_payout=counted,
        billing_month=billing_month
    ).on_conflict_do_nothing(
        index_elements=['user_id', 'flow_id', 'billing_month']
    )

    result = await db.execute(stmt)
    await db.commit()

    already_copied = result.rowcount == 0
    new_count = user_copy_count + (1 if counted and not already_copied else 0)

    return {
        "success": True,
        "copied": True,
        "counted_for_payout": counted and not already_copied,
        "user_copies_this_month": new_count,
        "copies_remaining": max(0, 100 - new_count),
        "creator_earned_cents": 7 if (counted and not already_copied) else 0,
        "already_copied": already_copied,
        "cap_reached": new_count >= 100,
        "prompt_text": flow.promptText
    }
```

### Creator Earnings

#### `GET /api/v1/creator/earnings`

**Authentication:** Required (creator account)

**Response:**
```json
{
  "total_lifetime_cents": 45600,
  "total_lifetime_usd": "456.00",
  "current_month": {
    "month": "2026-01",
    "copies": 142,
    "pending_cents": 994,
    "pending_usd": "9.94",
    "status": "pending"
  },
  "recent_payouts": [
    {
      "month": "2025-12",
      "copies": 508,
      "amount_cents": 3556,
      "amount_usd": "35.56",
      "status": "paid",
      "paid_at": "2026-01-05T00:00:00Z",
      "stripe_transfer_id": "tr_1AbCdEfGhIjKlMnO"
    }
  ],
  "top_flows": [
    {
      "flow_id": "uuid-here",
      "title": "Scrape LinkedIn Profiles",
      "slug": "scrape-linkedin-profiles",
      "copies_this_month": 87,
      "earnings_this_month_cents": 609
    }
  ]
}
```

#### `GET /api/v1/creator/analytics`

**Authentication:** Required (creator account)

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `flow_id` (optional): Filter to specific Flow

**Response:**
```json
{
  "period": {
    "start": "2025-12-01",
    "end": "2026-01-31"
  },
  "summary": {
    "total_copies": 1240,
    "unique_users": 892,
    "earnings_cents": 8680,
    "avg_copies_per_flow": 248
  },
  "daily_breakdown": [
    {
      "date": "2026-01-01",
      "copies": 42,
      "unique_users": 38,
      "earnings_cents": 294
    }
  ],
  "flow_performance": [
    {
      "flow_id": "uuid",
      "title": "Extract Hacker News Comments",
      "copies": 412,
      "unique_users": 389,
      "earnings_cents": 2884
    }
  ]
}
```

## Background Jobs

### Monthly Payout Calculation

**Schedule:** Runs on the 1st of each month at 00:00 UTC

**Job:** Calculate payouts for previous month and initiate Stripe transfers

```python
# apps/api/jobs/calculate_payouts.py

from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.dialects.postgresql import insert

async def calculate_monthly_payouts(db: AsyncSession):
    """
    Calculate creator payouts for the previous month.
    Called by cron job on the 1st of each month.
    """
    # Get previous month's date (2026-01-01 → 2025-12-01)
    today = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = (today - timedelta(days=1)).replace(day=1)

    logger.info(f"Calculating payouts for {last_month.strftime('%Y-%m')}")

    # Aggregate copies by creator
    query = select(
        flow_copies.c.creator_id,
        func.count().label('copy_count')
    ).where(
        and_(
            flow_copies.c.billing_month == last_month,
            flow_copies.c.counted_for_payout == True
        )
    ).group_by(flow_copies.c.creator_id)

    results = await db.execute(query)

    for row in results:
        amount_cents = row.copy_count * 7  # $0.07 per copy

        # Insert/update payout record
        stmt = insert(creator_payouts).values(
            creator_id=row.creator_id,
            billing_month=last_month,
            copy_count=row.copy_count,
            amount_cents=amount_cents,
            status='pending'
        ).on_conflict_do_update(
            index_elements=['creator_id', 'billing_month'],
            set_={
                'copy_count': row.copy_count,
                'amount_cents': amount_cents,
                'updated_at': datetime.utcnow()
            }
        )

        await db.execute(stmt)

    await db.commit()
    logger.info(f"Payout calculation complete for {last_month.strftime('%Y-%m')}")

    # Trigger Stripe transfers
    await process_pending_payouts(db, last_month)


async def process_pending_payouts(db: AsyncSession, billing_month: datetime):
    """
    Process pending payouts via Stripe Connect transfers.
    """
    MINIMUM_PAYOUT_CENTS = 1000  # $10 minimum

    query = select(creator_payouts).where(
        and_(
            creator_payouts.c.billing_month == billing_month,
            creator_payouts.c.status == 'pending',
            creator_payouts.c.amount_cents >= MINIMUM_PAYOUT_CENTS
        )
    )

    payouts = await db.execute(query)

    for payout in payouts:
        try:
            # Get creator's Stripe Connect account
            creator = await get_user_by_id(db, payout.creator_id)
            if not creator.stripe_connect_id:
                logger.warning(f"Creator {payout.creator_id} has no Stripe Connect account")
                continue

            # Create Stripe transfer
            transfer = stripe.Transfer.create(
                amount=payout.amount_cents,
                currency='usd',
                destination=creator.stripe_connect_id,
                transfer_group=f"payout_{billing_month.strftime('%Y%m')}"
            )

            # Update payout record
            payout.status = 'paid'
            payout.stripe_transfer_id = transfer.id
            payout.paid_at = datetime.utcnow()

            await db.commit()
            logger.info(f"Paid ${payout.amount_cents/100:.2f} to {creator.email}")

        except stripe.error.StripeError as e:
            logger.error(f"Stripe transfer failed for payout {payout.id}: {e}")
            payout.status = 'failed'
            await db.commit()
```

### Analytics Aggregation

**Schedule:** Daily at 02:00 UTC

**Job:** Update cached metrics for faster dashboard loading

```python
# apps/api/jobs/update_analytics.py

async def update_flow_copy_counts(db: AsyncSession):
    """
    Update cached copy counts on prompts table.
    """
    query = select(
        flow_copies.c.flow_id,
        func.count().label('total_copies')
    ).group_by(flow_copies.c.flow_id)

    results = await db.execute(query)

    for row in results:
        await db.execute(
            update(Prompt)
            .where(Prompt.id == row.flow_id)
            .values(total_copies=row.total_copies)
        )

    await db.commit()
```

## Stripe Integration

### Subscription Flow

**1. Customer Creation**
```python
customer = stripe.Customer.create(
    email=user.email,
    metadata={'user_id': user.id}
)
user.stripe_customer_id = customer.id
```

**2. Checkout Session**
```python
session = stripe.checkout.Session.create(
    customer=user.stripe_customer_id,
    mode='subscription',
    line_items=[{
        'price': 'price_premium_monthly_10usd',  # Created in Stripe Dashboard
        'quantity': 1
    }],
    success_url='https://flowtab.pro/dashboard?subscription=success',
    cancel_url='https://flowtab.pro/pricing'
)
```

**3. Webhook Handling**

```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")

    if event.type == 'customer.subscription.created':
        await handle_subscription_created(db, event.data.object)
    elif event.type == 'customer.subscription.updated':
        await handle_subscription_updated(db, event.data.object)
    elif event.type == 'customer.subscription.deleted':
        await handle_subscription_canceled(db, event.data.object)

    return {"status": "success"}


async def handle_subscription_created(db: AsyncSession, subscription_obj):
    user = await get_user_by_stripe_customer(db, subscription_obj.customer)

    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id=subscription_obj.id,
        stripe_customer_id=subscription_obj.customer,
        status=subscription_obj.status,
        current_period_start=datetime.fromtimestamp(subscription_obj.current_period_start),
        current_period_end=datetime.fromtimestamp(subscription_obj.current_period_end)
    )

    db.add(subscription)
    await db.commit()
```

### Creator Payouts (Stripe Connect)

**1. Connect Onboarding**
```python
account_link = stripe.AccountLink.create(
    account=user.stripe_connect_id,
    refresh_url='https://flowtab.pro/creator/setup',
    return_url='https://flowtab.pro/creator/dashboard',
    type='account_onboarding'
)
```

**2. Transfer Funds**
```python
transfer = stripe.Transfer.create(
    amount=payout.amount_cents,
    currency='usd',
    destination=creator.stripe_connect_id,
    description=f"Flowtab.Pro payout for {billing_month}"
)
```

## Frontend Components

### Copy Button Component

```tsx
// apps/web/components/FlowCopyButton.tsx

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Copy, Check, Lock } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { useSubscription } from '@/lib/subscription';

export function FlowCopyButton({
  flowId,
  title
}: {
  flowId: string;
  title: string;
}) {
  const { user } = useAuth();
  const { isPremium, isLoading: subLoading } = useSubscription();
  const [copied, setCopied] = useState(false);
  const [copyData, setCopyData] = useState<any>(null);

  const handleCopy = async () => {
    try {
      const response = await fetch(`/api/v1/flows/${flowId}/copy`, {
        method: 'POST',
        credentials: 'include'
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.error === 'premium_required') {
          window.location.href = '/pricing';
          return;
        }
        throw new Error(data.message);
      }

      // Copy to clipboard
      await navigator.clipboard.writeText(data.prompt_text);

      setCopied(true);
      setCopyData(data);

      setTimeout(() => setCopied(false), 3000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  if (!user || subLoading) {
    return <Button disabled>Loading...</Button>;
  }

  if (!isPremium) {
    return (
      <Button onClick={() => window.location.href = '/pricing'} variant="default">
        <Lock className="h-4 w-4 mr-2" />
        Upgrade to Copy
      </Button>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <Button
        onClick={handleCopy}
        variant={copied ? 'secondary' : 'default'}
        className="gap-2"
      >
        {copied ? (
          <>
            <Check className="h-4 w-4" />
            Copied!
          </>
        ) : (
          <>
            <Copy className="h-4 w-4" />
            Copy Prompt
          </>
        )}
      </Button>

      {copied && copyData && (
        <div className="text-xs text-muted-foreground space-y-1">
          {copyData.counted_for_payout && (
            <p className="text-green-600 dark:text-green-400">
              ✓ Creator earned $0.07
            </p>
          )}
          <p>
            {copyData.copies_remaining > 0
              ? `${copyData.copies_remaining} paid copies remaining this month`
              : 'Monthly copy limit reached (unlimited free copies)'}
          </p>
          {copyData.already_copied && (
            <p className="text-amber-600 dark:text-amber-400">
              Already copied this month
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

### Protected Flow Display

```tsx
// apps/web/components/ProtectedFlowDisplay.tsx

'use client';

import { useEffect, useRef } from 'react';

export function ProtectedFlowDisplay({
  promptText,
  isPremium
}: {
  promptText: string;
  isPremium: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || isPremium) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Render text as canvas (prevents easy selection)
    ctx.font = '14px monospace';
    ctx.fillStyle = '#888';

    const lines = promptText.split('\n').slice(0, 10); // Show preview
    lines.forEach((line, i) => {
      const blurred = line.substring(0, 40) + '...';
      ctx.fillText(blurred, 10, 20 + i * 18);
    });

    ctx.fillText('🔒 Upgrade to view full prompt', 10, 220);
  }, [promptText, isPremium]);

  if (isPremium) {
    return (
      <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
        <code>{promptText}</code>
      </pre>
    );
  }

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={600}
        height={250}
        className="border rounded-lg bg-muted/50"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent pointer-events-none" />
    </div>
  );
}
```

## Security Considerations

### Rate Limiting
- 100 copy requests per minute per user
- 1000 copy requests per minute per IP (prevent abuse)

### Authentication
- JWT tokens with 1-hour expiry
- Refresh tokens for session management
- Subscription status checked on every copy request

### Data Privacy
- Copy events contain no PII beyond user_id
- Payout data encrypted at rest
- Stripe handles all payment data (PCI compliance)

## Performance Optimizations

### Database Indexes
- Partial indexes on `counted_for_payout` columns
- Covering indexes for common queries
- Monthly partitioning for `flow_copies` table (future)

### Caching
- Redis cache for subscription status (1-hour TTL)
- Cached copy counts on `prompts` table
- CDN caching for public Flow metadata

### Query Optimization
- Denormalized `creator_id` in `flow_copies`
- Materialized views for analytics dashboards
- Batch Stripe transfers (50 at a time)

## Monitoring & Alerts

### Key Metrics
- Copy request latency (p50, p95, p99)
- Failed Stripe transfers
- Payout calculation job duration
- Subscription churn rate

### Alerts
- Copy endpoint error rate >1%
- Payout job fails to complete
- Stripe webhook delays >5 minutes
- Subscription status sync failures

## Deployment Checklist

- [ ] Database migrations applied
- [ ] Stripe products/prices created
- [ ] Webhook endpoints configured
- [ ] Background jobs scheduled (cron)
- [ ] Environment variables set (Stripe keys)
- [ ] Monitoring dashboards configured
- [ ] Creator onboarding flow tested
- [ ] Payment flows tested (staging)
- [ ] Legal docs updated (ToS, Privacy Policy)

---

## Next Steps

1. Implement database migrations
2. Build API endpoints
3. Integrate Stripe subscriptions
4. Create frontend components
5. Set up background jobs
6. Deploy to staging environment
7. Conduct load testing
8. Launch to beta users
