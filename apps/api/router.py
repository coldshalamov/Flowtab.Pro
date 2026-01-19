"""
API router for the Flowtab.Pro backend API.

This module defines all API endpoints for the prompts API.
"""

import base64
import hashlib
import logging
import time
import urllib.parse
from typing import Literal

from fastapi import APIRouter, Depends, Query, Header, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlmodel import Session, select

from apps.api.schemas import (
    PromptCreate,
    PromptUpdate,
    PromptRead,
    PromptListResponse,
    CommentCreate,
    CommentRead,
    CommentListResponse,
    LikeStatusResponse,
    TagsResponse,
    UserCreate,
    UserRead,
    Token,
    OAuthExchangeRequest,
    OAuthStartResponse,
)
from apps.api.crud import (
    get_prompt_by_slug,
    get_prompts,
    get_all_tags,
    create_prompt,
    update_prompt,
    delete_prompt,
    get_user_by_email,
    get_user_by_username,
    get_user_by_email_or_username,
    create_user,
    get_comments_for_prompt,
    create_comment,
    get_comment_by_id,
    delete_comment,
    like_target,
    unlike_target,
)
from apps.api.settings import settings
from apps.api.db import get_session
from apps.api.utils import (
    error_response,
    validation_error_response,
    format_pydantic_validation_error,
)
from apps.api.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
    get_current_superuser,
)
import os
import secrets

import httpx

from apps.api.models import User, OAuthAccount, Prompt, Comment
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

logger = logging.getLogger(__name__)

# Create API router with prefix and tags
router = APIRouter(prefix="/v1", tags=["prompts"])


