# HTTP API

The HTTP API provides utilities for making HTTP requests and handling HTTP-related functionality.

## Core Components

### HttpClient

Async HTTP client wrapper for making external API requests.

**Constructor:**
```python
HttpClient(
    base_url: str | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    **kwargs
)
```

**Parameters:**
- `base_url`: Base URL for all requests
- `headers`: Default headers for all requests
- `timeout`: Request timeout in seconds
- `**kwargs`: Additional httpx client arguments

**Key Methods:**
- `get(url, **kwargs)`: Make GET request
- `post(url, **kwargs)`: Make POST request
- `put(url, **kwargs)`: Make PUT request
- `patch(url, **kwargs)`: Make PATCH request
- `delete(url, **kwargs)`: Make DELETE request
- `request(method, url, **kwargs)`: Make generic request

**Usage:**
```python
from ascender.common.http import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"}
)

response = await client.get("/users")
data = response.json()
```

### Request Context (Req)

Dependency injection helper for accessing the current HTTP request in controllers.

**Signature:**
```python
Req() -> Request
```

**Usage:**
```python
from ascender.core import Controller, Get
from ascender.common.http import Req

@Controller("/api")
class ApiController:
    @Get("/info")
    async def get_info(self, req=Req()):
        return {
            "method": req.method,
            "url": str(req.url),
            "headers": dict(req.headers),
            "client": req.client.host
        }
```

**Request Properties:**
- `method`: HTTP method (GET, POST, etc.)
- `url`: Request URL
- `headers`: Request headers
- `query_params`: Query parameters
- `path_params`: Path parameters
- `client`: Client information
- `cookies`: Request cookies
- `json()`: Parse JSON body
- `form()`: Parse form data
- `body()`: Get raw body

### Response Context (Res)

Dependency injection helper for accessing/modifying the HTTP response.

**Signature:**
```python
Res() -> Response
```

**Usage:**
```python
from ascender.core import Controller, Get
from ascender.common.http import Res

@Controller("/api")
class ApiController:
    @Get("/file")
    async def download(self, res=Res()):
        res.headers["Content-Disposition"] = "attachment; filename=file.txt"
        res.headers["Cache-Control"] = "public, max-age=3600"
        return {"content": "..."}
```

**Response Properties:**
- `headers`: Response headers dict
- `status_code`: HTTP status code
- `media_type`: Content type
- `set_cookie()`: Set response cookie
- `delete_cookie()`: Delete cookie

## Example Usage

### Using HTTP Client

```python
from ascender.common import Injectable, inject
from ascender.common.http import HttpClient

@Injectable()
class ExternalApiService:
    """Service for calling external APIs."""
    
    def __init__(self):
        self.client = HttpClient(base_url="https://api.example.com")
    
    async def get_user(self, user_id: str):
        """Get user from external API."""
        response = await self.client.get(f"/users/{user_id}")
        return response.json()
    
    async def create_user(self, user_data: dict):
        """Create user in external API."""
        response = await self.client.post(
            "/users",
            json=user_data,
            headers={"Authorization": "Bearer token"}
        )
        return response.json()
    
    async def update_user(self, user_id: str, user_data: dict):
        """Update user in external API."""
        response = await self.client.put(
            f"/users/{user_id}",
            json=user_data
        )
        return response.json()
    
    async def delete_user(self, user_id: str):
        """Delete user from external API."""
        await self.client.delete(f"/users/{user_id}")
```

### HTTP Client with Configuration

```python
from ascender.common.http import HttpClient
import httpx

class GithubApiClient:
    """GitHub API client."""
    
    def __init__(self, token: str):
        self.client = HttpClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=30.0
        )
    
    async def get_repo(self, owner: str, repo: str):
        """Get repository information."""
        response = await self.client.get(f"/repos/{owner}/{repo}")
        return response.json()
    
    async def list_repos(self, username: str):
        """List user repositories."""
        response = await self.client.get(f"/users/{username}/repos")
        return response.json()
```

### Accessing Request in Controllers

```python
from ascender.common import Controller, GET, POST
from ascender.common.http import Req, Res

@Controller("/api")
class ApiController:
    """API controller with request/response access."""
    
    @GET("/info")
    async def get_info(self, req=Req()):
        """Get request information."""
        return {
            "method": req.method,
            "url": str(req.url),
            "headers": dict(req.headers),
            "client": req.client.host,
        }
    
    @POST("/echo")
    async def echo(self, req=Req()):
        """Echo request body."""
        body = await req.json()
        return {
            "received": body,
            "content_type": req.headers.get("content-type"),
        }
```

### Custom Response Headers

```python
from ascender.common import Controller, GET
from ascender.common.http import Res
from fastapi.responses import JSONResponse

@Controller("/files")
class FileController:
    """File controller with custom responses."""
    
    @GET("/download/:filename")
    async def download(self, filename: str, res=Res()):
        """Download file with custom headers."""
        # Set custom headers
        res.headers["Content-Disposition"] = f"attachment; filename={filename}"
        res.headers["X-Custom-Header"] = "custom-value"
        
        return JSONResponse(
            content={"file": filename},
            headers=res.headers
        )
    
    @GET("/cached")
    async def cached_data(self, res=Res()):
        """Return cached data."""
        res.headers["Cache-Control"] = "public, max-age=3600"
        res.headers["ETag"] = "abc123"
        
        return {"data": "cached content"}
```

### Error Handling with HTTP Client

```python
from ascender.common.http import HttpClient
import httpx

class ResilientApiClient:
    """API client with error handling."""
    
    def __init__(self):
        self.client = HttpClient(
            base_url="https://api.example.com",
            timeout=10.0
        )
    
    async def fetch_data(self, endpoint: str, retries: int = 3):
        """Fetch data with retry logic."""
        for attempt in range(retries):
            try:
                response = await self.client.get(endpoint)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None  # Not found, don't retry
                elif e.response.status_code >= 500:
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                raise
            
            except httpx.TimeoutException:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                raise
```

### File Upload

```python
from ascender.common import Controller, POST
from ascender.common.http import Req
from fastapi import UploadFile, File

@Controller("/upload")
class UploadController:
    """File upload controller."""
    
    @POST("/file")
    async def upload_file(self, file: UploadFile = File(...)):
        """Upload a single file."""
        contents = await file.read()
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents)
        }
    
    @POST("/files")
    async def upload_multiple(self, files: list[UploadFile] = File(...)):
        """Upload multiple files."""
        results = []
        for file in files:
            contents = await file.read()
            results.append({
                "filename": file.filename,
                "size": len(contents)
            })
        
        return {"files": results}
```

## See Also

- [HTTP Client Guide](../http/client.md) - Comprehensive HTTP client guide
- [Controllers](controllers.md) - Controller request/response handling
- [HTTPX Documentation](https://www.python-httpx.org/) - Underlying HTTP library
