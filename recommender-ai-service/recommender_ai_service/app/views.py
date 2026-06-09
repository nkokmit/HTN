import math
import os
import re
from collections import Counter, defaultdict

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")
RATE_SERVICE_URL = os.getenv("RATE_SERVICE_URL", "http://comment-rate-service:8000")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# In-memory interaction history acts as a lightweight sequence model state.
USER_EVENT_HISTORY = defaultdict(list)


def _safe_get_json(url: str, timeout: int = 5):
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None


def _tokenize(text: str) -> list[str]:
    return [tok for tok in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(tok) > 1]


def _build_catalog() -> list[dict]:
    products = _safe_get_json(f"{PRODUCT_SERVICE_URL}/products/") or []
    catalog = []
    for item in products:
        ptype = (item.get("product_type") or item.get("type") or "").upper()
        title = item.get("title") or item.get("name") or ""
        price = float(item.get("price") or 0)
        stock = 0
        # try common stock fields
        if item.get("stock") is not None:
            try:
                stock = int(item.get("stock") or 0)
            except Exception:
                stock = 0
        else:
            # variants shape
            stock = int(sum(v.get("stock", 0) for v in (item.get("variants") or [])))

        tags = _tokenize(" ".join([str(item.get(k) or "") for k in ("title", "author", "name", "description")]));

        catalog.append(
            {
                "product_type": ptype or "BOOK",
                "id": item.get("id"),
                "title": title,
                "description": item.get("description") or "",
                "price": price,
                "stock": stock,
                "tags": tags,
                "raw": item,
            }
        )

    return catalog


def _rating_maps() -> tuple[dict, dict]:
    ratings = _safe_get_json(f"{RATE_SERVICE_URL}/ratings/") or []
    score_map = defaultdict(float)
    count_map = defaultdict(int)

    for row in ratings:
        pid = row.get("product_id") or row.get("book_id")
        if pid is None:
            continue
        try:
            score_map[int(pid)] += float(row.get("score") or 0)
            count_map[int(pid)] += 1
        except Exception:
            continue

    return score_map, count_map


def _rag_retrieve(question: str, catalog: list[dict], top_k: int = 5) -> list[dict]:
    q_tokens = Counter(_tokenize(question))
    if not q_tokens:
        return catalog[:top_k]

    scored = []
    for item in catalog:
        d_tokens = Counter(item.get("tags") or [])
        overlap = set(q_tokens.keys()) & set(d_tokens.keys())
        score = sum(q_tokens[t] * d_tokens[t] for t in overlap)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]] or catalog[:top_k]


def _rnn_sequence_score(customer_id: int | None, item: dict) -> float:
    if customer_id is None:
        return 0.0

    history = USER_EVENT_HISTORY.get(int(customer_id), [])
    if not history:
        return 0.0

    score = 0.0
    decay = 0.9
    for index, event in enumerate(reversed(history[-40:])):
        weight = decay ** index
        if event.get("product_type") == item.get("product_type"):
            score += 0.4 * weight
        if int(event.get("product_id") or -1) == int(item.get("id") or -2):
            score += 1.2 * weight
        if event.get("event_type") == "rate":
            score += (float(event.get("value") or 0) / 5.0) * weight
    return score


def _lstm_preference_score(customer_id: int | None, item: dict) -> float:
    if customer_id is None:
        return 0.0

    history = USER_EVENT_HISTORY.get(int(customer_id), [])[-80:]
    if not history:
        return 0.0

    # Simulate LSTM-like long/short memory gates with weighted counters.
    long_term = Counter()
    short_term = Counter()
    for idx, event in enumerate(history):
        ptype = event.get("product_type")
        if not ptype:
            continue
        long_term[ptype] += 1
        if idx >= len(history) - 15:
            short_term[ptype] += 1

    ptype = item.get("product_type")
    long_pref = long_term.get(ptype, 0)
    short_pref = short_term.get(ptype, 0)
    return 0.15 * math.log1p(long_pref) + 0.3 * math.log1p(short_pref)


def _avg_rating_score(item: dict, score_map: dict, count_map: dict) -> float:
    if item.get("product_type") != "BOOK":
        return 0.0
    bid = int(item.get("id") or 0)
    count = count_map.get(bid, 0)
    if count == 0:
        return 0.0
    return float(score_map[bid]) / float(count)


