import stripe
from apps.api.settings import settings

class StripeClient:
    def __init__(self):
        self.api_key = settings.stripe_secret_key
        stripe.api_key = self.api_key

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

    def create_payment_intent(self, amount_cents: int, currency: str, seller_account_id: str, platform_fee_cents: int) -> stripe.PaymentIntent:
        """Create a payment intent with split payment (application fee)."""
        return stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            application_fee_amount=platform_fee_cents,
            transfer_data={
                "destination": seller_account_id,
            },
        )

    def retrieve_account(self, account_id: str) -> stripe.Account:
        return stripe.Account.retrieve(account_id)

stripe_client = StripeClient()
