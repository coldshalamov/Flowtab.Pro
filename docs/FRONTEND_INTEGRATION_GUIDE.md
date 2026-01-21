# Frontend Integration Guide - Monetization Features

**For:** Frontend/React developers implementing Flowtab.Pro monetization
**Last Updated:** January 21, 2026

---

## 🎯 Overview

The backend has all monetization features ready. Your job is to:

1. Build UI for subscription management
2. Display prompts with non-copyable formatting + copy button
3. Create creator dashboard
4. Integrate Stripe.js for payments

---

## 📦 Frontend Setup

### Install Dependencies

```bash
cd apps/web
npm install @stripe/react-stripe-js @stripe/js
```

### Environment Variables (.env.local)

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...  # Get from backend config
```

---

## 🔑 Key Flows

### Flow 1: User Subscribes

```
1. User clicks "Upgrade to Premium"
   ↓
2. Frontend: POST /v1/subscriptions/checkout
   ← Response: { sessionId: "cs_test_..." }
   ↓
3. Redirect to Stripe Checkout:
   stripe.redirectToCheckout({ sessionId })
   ↓
4. User pays with card
   ↓
5. Stripe sends webhook to backend: customer.subscription.created
   ↓
6. User's subscription is now ACTIVE in database
   ↓
7. Redirect to /account/subscription?success=true
```

### Flow 2: User Copies a Prompt

```
1. User views a prompt (already implemented)
   ↓
2. Click "Copy to Clipboard" button
   ↓
3. Check subscription status: GET /v1/subscriptions/me
   - If not_subscriber: show upgrade modal
   - If subscriber: continue
   ↓
4. Call: POST /v1/flows/{flow_id}/copy
   ↓
5. Response contains:
   - copies_remaining: 87  (out of 100)
   - payout_earned: 7 cents (to creator)
   - If copies_remaining === 0:
     Show "You've used all 100 copies this month!"
   ↓
6. Copy JSON to clipboard (or show success)
7. Show toast: "✓ Copied! (87 copies left)"
```

### Flow 3: Creator Views Earnings

```
1. Creator clicks "Dashboard" in menu
   ↓
2. GET /v1/creators/me/earnings
   ↓
3. Response:
   {
     "account_balance_cents": 4207,
     "total_earnings_cents": 8914,
     "monthly_earnings": [...]
   }
   ↓
4. Display charts and tables showing:
   - Total earnings: $89.14
   - Account balance: $42.07
   - Monthly breakdown
```

### Flow 4: Creator Starts Getting Paid

```
1. Creator clicks "Set Up Payments" in dashboard
   ↓
2. POST /v1/creators/me/connect
   ↓
3. Response: { onboarding_url: "https://connect.stripe.com/..." }
   ↓
4. Redirect user to onboarding URL
   ↓
5. User completes Stripe Connect (bank account, tax info)
   ↓
6. Stripe redirects back to /creator/dashboard
   ↓