def _scored_recommendations(customer_id: int | None, limit: int = 8) -> list[dict]:
    catalog = _build_catalog()
    score_map, count_map = _rating_maps()

    scored = []
    for item in catalog:
        base = _avg_rating_score(item, score_map, count_map)
        rnn = _rnn_sequence_score(customer_id, item)
        lstm = _lstm_preference_score(customer_id, item)
        final_score = base + rnn + lstm
        scored.append(
            {
                "product_type": item["product_type"],
                "id": item["id"],
                "title": item["title"],
                "description": item["description"],
                "price": item["price"],
                "stock": item["stock"],
                "score": round(final_score, 4),
                "raw": item["raw"],
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def _gemini_answer(question: str, context_rows: list[dict]) -> str | None:
    if not GEMINI_API_KEY:
        return None

    context_text = "\n".join(
        f"- [{row['product_type']}] {row['title']} | price={row['price']} | stock={row['stock']}"
        for row in context_rows[:6]
    )
    prompt = (
        "You are an ecommerce assistant. Use only this catalog context to answer. "
        "Keep answer concise in Vietnamese.\n"
        f"Context:\n{context_text}\n\nQuestion: {question}"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code != 200:
            return None
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return None
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        if not parts:
            return None
        return (parts[0].get("text") or "").strip() or None
    except requests.RequestException:
        return None


def _fallback_answer(question: str, context_rows: list[dict]) -> str:
    if not context_rows:
        return "Mình chưa tìm thấy sản phẩm phù hợp lúc này. Bạn thử mô tả cụ thể hơn như loại sản phẩm, giá, hoặc màu sắc nhé."

    top = context_rows[0]
    if "giá" in question.lower() or "price" in question.lower():
        return f"Sản phẩm phù hợp nhất là {top['title']} với giá khoảng {top['price']}."
    if "còn hàng" in question.lower() or "stock" in question.lower():
        return f"{top['title']} hiện còn khoảng {top['stock']} sản phẩm trong kho."
    if "gợi ý" in question.lower() or "đề xuất" in question.lower():
        titles = ", ".join(row["title"] for row in context_rows[:3])
        return f"Bạn có thể xem thử: {titles}."
    return f"Bạn có thể bắt đầu với {top['title']} (giá {top['price']}) vì nó phù hợp với câu hỏi của bạn."


class RecommendationView(APIView):
    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        try:
            customer_id_val = int(customer_id) if customer_id is not None else None
        except ValueError:
            return Response({"error": "customer_id must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        recs = _scored_recommendations(customer_id_val, limit=8)
        return Response({"recommendations": recs})


class HomeSuggestionsView(APIView):
    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        try:
            customer_id_val = int(customer_id) if customer_id is not None else None
        except ValueError:
            return Response({"error": "customer_id must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        recs = _scored_recommendations(customer_id_val, limit=10)
        return Response({"suggestions": recs})


class TrackEventView(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        event_type = str(request.data.get("event_type") or "").strip().lower()
        product_type = str(request.data.get("product_type") or "").strip().upper()
        product_id = request.data.get("product_id")
        value = request.data.get("value", 1)

        if customer_id is None:
            return Response({"error": "customer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if event_type not in {"click", "add_to_cart", "view_detail", "rate", "chat"}:
            return Response({"error": "invalid event_type"}, status=status.HTTP_400_BAD_REQUEST)
        if product_type and product_type not in {"BOOK", "CLOTHES", "MOBILE", "ELECTRONICS", "COSMETICS"}:
            return Response({"error": "invalid product_type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cid = int(customer_id)
            pid = int(product_id) if product_id is not None else None
            v = float(value)
        except (TypeError, ValueError):
            return Response({"error": "invalid numeric fields"}, status=status.HTTP_400_BAD_REQUEST)

        USER_EVENT_HISTORY[cid].append(
            {
                "event_type": event_type,
                "product_type": product_type,
                "product_id": pid,
                "value": v,
            }
        )

        if len(USER_EVENT_HISTORY[cid]) > 200:
            USER_EVENT_HISTORY[cid] = USER_EVENT_HISTORY[cid][-200:]

        return Response({"status": "tracked", "history_size": len(USER_EVENT_HISTORY[cid])})


class ProductChatView(APIView):
    def post(self, request):
        question = str(request.data.get("question") or "").strip()
        customer_id = request.data.get("customer_id")

        if not question:
            return Response({"error": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

        customer_id_val = None
        if customer_id is not None:
            try:
                customer_id_val = int(customer_id)
            except ValueError:
                return Response({"error": "customer_id must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        catalog = _build_catalog()
        retrieved = _rag_retrieve(question, catalog, top_k=6)

        gemini_text = _gemini_answer(question, retrieved)
        answer = gemini_text or _fallback_answer(question, retrieved)

        if customer_id_val is not None:
            USER_EVENT_HISTORY[customer_id_val].append(
                {
                    "event_type": "chat",
                    "product_type": "",
                    "product_id": None,
                    "value": 1,
                }
            )

        products = [
            {
                "product_type": row.get("product_type"),
                "id": row.get("id"),
                "title": row.get("title"),
                "price": row.get("price"),
                "stock": row.get("stock"),
            }
            for row in retrieved
        ]

        return Response(
            {
                "answer": answer,
                "source": "gemini" if gemini_text else "rag-fallback",
                "products": products,
            }
        )


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "recommender-ai-service"})
