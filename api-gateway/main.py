import os

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="BookStore API Gateway")

SERVICE_MAP = {
    "book": "http://product-service:8000",
    "customer": "http://user-service:8000",
    "user": "http://user-service:8000",
    "cart": "http://cart-service:8000",
    "staff": "http://user-service:8000",
    "manager": "http://user-service:8000",
    "catalog": "http://product-service:8000",
    "product": "http://product-service:8000",
    "order": "http://order-service:8000",
    "ship": "http://ship-service:8000",
    "pay": "http://pay-service:8000",
    "rating": "http://comment-rate-service:8000",
    "recommender": "http://recommender-ai-service:8000",
    "clothes": "http://product-service:8000",
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

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


async def _proxy_to_target(request: Request, base_url: str, full_path: str = "") -> Response:
    target_url = f"{base_url}/{full_path}" if full_path else f"{base_url}/"

    body = await request.body()
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                headers=_filtered_request_headers(request),
                content=body,
            )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=502,
            content={
                "detail": "Upstream service unavailable",
                "target": target_url,
                "error": str(exc),
            },
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=_filtered_response_headers(upstream_response.headers),
        media_type=upstream_response.headers.get("content-type"),
    )


async def _proxy_request(request: Request, service: str, full_path: str = "") -> Response:
    return await _proxy_to_target(request, SERVICE_MAP[service], full_path)


async def _proxy_frontend(request: Request, full_path: str = "") -> Response:
    return await _proxy_to_target(request, FRONTEND_URL, full_path)


@app.api_route("/{service}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_service_root(service: str, request: Request) -> Response:
    if service in SERVICE_MAP:
        return await _proxy_request(request, service)
    if request.method == "GET":
        return await _proxy_frontend(request, service)
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.api_route("/{service}/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_service_path(service: str, full_path: str, request: Request) -> Response:
    if service in SERVICE_MAP:
        return await _proxy_request(request, service, full_path)
    if request.method == "GET":
        return await _proxy_frontend(request, f"{service}/{full_path}")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.get("/")
async def root(request: Request) -> Response:
    return await _proxy_frontend(request)


@app.get("/{path:path}")
async def serve_spa(path: str, request: Request) -> Response:
    normalized_path = path.strip("/")

    if normalized_path in SERVICE_MAP:
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    return await _proxy_frontend(request, normalized_path)
