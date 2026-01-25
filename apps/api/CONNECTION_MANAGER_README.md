# Connection Manager & Credential Vault - Implementation Guide

## Overview

Phase 3 implements a secure connection manager for integrating with various AI providers. It includes:

1. **Encryption Service** - AES-256-GCM encryption for credential storage
2. **Provider Seeding** - Pre-configured AI providers (Z.ai, Claude Code, Codex, etc.)
3. **Connection API** - CRUD operations for managing user connections
4. **Security** - Credentials are never returned in API responses

## Architecture

### Models

- `Provider` - AI provider configuration and capabilities
- `AccountConnection` - User's connection to a provider
- `CredentialVaultItem` - Encrypted credential storage
- `ManualOverride` - Manual configuration overrides

### Components

- `encryption.py` - Encryption/decryption service
- `connections_crud.py` - Database operations
- `connections_routes.py` - FastAPI routes
- `seed_providers.py` - Provider seeding script
- `tests/test_encryption.py` - Unit tests for encryption
- `tests/test_connections.py` - Integration tests for API

## Setup

### 1. Install Dependencies

```bash
cd apps/api
pip install -r requirements.txt
```

The `cryptography` package is now included.

### 2. Configure Encryption Key

Add to `.env`:
```bash
ENCRYPTION_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

**Important**: Generate a secure random key for production:
```python
import secrets
key = secrets.token_hex(32)  # 64 hex characters
print(key)
```

### 3. Seed Providers

```bash
python seed_providers.py
```

This will populate the database with:
- Z.ai
- Claude Code
- OpenAI Codex
- Moonshot Kimi
- MiniMax
- GitHub Copilot
- Grok
- Google Gemini
- Google Antigravity

## API Endpoints

### Providers

#### List Providers
```http
GET /v1/connections/providers
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "id": "uuid",
    "name": "zai",
    "slug": "zai",
    "display_name": "Z.ai",
    "description": "...",
    "auth_type": "api_key",
    "supports_api_key": true,
    "supports_oauth": false,
    "supports_manual": true,
    "rate_limit_per_minute": 100,
    "rate_limit_per_hour": 5000,
    "is_active": true
  }
]
```

### Connections

#### List Connections
```http
GET /v1/connections
Authorization: Bearer <token>
```

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "provider_id": "uuid",
      "label": "My Z.ai Connection",
      "connection_type": "api_key",
      "status": "active",
      "last_used_at": "2024-01-24T12:00:00",
      "last_error": null,
      "created_at": "2024-01-24T12:00:00",
      "updated_at": "2024-01-24T12:00:00",
      "provider": { ... }
    }
  ]
}
```

#### Create Connection
```http
POST /v1/connections
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider_id": "uuid",
  "label": "My Connection",
  "connection_type": "api_key",
  "credentials": {
    "api_key": "sk-..."
  },
  "manual_config": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}
```

#### Get Connection
```http
GET /v1/connections/{connection_id}
Authorization: Bearer <token>
```

#### Delete Connection
```http
DELETE /v1/connections/{connection_id}
Authorization: Bearer <token>
```

## Security Features

### Encryption

- **Algorithm**: AES-256-GCM (authenticated encryption)
- **Key**: 32 bytes (256 bits) from hex-encoded environment variable
- **IV**: 12 bytes randomly generated per encryption
- **Auth Tag**: 16 bytes for message authentication
- **Format**: `iv:auth_tag:encrypted_content` (hex-encoded)

### Credential Storage

1. Credentials are encrypted before storage
2. Encrypted format includes IV and auth tag
3. Credentials are never returned in API responses
4. Each credential is stored separately in `CredentialVaultItem`
5. Key name is stored in plaintext for identification

### Access Control

- All endpoints require authentication
- Users can only access their own connections
- Connections are filtered by `user_id`
- Provider IDs are validated

## Testing

### Unit Tests

```bash
pytest tests/test_encryption.py -v
```

Tests cover:
- Basic encryption/decryption
- Special characters and unicode
- Encryption format validation
- Uniqueness of ciphertexts
- Invalid key handling
- Tampered data detection
- Empty and long strings

### Integration Tests

```bash
pytest tests/test_connections.py -v
```

Tests cover:
- Provider listing
- Connection CRUD operations
- Credential encryption in database
- Credential decryption verification
- Authentication requirements
- Error handling

## Usage Examples

### Creating an API Key Connection

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/connections",
    json={
        "provider_id": provider_id,
        "label": "My Z.ai Connection",
        "connection_type": "api_key",
        "credentials": {
            "api_key": "sk-your-api-key-here"
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

### Creating a Manual Configuration

```python
response = httpx.post(
    "http://localhost:8000/v1/connections",
    json={
        "provider_id": provider_id,
        "label": "Custom Config",
        "connection_type": "manual",
        "manual_config": {
            "model": "gpt-4-turbo",
            "temperature": 0.8,
            "max_tokens": 4000
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## Database Schema

### providers
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | string | Provider name |
| slug | string | URL-friendly identifier |
| display_name | string | Display name |
| auth_type | string | api_key, oauth, manual |
| supports_api_key | boolean | API key support |
| supports_oauth | boolean | OAuth support |
| supports_manual | boolean | Manual config support |
| api_endpoint | string | API endpoint URL |
| rate_limit_per_minute | int | Rate limit |
| rate_limit_per_hour | int | Rate limit |
| is_active | boolean | Active status |

### account_connections
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | User FK |
| provider_id | UUID | Provider FK |
| label | string | User-defined label |
| connection_type | string | api_key, oauth, manual |
| status | string | active, inactive, error |
| last_used_at | timestamp | Last usage |
| last_error | string | Last error message |

### credential_vault_items
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| connection_id | UUID | Connection FK |
| encrypted_data | string | Encrypted credential |
| key_name | string | Credential key name |

### manual_overrides
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| connection_id | UUID | Connection FK |
| config | JSON | Manual configuration |

## Best Practices

### Production Deployment

1. **Generate a secure encryption key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Store key in environment variables**, never in code

3. **Rotate keys periodically** (requires migration of encrypted data)

4. **Enable HTTPS** to protect tokens in transit

5. **Use database encryption at rest** for additional security

### Error Handling

- Invalid encrypted format: Returns `400 Bad Request`
- Provider not found: Returns `400 Bad Request`
- Unsupported connection type: Returns `400 Bad Request`
- Connection not found: Returns `404 Not Found`
- Unauthorized: Returns `401 Unauthorized`

## Future Enhancements

- [ ] OAuth flow integration
- [ ] Connection testing/validation endpoint
- [ ] Usage analytics dashboard
- [ ] Key rotation support
- [ ] Multi-factor authentication for sensitive operations
- [ ] Audit logging for credential access

## Troubleshooting

### Encryption Key Error

```
ValueError: Encryption key must be 32 bytes (64 hex chars)
```

Solution: Ensure `ENCRYPTION_KEY` in `.env` is exactly 64 hex characters.

### Decryption Failed

```
ValueError: Decryption failed: ...
```

Possible causes:
- Encrypted data was tampered with
- Wrong encryption key
- Corrupted database

Solution: Check encryption key configuration and database integrity.

### Provider Not Found

```
ValueError: Provider not found: uuid
```

Solution: Run `python seed_providers.py` to populate providers table.
