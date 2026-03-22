import re
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

app = FastAPI(title="BookStore API Gateway")

SERVICE_MAP = {
    "book": "http://book-service:8000",
    "customer": "http://customer-service:8000",
    "cart": "http://cart-service:8000",
    "staff": "http://staff-service:8000",
    "manager": "http://manager-service:8000",
    "catalog": "http://catalog-service:8000",
    "order": "http://order-service:8000",
    "ship": "http://ship-service:8000",
    "pay": "http://pay-service:8000",
    "rating": "http://comment-rate-service:8000",
    "recommender": "http://recommender-ai-service:8000",
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

INDEX_FILE = Path(__file__).with_name("index.html")
SPA_SERVICE_ROOTS = {"cart", "order"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "gateway": "fastapi"}


def _filtered_request_headers(request: Request) -> dict[str, str]:
    return {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host"
    }


def _filtered_response_headers(headers: httpx.Headers) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


async def _proxy_request(request: Request, service: str, full_path: str = "") -> Response:
    upstream = SERVICE_MAP[service]
    target_url = f"{upstream}/{full_path}" if full_path else f"{upstream}/"

    body = await request.body()
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            headers=_filtered_request_headers(request),
            content=body,
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=_filtered_response_headers(upstream_response.headers),
        media_type=upstream_response.headers.get("content-type"),
    )


@app.api_route("/{service}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_service_root(service: str, request: Request) -> Response:
    if request.method == "GET" and service in SPA_SERVICE_ROOTS:
        return await serve_spa(service)
    if service in SERVICE_MAP:
        return await _proxy_request(request, service)
    return await serve_spa(service)


@app.api_route("/{service}/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_service_path(service: str, full_path: str, request: Request) -> Response:
    if service in SERVICE_MAP:
        return await _proxy_request(request, service, full_path)
    return await serve_spa(f"{service}/{full_path}")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/{path:path}")
async def serve_spa(path: str) -> Response:
    normalized_path = path.strip("/")

    if re.fullmatch(r"book-\d+", normalized_path) or re.fullmatch(r"order-\d+", normalized_path):
        return FileResponse(INDEX_FILE)

    if normalized_path in {"", "login", "register", "books", "cart", "carts", "order", "checkout", "staff-books"}:
        return FileResponse(INDEX_FILE)

    if normalized_path in SERVICE_MAP:
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    static_file = Path(__file__).parent / normalized_path
    if static_file.exists() and static_file.is_file():
        return FileResponse(static_file)

    return FileResponse(INDEX_FILE)
