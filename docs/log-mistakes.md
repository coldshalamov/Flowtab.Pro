# Mistake Log

## 2026-01-18
- Tried running `pytest` directly; it wasn't available on PATH in this environment. Fixed by using `python -m pytest`.
- Tests initially failed to import the API due to FastAPI asserting that `204` responses must not have a response body. Fixed by ensuring the delete endpoint returns an empty `Response` and explicitly setting `response_model=None`.
- User registration tests hit a bcrypt backend incompatibility on Python 3.13 (passlib + bcrypt 5.x wrap-bug detection path). Fixed by pinning `bcrypt==4.1.3`.
- Introduced a syntax error while adding PKCE to the GitHub token exchange call (missing comma). Fixed immediately.
- Added an OAuth link endpoint without setting a response model; FastAPI rejected the union return type. Fixed by disabling response model inference for that route.
