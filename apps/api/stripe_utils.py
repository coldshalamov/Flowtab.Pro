"""
Stripe integration utilities for Flowtab.Pro monetization.

Handles subscription management, webhooks, and payout processing.
"""

import logging
from datetime import datetime
from sqlmodel import Session

import stripe
from apps.api.settings import settings

logger = logging.getLogger(__name__)


class StripeClient:
    def __init__(self):
        self.api_key = settings.stripe_secret_key
        stripe.api_key = self.api_key

    # Seller/Creator Account Management (Stripe Connect)

    def create_account(self, email: str) -> stripe.Account:
        """Create a Stripe Express account for a seller."""
        return stripe.Account.create(
            type="express",
            country="US",
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )

    def create_account_link(self, account_id: str, refresh_url: str, return_url: str) -> stripe.AccountLink:
        """Create an onboarding link for the seller."""
        return stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

    def retrieve_account(self, account_id: str) -> stripe.Account:
        return stripe.Account.retrieve(account_id)

    # Subscription Management

    def create_customer(self, email: str, username: str) -> str:
        """Create a Stripe customer and return customer ID."""
        customer = stripe.Customer.create(
            email=email,
            metadata={"username": username}
        )
        return customer.id

    def get_customer(self, customer_id: str) -> stripe.Customer:
        """Retrieve a customer by ID."""
        return stripe.Customer.retrieve(customer_id)

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe checkout session and return session ID."""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.id

    def cancel_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Cancel a subscription."""
        return stripe.Subscription.delete(subscription_id)

    # Webhook Verification

    def verify_webhook_signature(self, body: bytes, sig_header: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            stripe.Webhook.construct_event(
                body, sig_header, settings.stripe_webhook_secret
            )
            return True
        except ValueError:
            logger.warning("Invalid webhook payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid webhook signature")
            return False

    # Payment Intent (for marketplace purchases)

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        seller_account_id: str,
        platform_fee_cents: int
    ) -> stripe.PaymentIntent:
        """Create a payment intent with split payment (application fee)."""
        return stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            application_fee_amount=platform_fee_cents,
            transfer_data={
                "destination": seller_account_id,
            },
        )

    # Transfers for Creator Payouts

    def create_transfer(
        self,
        amount_cents: int,
        destination_account_id: str,
        description: str
    ) -> stripe.Transfer:
        """Transfer funds to a connected account (creator payout)."""
        return stripe.Transfer.create(
            amount=amount_cents,
            currency="usd",
            destination=destination_account_id,
            description=description,
        )


stripe_client = StripeClient()


# Webhook event handlers

def handle_subscription_event(session: Session, event: dict) -> dict:
    """Handle subscription-related events from Stripe."""
    from apps.api.crud import get_user_by_email, get_subscription_by_stripe_id, create_or_update_subscription

    data = event["data"]["object"]
    event_type = event["type"]

    # Get user from subscription metadata or customer email
    customer_id = data.get("customer")
    customer = stripe_client.get_customer(customer_id)
    user = get_user_by_email(session, customer.email)

    if not user:
        logger.error(
            f"Subscription event for unknown user: {customer.email}"
        )
        return {"status": "error", "message": "User not found"}

    # Handle different subscription events
    if event_type == "customer.subscription.created":
        return handle_subscription_created(session, user, data)
    elif event_type == "customer.subscription.updated":
        return handle_subscription_updated(session, user, data)
    elif event_type == "customer.subscription.deleted":
        return handle_subscription_deleted(session, user, data)

    return {"status": "ok"}


def handle_subscription_created(session: Session, user, data: dict) -> dict:
    """Handle subscription.created event."""
    from apps.api.crud import create_or_update_subscription

    subscription = create_or_update_subscription(
        session=session,
        user_id=user.id,
        stripe_subscription_id=data["id"],
        stripe_customer_id=data["customer"],
        status=data["status"],
        current_period_start=datetime.fromtimestamp(data["current_period_start"]),
        current_period_end=datetime.fromtimestamp(data["current_period_end"]),
        plan_id=data["items"]["data"][0]["price"]["id"],
    )

    # Update user stripe customer ID
    user.stripe_customer_id = data["customer"]
    session.add(user)
    session.commit()

    logger.info(f"Subscription created for user {user.id}: {subscription.id}")
    return {"status": "ok", "subscription_id": subscription.id}


def handle_subscription_updated(session: Session, user, data: dict) -> dict:
    """Handle subscription.updated event."""
    from apps.api.crud import create_or_update_subscription

    subscription = create_or_update_subscription(
        session=session,
        user_id=user.id,
        stripe_subscription_id=data["id"],
        stripe_customer_id=data["customer"],
        status=data["status"],
        current_period_start=datetime.fromtimestamp(data["current_period_start"]),
        current_period_end=datetime.fromtimestamp(data["current_period_end"]),
        plan_id=data["items"]["data"][0]["price"]["id"],
    )

    logger.info(f"Subscription updated for user {user.id}: {subscription.id}")
    return {"status": "ok", "subscription_id": subscription.id}


def handle_subscription_deleted(session: Session, user, data: dict) -> dict:
    """Handle subscription.deleted event (cancellation)."""
    from apps.api.crud import get_subscription_by_stripe_id

    subscription = get_subscription_by_stripe_id(session, data["id"])

    if subscription:
        subscription.status = "canceled"
        subscription.updated_at = datetime.utcnow()
        session.add(subscription)
        session.commit()

        logger.info(f"Subscription canceled for user {user.id}")
        return {"status": "ok", "subscription_id": subscription.id}

    return {"status": "ok"}
