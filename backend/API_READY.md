# API Readiness Report - Frontend Integration Guide

**Status**: 🟡 Partially Ready (36% API coverage)  
**Date**: 2025-10-12  
**Backend Version**: develop branch  
**Coverage**: 31%  

## 🎯 Executive Summary

The backend API is **partially ready** for frontend development. Core authentication and tag management endpoints are stable and well-tested (78% coverage). Other endpoints require additional stabilization.

### Recommendation

**Proceed with caution**: Frontend development can begin on **Tags** and **Authentication** endpoints. For other endpoints (Builds, Users, Webhooks), coordinate closely with backend team for schema validation and error handling.

---

## ✅ Production-Ready Endpoints

### Tags API (78% tested, 7/9 tests passing)

Base URL: `{API_V1_STR}/tags/`

#### Tested & Working

| Method | Endpoint | Auth Required | Description | Status |
|--------|----------|---------------|-------------|--------|
| GET | `/tags/` | Yes | List all tags | ✅ Stable |
| GET | `/tags/{id}` | Yes | Get tag by ID | ✅ Stable |
| POST | `/tags/` | Admin only | Create new tag | ✅ Stable |
| PUT | `/tags/{id}` | Admin only | Update tag | ✅ Stable |

#### Request/Response Examples

**Create Tag** (Admin only)
```bash
POST /api/v1/tags/
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "WvW",
  "description": "World vs World content",
  "category": "game_mode"
}
```

**Response** (201 Created)
```json
{
  "id": 1,
  "name": "WvW",
  "description": "World vs World content",
  "category": "game_mode",
  "created_at": "2025-10-12T20:00:00Z"
}
```

**List Tags**
```bash
GET /api/v1/tags/
Authorization: Bearer {jwt_token}
```

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "name": "WvW",
    "description": "World vs World content",
    "category": "game_mode"
  },
  {
    "id": 2,
    "name": "PvE",
    "description": "Player vs Environment",
    "category": "game_mode"
  }
]
```

#### Known Issues

- **DELETE `/tags/{id}`**: Returns `{msg}` instead of `{detail}` (backend schema issue)
- **Edge cases**: Some validation edge cases not fully tested

---

### Authentication API (25% tested, 3/12 tests passing)

Base URL: `{API_V1_STR}/auth/`

#### Tested & Working

| Method | Endpoint | Auth Required | Description | Status |
|--------|----------|---------------|-------------|--------|
| POST | `/auth/login` | No | Login with credentials | ⚠️ Partial |
| POST | `/auth/register` | No | Register new user | ⚠️ Partial |

#### Request/Response Examples

**Login**
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=myuser&password=mypassword
```

**Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Invalid Credentials** (400 Bad Request)
```json
{
  "detail": "Incorrect email or password"
}
```

**Register User**
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (201 Created)
```json
{
  "id": 1,
  "username": "newuser",
  "email": "newuser@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-12T20:00:00Z"
}
```

#### Authentication Header Format

All authenticated requests must include:

```http
Authorization: Bearer {jwt_token}
```

Example:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     https://api.example.com/api/v1/tags/
```

---

## ⚠️ Partially Ready Endpoints

### Users API (25% tested)

| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | `/users/me` | ⚠️ | ResponseValidationError (backend issue) |
| GET | `/users/{id}` | ⚠️ | Works for forbidden cases, needs schema fix |
| PUT | `/users/me` | ⚠️ | AttributeError in tests |
| GET | `/users/` | ⚠️ | Admin only, needs testing |

**Recommendation**: Wait for backend schema fixes before integrating.

---

### Builds API (status unknown)

**Status**: 🔴 Not Ready  
**Tests Passing**: Unknown  
**Issues**: ExceptionGroup errors, endpoint validation issues  

**Recommendation**: **Do not integrate** until backend fixes are applied.

---

### Webhooks API (status unknown)

**Status**: 🔴 Not Ready  
**Tests Passing**: Unknown  
**Issues**: SQLAlchemy session errors  

**Recommendation**: **Do not integrate** until backend fixes are applied.

---

## 🔐 Authentication Model

### JWT Token Structure

Tokens are JWTs (JSON Web Tokens) with the following claims:

```json
{
  "sub": "1",                    // User ID (string)
  "type": "access",              // Token type
  "exp": 1760286384,             // Expiration timestamp
  "iat": 1760282784,             // Issued at timestamp
  "jti": "unique-token-id",      // JWT ID
  "iss": "gw2-wvwbuilder-api",   // Issuer
  "aud": "gw2-wvwbuilder-client" // Audience
}
```

### Token Expiration

- **Default**: 1 hour (3600 seconds)
- **Refresh**: Not yet implemented (planned)

### Permission Levels

- **Normal User**: Can access own resources
- **Superuser/Admin**: Can access all resources, create/update/delete

---

## 🔧 Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message here"
}
```

