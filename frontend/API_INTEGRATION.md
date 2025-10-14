# 🔌 API Integration Guide - Frontend to Backend

**Date**: 2025-10-12  
**Frontend Version**: 1.0.0  
**Backend Version**: 1.0.0  

---

## 📊 Overview

This document provides a complete mapping between frontend API calls and backend endpoints, with code examples and integration patterns.

---

## 🔐 Authentication Flow

### 1. User Login

**Frontend**: `src/api/auth.ts`

```typescript
import { login } from './api/auth';

// Login user
const response = await login({
  username: 'testuser',
  password: 'SecurePass123!',
});

// Response: { access_token: string, token_type: 'bearer' }
// Token automatically stored in localStorage
```

**Backend Endpoint**: `POST /api/v1/auth/login`

**Request**:
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=testuser&password=SecurePass123!
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `422 Unprocessable Entity`: Validation error

---

### 2. User Registration

**Frontend**: `src/api/auth.ts`

```typescript
import { register } from './api/auth';

// Register new user
const user = await register({
  username: 'newuser',
  email: 'newuser@example.com',
  password: 'SecurePass123!',
  full_name: 'John Doe', // Optional
});

// Response: User object
// Auto-login after registration
```

**Backend Endpoint**: `POST /api/v1/auth/register`

**Request**:
```http
POST /api/v1/auth/register HTTP/1.1
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-12T20:00:00Z"
}
```

---

### 3. Get Current User

**Frontend**: `src/api/auth.ts`

```typescript
import { getCurrentUser } from './api/auth';

// Get authenticated user profile
const user = await getCurrentUser();

// Response: User object with all details
```

**Backend Endpoint**: `GET /api/v1/users/me`

**Request**:
```http
GET /api/v1/users/me HTTP/1.1
Authorization: Bearer {jwt_token}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-12T20:00:00Z",
  "updated_at": "2025-10-12T21:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Backend validation issue (known bug)

---

## 🏷️ Tags Management

### 1. List All Tags

**Frontend**: `src/api/tags.ts`

```typescript
import { getTags } from './api/tags';

// Fetch all tags
const tags = await getTags();

// Response: Array of Tag objects
```

**Backend Endpoint**: `GET /api/v1/tags/`

**Request**:
```http
GET /api/v1/tags/ HTTP/1.1
Authorization: Bearer {jwt_token}
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "WvW",
    "description": "World vs World content",
    "category": "game_mode",
    "created_at": "2025-10-12T20:00:00Z"
  },
  {
    "id": 2,
    "name": "PvE",
    "description": "Player vs Environment",
    "category": "game_mode",
    "created_at": "2025-10-12T20:05:00Z"
  }
]
```

---

### 2. Get Single Tag

**Frontend**: `src/api/tags.ts`

```typescript
import { getTag } from './api/tags';

// Fetch tag by ID
const tag = await getTag(1);

// Response: Single Tag object
```

**Backend Endpoint**: `GET /api/v1/tags/{id}`

**Request**:
```http
GET /api/v1/tags/1 HTTP/1.1
Authorization: Bearer {jwt_token}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "WvW",
  "description": "World vs World content",
  "category": "game_mode",
  "created_at": "2025-10-12T20:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Tag does not exist

---

### 3. Create Tag (Admin Only)

**Frontend**: `src/api/tags.ts`

```typescript
import { createTag } from './api/tags';

// Create new tag (requires admin permissions)
const newTag = await createTag({
  name: 'Roaming',
  description: 'Small group roaming',
  category: 'playstyle',
});

// Response: Created Tag object
```

**Backend Endpoint**: `POST /api/v1/tags/`

**Request**:
```http
POST /api/v1/tags/ HTTP/1.1
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Roaming",
  "description": "Small group roaming",
  "category": "playstyle"
}
```

**Response** (200 OK):
```json
{
  "id": 3,
  "name": "Roaming",
  "description": "Small group roaming",
  "category": "playstyle",
  "created_at": "2025-10-12T21:00:00Z"
}
```

**Error Responses**:
- `403 Forbidden`: User is not admin
- `400 Bad Request`: Tag name already exists

---

### 4. Update Tag (Admin Only)

**Frontend**: `src/api/tags.ts`

```typescript
import { updateTag } from './api/tags';

// Update existing tag (requires admin permissions)
const updated = await updateTag(1, {
  description: 'Updated description',
});

// Response: Updated Tag object
```

**Backend Endpoint**: `PUT /api/v1/tags/{id}`

**Request**:
```http
PUT /api/v1/tags/1 HTTP/1.1
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "WvW",
  "description": "Updated description",
  "category": "game_mode",
  "created_at": "2025-10-12T20:00:00Z",
  "updated_at": "2025-10-12T21:30:00Z"
}
```

**Error Responses**:
- `403 Forbidden`: User is not admin
- `404 Not Found`: Tag does not exist

---

### 5. Delete Tag (Admin Only)

**Frontend**: `src/api/tags.ts`

```typescript
import { deleteTag } from './api/tags';

// Delete tag (requires admin permissions)
const result = await deleteTag(1);

// Response: { msg: 'Tag deleted' } or { detail: 'Tag deleted' }
// Note: Backend inconsistency - may return either format
```