@router.post("/users/promote", status_code=status.HTTP_200_OK, tags=["users"])
def promote_user_to_superuser(
    email: str,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    session: Session = Depends(get_session),
):
    """
    Promote a user to superuser.
    Requires X-Admin-Key header (bootstrapping).
    """
    if x_admin_key != settings.admin_key:
        if not settings.admin_key:
            return error_response(
                error="Forbidden",
                message="Admin key not configured on server",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return error_response(
            error="Unauthorized",
            message="Invalid or missing X-Admin-Key header",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = get_user_by_email(session, email=email)
    if not user:
        return error_response(
            error="Not found",
            message=f"User with email '{email}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    user.is_superuser = True
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": f"User {email} is now a superuser"}


@router.post(
    "/auth/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def register(
    user_in: UserCreate,
    session: Session = Depends(get_session),
):
    """
    Register a new user.
    """
    user = get_user_by_email(session, email=user_in.email)
    if user:
        return error_response(
            error="Conflict",
            message="User with this email already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    hashed_password = get_password_hash(user_in.password)
    # Check if username is taken
    if get_user_by_username(session, username=user_in.username):
        return error_response(
            error="Conflict",
            message="Username is already taken",
            status_code=status.HTTP_409_CONFLICT,
        )
    user = create_user(session, user_create=user_in, hashed_password=hashed_password)
    return user


@router.post("/auth/token", response_model=Token, tags=["auth"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Supports login via email or username.
    """
    user = get_user_by_email_or_username(session, login=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        return error_response(
            error="Unauthorized",
            message="Incorrect email or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def _is_testing() -> bool:
    return os.getenv("TESTING") == "true"


def _require_oauth_config(provider: str) -> tuple[str, str] | JSONResponse:
    """Return (client_id, client_secret) for provider, or JSONResponse on error."""

    def err(name: str) -> JSONResponse:
        return error_response(
            error="Server misconfigured",
            message=f"OAuth provider '{provider}' not configured: missing {name}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if provider == "google":
        if not settings.google_client_id and not _is_testing():
            return err("GOOGLE_CLIENT_ID")
        if not settings.google_client_secret and not _is_testing():
            return err("GOOGLE_CLIENT_SECRET")
        return (
            settings.google_client_id or "test-google-client-id",
            settings.google_client_secret or "test-google-client-secret",
        )

    if provider == "github":
        if not settings.github_client_id and not _is_testing():
            return err("GITHUB_CLIENT_ID")
        if not settings.github_client_secret and not _is_testing():
            return err("GITHUB_CLIENT_SECRET")
        return (
            settings.github_client_id or "test-github-client-id",
            settings.github_client_secret or "test-github-client-secret",
        )

    if provider == "facebook":
        if not settings.facebook_client_id and not _is_testing():
            return err("FACEBOOK_CLIENT_ID")
        if not settings.facebook_client_secret and not _is_testing():
            return err("FACEBOOK_CLIENT_SECRET")
        return (
            settings.facebook_client_id or "test-facebook-client-id",
            settings.facebook_client_secret or "test-facebook-client-secret",
        )

    return err("unknown-provider")


_OAUTH_STATE_TTL_SECONDS = 5 * 60
_OAUTH_STATE: dict[str, dict[str, str | float]] = {}

# Best-effort in-memory rate limiting (dev/test only). For production, move
# this to a shared store (Redis) so it works across multiple workers.
_RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}


def _rate_limit(key: str, *, limit: int, window_seconds: int) -> JSONResponse | None:
    now = time.time()
    bucket = _RATE_LIMIT_BUCKETS.setdefault(key, [])
    bucket[:] = [ts for ts in bucket if now - ts < window_seconds]

    if len(bucket) >= limit:
        return error_response(
            error="Too many requests",
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    bucket.append(now)
    return None


def _create_random_password_hash() -> str:
    # OAuth users don't use local password login; set a random password hash.
    return get_password_hash(secrets.token_urlsafe(32)[:48])


def _validate_redirect_uri(redirect_uri: str) -> JSONResponse | None:
    if redirect_uri not in settings.oauth_redirect_allowlist_list:
        return error_response(
            error="Bad request",
            message="redirect_uri is not allowed",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return None


def _pkce_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _oauth_state_put(
    *, state: str, provider: str, redirect_uri: str, code_verifier: str
) -> None:
    _OAUTH_STATE[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "created_at": time.time(),
    }


def _oauth_state_pop(*, state: str) -> dict[str, str | float] | None:
    item = _OAUTH_STATE.pop(state, None)
    if not item:
        return None
    created_at = float(item.get("created_at", 0))
    if time.time() - created_at > _OAUTH_STATE_TTL_SECONDS:
        return None
    return item


def _oauth_authorize_url(
    provider: str, client_id: str, redirect_uri: str, state: str, code_challenge: str
) -> str:
    if provider == "google":
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent",
        }
    elif provider == "github":
        base = "https://github.com/login/oauth/authorize"
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    else:  # facebook
        base = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "email",
            "state": state,
        }

    return f"{base}?{urllib.parse.urlencode(params)}"


@router.post(
    "/auth/oauth/{provider}/start",
    response_model=OAuthStartResponse,
    tags=["auth"],
)
def oauth_start(provider: str, redirect_uri: str) -> OAuthStartResponse | JSONResponse:
    provider = provider.lower()
    if provider not in {"google", "github", "facebook"}:
        return error_response(
            error="Bad request",
            message=f"Unsupported OAuth provider '{provider}'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    redirect_err = _validate_redirect_uri(redirect_uri)
    if redirect_err:
        return redirect_err

    config = _require_oauth_config(provider)
    if isinstance(config, JSONResponse):
        return config
    client_id, _client_secret = config

    state = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(48)
    code_challenge = _pkce_code_challenge(code_verifier)

    _oauth_state_put(
        state=state,
        provider=provider,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )

    authorize_url = _oauth_authorize_url(
        provider=provider,
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state,
        code_challenge=code_challenge,
    )

    return OAuthStartResponse(
        authorize_url=authorize_url,
        state=state,
        code_verifier=code_verifier,
        code_challenge=code_challenge,
    )


def _validate_oauth_state(
    provider: str, payload: OAuthExchangeRequest
) -> JSONResponse | None:
    redirect_err = _validate_redirect_uri(payload.redirect_uri)
    if redirect_err:
        return redirect_err

    state_entry = _oauth_state_pop(state=payload.state)
    if not state_entry:
        return error_response(
            error="Unauthorized",
            message="Invalid or expired OAuth state",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if state_entry.get("provider") != provider:
        return error_response(
            error="Unauthorized",
            message="OAuth state/provider mismatch",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if state_entry.get("redirect_uri") != payload.redirect_uri:
        return error_response(
            error="Unauthorized",
            message="OAuth state/redirect_uri mismatch",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if state_entry.get("code_verifier") != payload.code_verifier:
        return error_response(
            error="Unauthorized",
            message="Invalid OAuth code_verifier",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return None


def _oauth_fetch_profile(
    *,
    provider: str,
    payload: OAuthExchangeRequest,
    client_id: str,
    client_secret: str,
) -> tuple[str, str, str | None] | JSONResponse:
    """Return (provider_user_id, email, name) or JSONResponse on error."""

    try:
        if provider == "google":
            token_resp = httpx.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": payload.code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": payload.redirect_uri,
                    "grant_type": "authorization_code",
                    "code_verifier": payload.code_verifier,
                },
                timeout=10,
            )
            if token_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            access_token = token_resp.json().get("access_token")
            if not access_token:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange did not return access_token",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            userinfo_resp = httpx.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            if userinfo_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth userinfo fetch failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            userinfo = userinfo_resp.json()
            provider_user_id = userinfo.get("sub")
            email = userinfo.get("email")
            name = userinfo.get("name")

        elif provider == "github":
            token_resp = httpx.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": payload.code,
                    "redirect_uri": payload.redirect_uri,
                    "code_verifier": payload.code_verifier,
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if token_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            access_token = token_resp.json().get("access_token")
            if not access_token:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange did not return access_token",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            user_resp = httpx.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            if user_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth user fetch failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            userinfo = user_resp.json()
            provider_user_id = str(userinfo.get("id"))
            name = userinfo.get("name") or userinfo.get("login")

            # Prefer verified email from /user/emails.
            emails_resp = httpx.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            email = None
            if emails_resp.status_code == 200:
                emails = emails_resp.json() or []
                primary = next(
                    (e for e in emails if e.get("primary") and e.get("verified")),
                    None,
                )
                if not primary:
                    primary = next((e for e in emails if e.get("verified")), None)
                if primary:
                    email = primary.get("email")

        else:  # facebook
            token_resp = httpx.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": payload.redirect_uri,
                    "code": payload.code,
                },
                timeout=10,
            )
            if token_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            access_token = token_resp.json().get("access_token")
            if not access_token:
                return error_response(
                    error="Unauthorized",
                    message="OAuth token exchange did not return access_token",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            user_resp = httpx.get(
                "https://graph.facebook.com/me",
                params={"fields": "id,name,email", "access_token": access_token},
                timeout=10,
            )
            if user_resp.status_code != 200:
                return error_response(
                    error="Unauthorized",
                    message="OAuth user fetch failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            userinfo = user_resp.json()
            provider_user_id = userinfo.get("id")
            name = userinfo.get("name")
            email = userinfo.get("email")

        if not provider_user_id:
            return error_response(
                error="Unauthorized",
                message="OAuth profile missing provider user id",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not email:
            return error_response(
                error="Unauthorized",
                message="OAuth profile missing email",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return (str(provider_user_id), str(email), name)

    except httpx.TimeoutException:
        return error_response(
            error="Bad gateway",
            message="OAuth provider timed out",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except httpx.RequestError:
        return error_response(
            error="Bad gateway",
            message="OAuth provider request failed",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception:
        logger.exception("Unhandled error in OAuth provider flow (%s)", provider)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/auth/oauth/{provider}/exchange",
    response_model=Token,
    tags=["auth"],
)
def oauth_exchange_code(
    provider: str,
    payload: OAuthExchangeRequest,
    session: Session = Depends(get_session),
) -> Token | JSONResponse:
    """Exchange an OAuth authorization code for a Flowtab JWT.

    Security:
    - Validates `state` and `redirect_uri` against a server-side allowlist.
    - Does NOT auto-link to an existing email/password user (prevents account takeover).
    """

    provider = provider.lower()
    if provider not in {"google", "github", "facebook"}:
        return error_response(
            error="Bad request",
            message=f"Unsupported OAuth provider '{provider}'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    state_err = _validate_oauth_state(provider, payload)
    if state_err:
        return state_err

    config = _require_oauth_config(provider)
    if isinstance(config, JSONResponse):
        return config
    client_id, client_secret = config

    profile = _oauth_fetch_profile(
        provider=provider,
        payload=payload,
        client_id=client_id,
        client_secret=client_secret,
    )
    if isinstance(profile, JSONResponse):
        return profile
    provider_user_id, email, name = profile

    existing_account = session.exec(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
    ).first()

    user = None
    if existing_account:
        user = session.exec(
            select(User).where(User.id == existing_account.user_id)
        ).first()
        if user is None:
            # Dangling account; treat as missing.
            existing_account = None

    if not existing_account:
        # Prevent account takeover by email collision: do not link unless user explicitly links.
        user_by_email = session.exec(select(User).where(User.email == email)).first()
        if user_by_email:
            return error_response(
                error="Conflict",
                message="An account with this email already exists. Log in and link this provider.",
                status_code=status.HTTP_409_CONFLICT,
            )

        # Generate a username from email for OAuth users
        username_base = email.split("@")[0]
        username = username_base
        counter = 1
        while get_user_by_username(session, username=username):
            username = f"{username_base}{counter}"
            counter += 1

        user = User(
            email=email,
            username=username,
            hashed_password=_create_random_password_hash(),
            is_active=True,
            is_superuser=False,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
        )
        session.add(account)
        session.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    jwt_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.post(
    "/auth/oauth/{provider}/link",
    tags=["auth"],
    response_model=None,
)
def oauth_link_provider(
    provider: str,
    payload: OAuthExchangeRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Link an OAuth provider to an existing authenticated user."""

    provider = provider.lower()
    if provider not in {"google", "github", "facebook"}:
        return error_response(
            error="Bad request",
            message=f"Unsupported OAuth provider '{provider}'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    state_err = _validate_oauth_state(provider, payload)
    if state_err:
        return state_err

    config = _require_oauth_config(provider)
    if isinstance(config, JSONResponse):
        return config
    client_id, client_secret = config

    profile = _oauth_fetch_profile(
        provider=provider,
        payload=payload,
        client_id=client_id,
        client_secret=client_secret,
    )
    if isinstance(profile, JSONResponse):
        return profile
    provider_user_id, email, name = profile

    if email.lower() != current_user.email.lower():
        return error_response(
            error="Conflict",
            message="OAuth email does not match current user",
            status_code=status.HTTP_409_CONFLICT,
        )

    existing_account = session.exec(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
    ).first()

    if existing_account and existing_account.user_id != current_user.id:
        return error_response(
            error="Conflict",
            message="This OAuth account is already linked to another user",
            status_code=status.HTTP_409_CONFLICT,
        )

    if not existing_account:
        account = OAuthAccount(
            user_id=current_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
        )
        session.add(account)
        session.commit()

    return {"message": "linked"}


@router.get("/users/me", response_model=UserRead, tags=["users"])
def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user


@router.get(
    "/prompts", response_model=PromptListResponse, status_code=status.HTTP_200_OK
)
def list_prompts(
    q: str | None = Query(default=None, description="Search query for text search"),
    tags: str | None = Query(
        default=None, description="Comma-separated list of tags to filter by"
    ),

    worksWith: str | None = Query(
        default=None, description="Comma-separated list of tools to filter by"
    ),
    type: Literal["prompt", "discussion"] | None = Query(
        default=None, description="Type of content"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(
        default=20, ge=1, le=100, description="Number of items per page"
    ),
    session: Session = Depends(get_session),
) -> PromptListResponse | JSONResponse:
    """
    List all prompts with optional filtering, search, and pagination.

    Query parameters:
    - q: Search query for text search across title, summary, and promptText
    - tags: Comma-separated list of tags to filter by (AND logic)
    - difficulty: Difficulty level to filter by (beginner, intermediate, advanced)
    - worksWith: Comma-separated list of tools to filter by (OR logic)
    - page: Page number (default: 1)
    - pageSize: Number of items per page (default: 20, max: 100)
    """
    try:
        # Parse comma-separated parameters into lists
        tags_list = tags.split(",") if tags else None
        works_with_list = worksWith.split(",") if worksWith else None

        # Calculate skip for pagination
        skip = (page - 1) * pageSize

        # Call get_prompts with filters
        prompts, total = get_prompts(
            session=session,
            skip=skip,
            limit=pageSize,
            q=q,
            tags=tags_list,
            type_=type,
            worksWith=works_with_list,
        )

        # Return PromptListResponse
        return PromptListResponse(
            items=prompts,
            page=page,
            pageSize=pageSize,
            total=total,
        )

    except Exception:
        logger.exception("Unhandled error in GET /v1/prompts")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get(
    "/prompts/{slug}", response_model=PromptRead, status_code=status.HTTP_200_OK
)
def get_prompt(
    slug: str, session: Session = Depends(get_session)
) -> PromptRead | JSONResponse:
    """
    Get a single prompt by slug.

    Path parameter:
    - slug: URL-friendly unique identifier of the prompt

    Returns the prompt if found, raises 404 if not found.
    """
    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)

        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return prompt

    except Exception:
        logger.exception("Unhandled error in GET /v1/prompts/{slug} (slug=%s)", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/tags", response_model=TagsResponse, status_code=status.HTTP_200_OK)
def list_tags(session: Session = Depends(get_session)) -> TagsResponse | JSONResponse:
    """
    Get all available tags.

    Returns a list of all unique tags across all prompts.
    """
    try:
        tags = get_all_tags(session=session)
        return TagsResponse(items=tags)

    except Exception:
        logger.exception("Unhandled error in GET /v1/tags")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/prompts", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
def create_new_prompt(
    prompt: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> PromptRead | JSONResponse:
    """
    Create a new prompt.

    Request body: PromptCreate schema with all required fields

    Requires authentication.
    """
    try:
        new_prompt = create_prompt(
            session=session, prompt_create=prompt, author_id=current_user.id
        )
        return new_prompt

    except PydanticValidationError as e:
        return validation_error_response(
            message="Request body validation failed",
            details=format_pydantic_validation_error(e),
        )
    except Exception:
        logger.exception("Unhandled error in POST /v1/prompts")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get(
    "/prompts/{slug}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    tags=["comments"],
)
def list_prompt_comments(
    slug: str,
    session: Session = Depends(get_session),
) -> CommentListResponse | JSONResponse:
    """List all comments for a prompt (public)."""

    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)
        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        comments = get_comments_for_prompt(session=session, prompt_id=prompt.id)
        return CommentListResponse(items=comments)

    except Exception:
        logger.exception("Unhandled error in GET /v1/prompts/%s/comments", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/prompts/{slug}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
)
def create_prompt_comment(
    slug: str,
    payload: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> CommentRead | JSONResponse:
    """Create a new comment for a prompt (authenticated)."""

    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)
        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        limiter = _rate_limit(
            f"comment:create:{current_user.id}",
            limit=10,
            window_seconds=60,
        )
        if limiter:
            return limiter

        comment = create_comment(
            session=session,
            prompt_id=prompt.id,
            author_id=current_user.id,
            body=payload.body,
        )
        return comment

    except Exception:
        logger.exception("Unhandled error in POST /v1/prompts/%s/comments", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put(
    "/prompts/{slug}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
    tags=["likes"],
)
def like_prompt(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Idempotently like a prompt (flow)."""

    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)
        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        limiter = _rate_limit(
            f"like:prompt:{current_user.id}",
            limit=60,
            window_seconds=60,
        )
        if limiter:
            return limiter

        created = like_target(
            session=session,
            user_id=current_user.id,
            target_type="prompt",
            target_id=prompt.id,
        )

        if created:
            prompt.like_count = (prompt.like_count or 0) + 1
            session.add(prompt)
            session.commit()

        session.refresh(prompt)
        return LikeStatusResponse(liked=True, likeCount=prompt.like_count)

    except Exception:
        logger.exception("Unhandled error in PUT /v1/prompts/%s/like", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete(
    "/prompts/{slug}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
    tags=["likes"],
)
def unlike_prompt(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Idempotently unlike a prompt (flow)."""

    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)
        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        limiter = _rate_limit(
            f"unlike:prompt:{current_user.id}",
            limit=60,
            window_seconds=60,
        )
        if limiter:
            return limiter

        deleted = unlike_target(
            session=session,
            user_id=current_user.id,
            target_type="prompt",
            target_id=prompt.id,
        )

        if deleted and (prompt.like_count or 0) > 0:
            prompt.like_count = prompt.like_count - 1
            session.add(prompt)
            session.commit()

        session.refresh(prompt)
        return LikeStatusResponse(liked=False, likeCount=prompt.like_count)

    except Exception:
        logger.exception("Unhandled error in DELETE /v1/prompts/%s/like", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put(
    "/comments/{comment_id}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
    tags=["likes"],
)
def like_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Idempotently like a comment."""

    try:
        comment = get_comment_by_id(session=session, comment_id=comment_id)
        if comment is None:
            return error_response(
                error="Not found",
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        limiter = _rate_limit(
            f"like:comment:{current_user.id}",
            limit=120,
            window_seconds=60,
        )
        if limiter:
            return limiter

        created = like_target(
            session=session,
            user_id=current_user.id,
            target_type="comment",
            target_id=comment.id,
        )

        if created:
            comment.like_count = (comment.like_count or 0) + 1
            session.add(comment)
            session.commit()

        session.refresh(comment)
        return LikeStatusResponse(liked=True, likeCount=comment.like_count)

    except Exception:
        logger.exception("Unhandled error in PUT /v1/comments/%s/like", comment_id)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete(
    "/comments/{comment_id}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
    tags=["likes"],
)
def unlike_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Idempotently unlike a comment."""

    try:
        comment = get_comment_by_id(session=session, comment_id=comment_id)
        if comment is None:
            return error_response(
                error="Not found",
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        limiter = _rate_limit(
            f"unlike:comment:{current_user.id}",
            limit=120,
            window_seconds=60,
        )
        if limiter:
            return limiter

        deleted = unlike_target(
            session=session,
            user_id=current_user.id,
            target_type="comment",
            target_id=comment.id,
        )

        if deleted and (comment.like_count or 0) > 0:
            comment.like_count = comment.like_count - 1
            session.add(comment)
            session.commit()

        session.refresh(comment)
        return LikeStatusResponse(liked=False, likeCount=comment.like_count)

    except Exception:
        logger.exception("Unhandled error in DELETE /v1/comments/%s/like", comment_id)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    tags=["comments"],
)
def delete_comment_by_id(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Response | JSONResponse:
    """Delete a comment if you are its author (or a superuser)."""

    try:
        comment = get_comment_by_id(session=session, comment_id=comment_id)
        if comment is None:
            return error_response(
                error="Not found",
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if comment.author_id != current_user.id and not current_user.is_superuser:
            return error_response(
                error="Forbidden",
                message="You do not have permission to delete this comment",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        limiter = _rate_limit(
            f"comment:delete:{current_user.id}",
            limit=30,
            window_seconds=60,
        )
        if limiter:
            return limiter

        delete_comment(session=session, comment=comment)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception:
        logger.exception("Unhandled error in DELETE /v1/comments/%s", comment_id)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete(
    "/prompts/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
def delete_existing_prompt(
    slug: str,
    current_user: User = Depends(get_current_superuser),
    session: Session = Depends(get_session),
) -> Response | JSONResponse:
    """
    Delete a prompt by slug.

    Requires Superuser privileges.

    Returns 204 No Content on success.
    """
    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)

        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        delete_prompt(session=session, prompt=prompt)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception:
        logger.exception("Unhandled error in DELETE /v1/prompts/{slug}")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
@router.patch(
    "/prompts/{slug}",
    response_model=PromptRead,
    status_code=status.HTTP_200_OK,
)
def patch_existing_prompt(
    slug: str,
    prompt_update: PromptUpdate,
    current_user: User = Depends(get_current_superuser),
    session: Session = Depends(get_session),
) -> PromptRead | JSONResponse:
    """
    Update an existing prompt by slug.

    Requires Superuser privileges.

    Returns the updated prompt.
    """
    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)

        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        updated_prompt = update_prompt(
            session=session, prompt=prompt, prompt_update=prompt_update
        )
        return updated_prompt

    except Exception:
        logger.exception("Unhandled error in PATCH /v1/prompts/{slug}")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put(
    "/prompts/{slug}/save",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
)
def save_prompt_endpoint(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Bookmark (save) a prompt."""
    prompt = get_prompt_by_slug(session=session, slug=slug)
    if not prompt:
        return error_response(
            error="Not found",
            message=f"Prompt '{slug}' not found",
            status_code=404,
        )

    # Use 'save_prompt' from crud (ensure it is imported)
    from apps.api.crud import save_prompt as crud_save_prompt
    
    was_saved = crud_save_prompt(session=session, user_id=current_user.id, prompt_id=prompt.id)
    if was_saved:
        prompt.saves_count += 1
        session.add(prompt)
        session.commit()
    
    return {"liked": True, "likeCount": prompt.saves_count}


@router.delete(
    "/prompts/{slug}/save",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
)
def unsave_prompt_endpoint(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> LikeStatusResponse | JSONResponse:
    """Remove bookmark (unsave) from a prompt."""
    prompt = get_prompt_by_slug(session=session, slug=slug)
    if not prompt:
        return error_response(
            error="Not found",
            message=f"Prompt '{slug}' not found",
            status_code=404,
        )
        
    from apps.api.crud import unsave_prompt as crud_unsave_prompt
    
    was_unsaved = crud_unsave_prompt(session=session, user_id=current_user.id, prompt_id=prompt.id)
    if was_unsaved:
        prompt.saves_count = max(0, prompt.saves_count - 1)
        session.add(prompt)
        session.commit()
    
    return {"liked": False, "likeCount": prompt.saves_count}


# --- Stripe / Marketplace Endpoints ---

@router.post("/stripe/connect", tags=["marketplace"])
def connect_stripe_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict | JSONResponse:
    """Create a Stripe Express account for the user and return onboarding link."""
    if not settings.stripe_secret_key:
         return error_response(
            error="Server misconfigured",
            message="Stripe is not configured on this server.",
            status_code=500
        )

    from apps.api.stripe_utils import stripe_client
    
    # Create account if doesn't exist
    if not current_user.stripe_connect_id:
        try:
            account = stripe_client.create_account(current_user.email)
            current_user.stripe_connect_id = account.id
            session.add(current_user)
            session.commit()
            session.refresh(current_user)
        except Exception as e:
            return error_response(error="Stripe Error", message=str(e), status_code=500)
    
    # Generate link
    try:
        # TODO: Update return URLs to real frontend routes
        link = stripe_client.create_account_link(
            account_id=current_user.stripe_connect_id,
            refresh_url=f"{settings.cors_origins_list[0]}/settings?stripe=refresh",
            return_url=f"{settings.cors_origins_list[0]}/settings?stripe=return",
        )
        return {"url": link.url}
    except Exception as e:
            return error_response(error="Stripe Error", message=str(e), status_code=500)

@router.post("/prompts/{slug}/buy", tags=["marketplace"])
def buy_prompt(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict | JSONResponse:
    """Create a payment intent to purchase a prompt."""
    if not settings.stripe_secret_key:
         return error_response(
            error="Server misconfigured",
            message="Stripe is not configured on this server.",
            status_code=500
        )
        
    prompt = get_prompt_by_slug(session=session, slug=slug)
    if not prompt:
        return error_response(error="Not found", message="Prompt not found", status_code=404)
        
    if prompt.price <= 0:
        return error_response(error="Bad Request", message="This prompt is free.", status_code=400)
        
    seller = session.get(User, prompt.author_id)
    if not seller or not seller.stripe_connect_id:
         return error_response(error="d", message="Seller not setup for payments.", status_code=400)
         
    # Check if already purchased
    # existing = session.exec(select(Purchase).where(Purchase.buyer_id == current_user.id, Purchase.prompt_id == prompt.id)).first()
    # if existing: ... (Optional: allow re-purchase or block)

    # Calculate 10% fee
    platform_fee = int(prompt.price * 0.10)
    
    from apps.api.stripe_utils import stripe_client
    try:
        intent = stripe_client.create_payment_intent(
            amount_cents=prompt.price,
            currency=prompt.currency,
            seller_account_id=seller.stripe_connect_id,
            platform_fee_cents=platform_fee
        )
        
        # Record pending purchase? Or wait for webhook?
        # Typically we wait for webhook, but we can store intent ID to verify later.
        
        return {
            "clientSecret": intent.client_secret,
            "publishableKey": "pk_test_placeholder", # TODO: Add to settings if needed
            "amount": prompt.price,
            "currency": prompt.currency
        }
    except Exception as e:
        return error_response(error="Stripe Error", message=str(e), status_code=500)