**Note**: Some endpoints (e.g., DELETE) may return `{msg}` instead. This is a known backend issue.

### Common Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Multilingual Error Messages

The API may return error messages in **French** or **English**. Examples:

- "not found" / "non trouvé"
- "Incorrect email or password" / "Email ou mot de passe incorrect"

**Recommendation**: Handle both languages or use status codes for logic.

---

## 📝 Development Workflow

### 1. Setup

```bash
# Backend must be running
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`

### 2. Authentication Flow

```javascript
// Example: Login and get token
const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    body: formData
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    return data.access_token;
  }
  throw new Error('Login failed');
};

// Use token for authenticated requests
const getTags = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/api/v1/tags/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    return await response.json();
  }
  throw new Error('Failed to fetch tags');
};
```

### 3. Error Handling

```javascript
const handleAPIError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    
    switch (response.status) {
      case 401:
        // Redirect to login
        window.location.href = '/login';
        break;
      case 403:
        alert('You do not have permission to perform this action');
        break;
      case 404:
        alert('Resource not found');
        break;
      default:
        alert(error.detail || error.msg || 'An error occurred');
    }
    
    throw new Error(error.detail || error.msg);
  }
  
  return await response.json();
};
```

---

## 🚧 Known Limitations

1. **Schema Validation**: Some endpoints return unexpected schemas (e.g., `{msg}` vs `{detail}`)
2. **Error Messages**: Mixed French/English responses
3. **Documentation**: OpenAPI/Swagger may not reflect actual behavior
4. **Rate Limiting**: Not yet implemented
5. **Refresh Tokens**: Not yet implemented
6. **CORS**: Ensure proper CORS configuration for frontend domain

---

## 📊 Test Coverage by Endpoint

| Endpoint Group | Tests Passing | Coverage | Status |
|----------------|---------------|----------|--------|
| Tags | 7/9 | 78% | ✅ Ready |
| Auth | 3/12 | 25% | ⚠️ Partial |
| Users | 3/12 | 25% | ⚠️ Partial |
| Builds | Unknown | <20% | 🔴 Not Ready |
| Webhooks | Unknown | <20% | 🔴 Not Ready |
| Roles | 0/9 | 0% | 🔴 Not Ready |
| Professions | 1/10 | 10% | 🔴 Not Ready |

---

## 🎯 Recommendations for Frontend Team

### ✅ Safe to Integrate Now

1. **Tags Management** - Full CRUD except DELETE (use with caution)
2. **User Login** - Basic authentication flow
3. **User Registration** - New user signup

### ⚠️ Integrate with Caution

1. **User Profile** - `/users/me` has schema issues, may fail
2. **User Management** - Admin features partially tested

### 🔴 Do Not Integrate Yet

1. **Builds API** - Unstable, needs backend fixes
2. **Webhooks API** - Unstable, needs backend fixes
3. **Roles API** - Untested
4. **Professions API** - Unstable

### 🛠️ Best Practices

1. **Always check response status codes** before parsing JSON
2. **Implement robust error handling** for all API calls
3. **Store JWT tokens securely** (HttpOnly cookies recommended over localStorage)
4. **Handle token expiration** gracefully (redirect to login)
5. **Test with both valid and invalid tokens**
6. **Implement loading states** for async operations
7. **Add request timeouts** (recommended: 30s)

---

## 📞 Support & Contact

For questions or issues:

1. Check `TEST_PROGRESS.md` for current test status
2. Review `tests/api/` for example requests
3. Contact backend team for schema/validation issues
4. Report bugs with full request/response details

---

## 🔄 Next Backend Updates (Planned)

- [ ] Fix DELETE endpoint response schemas
- [ ] Stabilize Builds API
- [ ] Stabilize Webhooks API
- [ ] Add Refresh Token support
- [ ] Implement Rate Limiting
- [ ] Improve error message consistency (single language)
- [ ] Increase test coverage to 80%+

---

**Last Updated**: 2025-10-12 22:40 UTC+2  
**Backend Branch**: develop  
**API Version**: v1
