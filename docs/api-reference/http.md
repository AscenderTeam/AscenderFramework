# HTTP API

The HTTP API provides utilities for making HTTP requests and handling HTTP-related functionality.

## Core Components

::: ascender.common.http.HTTPClient
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.common.http.HTTPOptions
    options:
      show_root_heading: true
      show_source: true
      members_order: source

::: ascender.common.http.provideHTTPClient
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.common.http.Interceptor
    options:
      show_root_heading: true
      show_source: false
      members:
        - handle_request
        - handle_response

::: ascender.common.http.InterceptorFn
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## See Also

- [HTTP Client Guide](../http/client.md) - Comprehensive HTTP client guide
- [Controllers](controllers.md) - Controller request/response handling
- [HTTPX Documentation](https://www.python-httpx.org/) - Underlying HTTP library (for http exception handling and advanced usage)
