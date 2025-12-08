# HTTP Client

Ascender Framework includes a lightweight HTTP client built on top of [HTTPX](https://www.python-httpx.org/). The client integrates with the framework's dependency injection system and supports request/response interceptors and reactive streaming.

## Providing a client

```python title="bootstrap.py"
from ascender.common.http import provideHTTPClient, HTTPClient
from ascender.core.types import IBootstrap

bootstrap: IBootstrap = {
    "providers": [
        provideHTTPClient(base_url="https://api.example.com")
    ]
}
```

The factory registers `HTTPClient` so it can be injected anywhere in the application:

```python title="main_controller.py"
from ascender.core import Controller, Get
from ascender.common.http import HTTPClient

@Controller(standalone=True)
class MainController:
    def __init__(self, http: HTTPClient):
        self.http = http

    @Get()
    async def list_users(self):
        return await self.http.get(url="/users")
```

## Typed responses

Responses can be parsed into Pydantic models by passing the expected type:

```python title="usage.py"
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

user = await http.get(User, url="/users/1")
```

## Interceptors

`provideHTTPClient` accepts interceptors that can modify requests or responses. Interceptors can be async functions or classes extending `Interceptor`.

```python title="interceptors.py"
from ascender.common.http import provideHTTPClient, Interceptor
from httpx import Request, Response

class AuthInterceptor(Interceptor):
    async def handle_request(self, request: Request) -> Request:
        request.headers["Authorization"] = "Bearer <token>"
        return request

    async def handle_response(self, response: Response):
        return response

async def log_request(request: Request) -> Request:
    print(request.url)
    return request

providers = [
    provideHTTPClient(interceptors=[AuthInterceptor, log_request])
]
```

## Streaming responses

The `stream` method returns an RxPY `Observable` for consuming streamed data such as server-sent events by default. Pass `as_observable=False` to get the raw async context manager and read chunks manually.

```python title="stream.py"
stream = http.stream(dict, method="GET", url="/events")
stream.subscribe(on_next=lambda chunk: print(chunk))

# manual streaming
async with http.stream(dict, method="GET", url="/events", as_observable=False) as resp:
    async for line in resp.aiter_text():
        print(line)
```

## Form data and file uploads

Ascender introduces **FormData** - a unified payload builder that accepts both **plain string fields** and **file-like values** without needing
`data= / files= / json=` separation like HTTPX or Requests.

If the payload of `FormData` contains at least one `FileData`, the request automatically
becomes `multipart/form-data`. Otherwise, it is encoded as form fields.

```python title="examples/form_data.py"
from ascender.common.http import FormData, FileData

form = FormData(
    description="My upload",
    attachment=FileData(
        filename="report.pdf",
        content=open("report.pdf", "rb").read(),
        content_type="application/pdf",
    ),
)

await http.post(url="/upload", content=form)
```