7. Now payouts will be processed monthly
```

---

## 🎨 UI Components Needed

### 1. Subscription Button

```tsx
// apps/web/src/components/SubscriptionButton.tsx
export function SubscriptionButton() {
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState(null);

  const handleSubscribe = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/v1/subscriptions/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      const data = await res.json();

      // Redirect to Stripe
      const stripe = await stripePromise;
      await stripe.redirectToCheckout({ sessionId: data.sessionId });
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button onClick={handleSubscribe} disabled={isLoading}>
      {isLoading ? 'Loading...' : 'Upgrade to Premium'}
    </button>
  );
}
```

### 2. Copy Button with Counter

```tsx
// apps/web/src/components/FlowCopyButton.tsx
export function FlowCopyButton({ flowId, flowContent }) {
  const [copies, setCopies] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCopy = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/v1/flows/${flowId}/copy`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`
          }
        }
      );

      if (!res.ok) {
        if (res.status === 403) {
          // Show upgrade modal
          showUpgradeModal();
          return;
        }
        throw new Error(await res.text());
      }

      const data = await res.json();
      setCopies(data.copies_remaining);

      // Copy to clipboard
      await navigator.clipboard.writeText(
        JSON.stringify(JSON.parse(flowContent), null, 2)
      );

      showToast({
        title: 'Copied!',
        message: `${data.copies_remaining} copies left this month`,
        type: 'success'
      });
    } catch (err) {
      showToast({
        title: 'Error',
        message: err.message,
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleCopy} disabled={isLoading}>
        Copy {copies !== null && `(${copies}/100)`}
      </button>
      {copies === 0 && (
        <p style={{ color: 'orange' }}>
          You've used all 100 copies this month. Resets next month!
        </p>
      )}
    </div>
  );
}
```

### 3. Prompt Display (Non-Copyable)

The prompt should be displayed in a way that discourages direct copying:

```tsx
// apps/web/src/components/PromptDisplay.tsx
export function PromptDisplay({ prompt }) {
  return (
    <div
      style={{
        backgroundColor: '#f0f0f0',
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '16px',
        userSelect: 'none',
        WebkitUserSelect: 'none',
        MozUserSelect: 'none',
        msUserSelect: 'none'
      }}
    >
      <div
        style={{
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          backgroundColor: '#fff',
          padding: '12px',
          borderRadius: '4px',
          border: '1px dashed #999'
        }}
      >
        {prompt.promptText}
      </div>

      <div style={{ marginTop: '12px' }}>
        <FlowCopyButton
          flowId={prompt.id}
          flowContent={prompt.promptText}
        />
      </div>
    </div>
  );
}
```

### 4. Subscription Status Bar

```tsx
// apps/web/src/components/SubscriptionStatus.tsx
export function SubscriptionStatus() {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/v1/subscriptions/me`, {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`
          }
        });
        const data = await res.json();
        setStatus(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) return <div>Loading...</div>;
  if (!status.is_subscriber) {
    return (
      <div style={{ backgroundColor: '#fff3cd', padding: '8px', borderRadius: '4px' }}>
        <strong>Premium subscription required to copy prompts.</strong>
        <SubscriptionButton />
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#d4edda', padding: '8px', borderRadius: '4px' }}>
      ✓ Premium Active | {status.copies_remaining}/100 copies this month
    </div>
  );
}
```

### 5. Creator Dashboard

```tsx
// apps/web/src/app/creator/dashboard/page.tsx
export default function CreatorDashboard() {
  const [earnings, setEarnings] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/v1/creators/me/earnings`, {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`
          }
        });
        const data = await res.json();
        setEarnings(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) return <div>Loading...</div>;
  if (!earnings) return <div>No earnings yet</div>;

  return (
    <div>
      <h1>Creator Dashboard</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <Card title="Account Balance">
          <h2>${earnings.account_balance_dollars.toFixed(2)}</h2>
          <p>Available to use or withdraw</p>
        </Card>

        <Card title="All-Time Earnings">
          <h2>${earnings.total_earnings_dollars.toFixed(2)}</h2>
          <p>Total from all prompts</p>
        </Card>
      </div>

      <h3>Monthly Breakdown</h3>
      <table style={{ width: '100%', marginTop: '16px' }}>
        <thead>
          <tr>
            <th>Month</th>
            <th>Copies</th>
            <th>Earnings</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {earnings.monthly_earnings.map(month => (
            <tr key={month.billing_month}>
              <td>{new Date(month.billing_month).toLocaleDateString()}</td>
              <td>{month.copy_count}</td>
              <td>${month.amount_dollars.toFixed(2)}</td>
              <td>
                <StatusBadge status={month.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {!earnings.is_creator && (
        <CreatorOnboardingPrompt />
      )}
    </div>
  );
}

function CreatorOnboardingPrompt() {
  const handleSetUp = async () => {
    const res = await fetch(`${API_BASE}/v1/creators/me/connect`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });
    const data = await res.json();
    window.location.href = data.onboarding_url;
  };

  return (
    <div style={{
      backgroundColor: '#e7f3ff',
      border: '1px solid #b3d9ff',
      borderRadius: '8px',
      padding: '16px',
      marginTop: '24px'
    }}>
      <h3>Ready to Get Paid?</h3>
      <p>Set up Stripe Connect to receive payouts automatically.</p>
      <button onClick={handleSetUp}>
        Complete Creator Setup
      </button>
    </div>
  );
}
```

---

## 🧪 Testing Checklist

### Before Launch

- [ ] Subscription checkout flow works end-to-end
- [ ] Copy button is disabled without subscription
- [ ] Copy counter updates correctly
- [ ] Subscription status shows up in header
- [ ] Creator dashboard displays earnings
- [ ] Creator can start Stripe Connect flow
- [ ] Stripe test payments work (use 4242 4242 4242 4242)
- [ ] 100-copy limit is enforced
- [ ] Monthly reset works (test with mock dates)
- [ ] Prompt display prevents accidental direct copying

### Error Cases

- [ ] Handle 403 (no subscription) gracefully
- [ ] Handle 409 (already copied) gracefully
- [ ] Handle 429 (copy limit) gracefully
- [ ] Handle network errors
- [ ] Show loading states

---

## 📡 API Reference

### Get Subscription Status

```
GET /v1/subscriptions/me

Headers:
  Authorization: Bearer {token}

Response (200):
{
  "is_subscriber": true,
  "subscription": { ... },
  "copies_remaining": 87
}
```

### Start Checkout

```
POST /v1/subscriptions/checkout

Headers:
  Authorization: Bearer {token}

Response (200):
{
  "sessionId": "cs_test_..."
}
```

### Record Copy

```
POST /v1/flows/{flow_id}/copy

Headers:
  Authorization: Bearer {token}

Response (200):
{
  "id": "copy-uuid",
  "copied_at": "2026-01-15T10:30:00",
  "copies_this_month": 15,
  "copies_remaining": 85,
  "payout_earned": 7
}

Error (403):
{
  "error": "Forbidden",
  "message": "Premium subscription required"
}

Error (409):
{
  "error": "Conflict",
  "message": "You've already copied this flow this month"
}

Error (429):
{
  "error": "Limit Exceeded",
  "message": "You've reached your monthly copy limit (100)"
}
```

### Get Creator Earnings

```
GET /v1/creators/me/earnings

Headers:
  Authorization: Bearer {token}

Response (200):
{
  "user_id": "...",
  "is_creator": true,
  "account_balance_cents": 4207,
  "account_balance_dollars": 42.07,
  "total_earnings_cents": 8914,
  "total_earnings_dollars": 89.14,
  "monthly_earnings": [
    {
      "billing_month": "2026-01-01",
      "copy_count": 42,
      "amount_cents": 294,
      "amount_dollars": 2.94,
      "status": "paid",
      "paid_at": "2026-02-01T12:00:00"
    }
  ]
}
```

### Start Creator Onboarding

```
POST /v1/creators/me/connect

Headers:
  Authorization: Bearer {token}

Response (200):
{
  "onboarding_url": "https://connect.stripe.com/onboarding/..."
}
```

---

## 🔐 Security Notes

1. **Always verify subscription server-side** before allowing copy
   - Frontend check is just for UX
   - Backend always verifies in POST /flows/{flow_id}/copy

2. **Use AuthToken safely**
   - Store in HttpOnly cookie or memory
   - Never expose in localStorage for sensitive ops

3. **HTTPS only in production**
   - Stripe.js requires secure context

4. **Handle errors gracefully**
   - Never expose API error details to users
   - Log errors server-side for debugging

---

## 📊 Prompt Display Options

### Option 1: Styled Container (Recommended)
- Gray background with border
- Monospace font
- Prevents selection
- Has copy button

```tsx
<div className="prompt-display">
  <code>{promptText}</code>
  <CopyButton />
</div>
```

### Option 2: Image Rendering
- Render as SVG/Canvas image
- User cannot select text
- But loses accessibility

```tsx
<Canvas ref={canvasRef} />
<CopyButton />
```

### Option 3: Blur Effect
- Text is blurred until copy
- Requires subscription visible

```tsx
<div className="prompt-display blur">
  <code style={{ filter: 'blur(5px)' }}>
    {promptText}
  </code>
  <CopyButton onClick={() => copy()} />
</div>
```

---

## 🚀 Deployment Checklist

### Before Deploying to Production

- [ ] Update `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` to live key
- [ ] Update `FRONTEND_URL` in backend to production URL
- [ ] Set backend `STRIPE_SECRET_KEY` to live key
- [ ] Set `STRIPE_WEBHOOK_SECRET` to live webhook secret
- [ ] Update Stripe webhook endpoint to production URL
- [ ] Test Stripe live mode with small test amount
- [ ] Set up monitoring and error tracking
- [ ] Prepare creator communication (how to get paid)
- [ ] Test refund flow in live mode

---

**Need help?** Check [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for more details.
