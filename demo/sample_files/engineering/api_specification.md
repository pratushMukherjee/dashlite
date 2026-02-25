# API Specification: CloudSync Service v2.0

## Overview
This document specifies the REST API for the CloudSync file synchronization service. CloudSync handles real-time file synchronization across distributed nodes, supporting conflict resolution and versioning.

## Authentication
All API endpoints require Bearer token authentication via OAuth 2.0. Tokens expire after 3600 seconds and must be refreshed using the `/auth/refresh` endpoint.

## Endpoints

### File Operations

#### POST /api/v2/files/upload
Upload a new file or update an existing file.

**Request:**
- Content-Type: multipart/form-data
- Headers: Authorization: Bearer {token}
- Body: file (binary), metadata (JSON)

**Response (201):**
```json
{
  "file_id": "uuid",
  "version": 1,
  "checksum": "sha256:abc123",
  "sync_status": "pending"
}
```

#### GET /api/v2/files/{file_id}
Retrieve file metadata and download URL.

#### DELETE /api/v2/files/{file_id}
Soft-delete a file (moves to trash for 30 days).

### Sync Operations

#### POST /api/v2/sync/start
Initiate a sync session between client and server.

**Conflict Resolution Strategy:**
1. Last-write-wins for simple edits
2. Three-way merge for collaborative documents
3. Fork-and-notify for irreconcilable conflicts

#### GET /api/v2/sync/status/{session_id}
Check the status of an ongoing sync operation.

### Search

#### GET /api/v2/search?q={query}&type={file_type}
Full-text search across all user files. Supports hybrid retrieval combining keyword matching with semantic similarity using vector embeddings.

## Rate Limits
- Standard tier: 1000 requests/minute
- Premium tier: 10000 requests/minute
- Enterprise: Custom limits

## Error Codes
- 400: Bad Request — invalid parameters
- 401: Unauthorized — invalid or expired token
- 409: Conflict — file version conflict during sync
- 429: Too Many Requests — rate limit exceeded
- 503: Service Unavailable — sync service temporarily down

## Architecture Notes
The API is built on a microservices architecture with Go for performance-critical sync operations and Python for the search and ML pipelines. See the System Design Document for full architecture details.