**Backend Endpoint**: `DELETE /api/v1/tags/{id}`

**Request**:
```http
DELETE /api/v1/tags/1 HTTP/1.1
Authorization: Bearer {jwt_token}
```

**Response** (200 OK):
```json
{
  "msg": "Tag deleted successfully"
}
```

**Note**: Backend may return `{detail}` instead of `{msg}` - frontend handles both.

**Error Responses**:
- `403 Forbidden`: User is not admin
- `404 Not Found`: Tag does not exist

---

## 🔧 Error Handling Patterns

### Frontend Error Handler

```typescript
import { ApiClientError } from './api/client';

try {
  const tags = await getTags();
} catch (error) {
  if (error instanceof ApiClientError) {
    switch (error.status) {
      case 401:
        // Unauthorized - redirect to login
        logout();
        navigate('/login');
        break;
        
      case 403:
        // Forbidden - show permission error
        showToast('You do not have permission to perform this action');
        break;
        
      case 404:
        // Not found
        showToast('Resource not found');
        break;
        
      case 422:
        // Validation error
        showToast(`Validation error: ${error.detail}`);
        break;
        
      default:
        // Generic error
        showToast(`Error: ${error.detail}`);
    }
  }
}
```

### Backend Error Responses

**Standard Format**:
```json
{
  "detail": "Error message here"
}
```

**Alternative Format** (some endpoints):
```json
{
  "msg": "Error message here"
}
```

**Frontend handles both formats automatically.**

---

## 🔄 React Query Integration

### Query Example (GET)

```typescript
import { useQuery } from '@tanstack/react-query';
import { getTags } from './api/tags';

function TagsList() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['tags'],
    queryFn: getTags,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.map(tag => (
        <div key={tag.id}>{tag.name}</div>
      ))}
    </div>
  );
}
```

### Mutation Example (POST/PUT/DELETE)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createTag } from './api/tags';

function CreateTagForm() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: createTag,
    onSuccess: () => {
      // Invalidate and refetch tags list
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
    onError: (error) => {
      console.error('Failed to create tag:', error);
    },
  });

  const handleSubmit = (data) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create Tag'}
      </button>
    </form>
  );
}
```

---

## 🔐 Authentication State Management

### Zustand Store

```typescript
import { useAuthStore } from './store/authStore';

function MyComponent() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    loadUser,
  } = useAuthStore();

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Access user data
  return <div>Welcome, {user?.username}!</div>;
}
```

### Protected Route Pattern

```typescript
import { Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Usage in App.tsx
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

---

## 📝 TypeScript Types

### Authentication Types

```typescript
// Login request
interface LoginRequest {
  username: string;
  password: string;
}

// Login response
interface LoginResponse {
  access_token: string;
  token_type: string;
}

// User object
interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}
```

### Tags Types

```typescript
// Tag object
interface Tag {
  id: number;
  name: string;
  description?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
}

// Create tag request
interface CreateTagRequest {
  name: string;
  description?: string;
  category?: string;
}

// Update tag request
interface UpdateTagRequest {
  name?: string;
  description?: string;
  category?: string;
}
```

---

## 🚀 Future Endpoints (Pending Backend Stabilization)

### Builds API (Not Ready)

```typescript
// Will be available when backend stabilizes
import { getBuilds, createBuild } from './api/builds';

// Fetch builds
const builds = await getBuilds();

// Create build
const newBuild = await createBuild({
  name: 'Zerg Build',
  description: 'Large group composition',
  professions: [1, 2, 3],
});
```

**Backend Status**: 🔴 Unstable (ExceptionGroup errors)

### Webhooks API (Not Ready)

```typescript
// Will be available when backend stabilizes
import { getWebhooks, createWebhook } from './api/webhooks';

// Fetch webhooks
const webhooks = await getWebhooks();

// Create webhook
const webhook = await createWebhook({
  url: 'https://example.com/webhook',
  events: ['build.created', 'build.updated'],
});
```

**Backend Status**: 🔴 Unstable (Session conflicts)

---

## ✅ Integration Checklist

### Before Integrating New Endpoint

- [ ] Check backend status in `backend/API_READY.md`
- [ ] Verify endpoint is stable (>70% tested)
- [ ] Review request/response schemas
- [ ] Create TypeScript types
- [ ] Implement API function in `src/api/`
- [ ] Add error handling
- [ ] Create React Query hooks
- [ ] Write tests
- [ ] Update documentation

### Testing Integration

- [ ] Test successful requests
- [ ] Test error responses (401, 403, 404, 422)
- [ ] Test with invalid data
- [ ] Test with expired token
- [ ] Test with missing permissions
- [ ] Test loading states
- [ ] Test error states

---

## 📞 Support

For integration issues:

1. **Check Backend Status**: `backend/API_READY.md`
2. **Review API Docs**: `backend/FINAL_DELIVERY_REPORT.md`
3. **Check Frontend Logs**: Browser console
4. **Check Backend Logs**: `docker-compose logs backend`
5. **Test Endpoint**: Use curl or Postman

---

**Last Updated**: 2025-10-12 23:40 UTC+2  
**Maintained By**: Frontend Team  
**Backend Version**: 1.0.0 (develop branch)
