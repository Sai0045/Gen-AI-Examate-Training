import hashlib
import json
import logging
import os
import time
from collections import OrderedDict

import requests

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300
CACHE_MAX_SIZE = 128
_response_cache = OrderedDict()


def load_env():
    # Read the .env file so the key stays out of the code.
    path = os.path.join(BASE_FOLDER, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip())


def _cache_key(model, system_prompt, user_message, temperature):
    content = json.dumps(
        [model, system_prompt, user_message, temperature],
        ensure_ascii=False,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _get_cached_response(cache_key):
    cached = _response_cache.get(cache_key)
    if cached is None:
        return None

    response, created_at = cached

    if time.monotonic() - created_at >= CACHE_TTL_SECONDS:
        del _response_cache[cache_key]
        return None

    _response_cache.move_to_end(cache_key)
    return response


def _store_cached_response(cache_key, response):
    _response_cache[cache_key] = (response, time.monotonic())
    _response_cache.move_to_end(cache_key)

    while len(_response_cache) > CACHE_MAX_SIZE:
        _response_cache.popitem(last=False)


load_env()


def ask_llm(system_prompt, user_message, temperature=0.2):
    key = os.environ.get("GROQ_API_KEY", "")
    if key == "" or key == "your_key_here":
        raise RuntimeError("GROQ_API_KEY is missing. Add it to the .env file.")

    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
    cache_key = _cache_key(model, system_prompt, user_message, temperature)

    start_time = time.perf_counter()
    cached_response = _get_cached_response(cache_key)

    if cached_response is not None:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "LLM cache hit | model=%s | latency_ms=%.2f | "
            "input_tokens=0 | output_tokens=0 | total_tokens=0",
            model,
            elapsed_ms,
        )
        return cached_response

    logger.info("LLM cache miss | model=%s", model)

    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    headers = {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }

    try:
        response = None
        for attempt in range(4):
            response = requests.post(
                GROQ_URL, json=body, headers=headers, timeout=60
            )
            # 429 means too many requests, so wait and try again.
            if response.status_code == 429 and attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
            break

        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        usage = result.get("usage") or {}

        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        logger.info(
            "LLM request | model=%s | latency_ms=%.2f | "
            "input_tokens=%s | output_tokens=%s | total_tokens=%s",
            model,
            elapsed_ms,
            prompt_tokens,
            completion_tokens,
            total_tokens,
        )

        _store_cached_response(cache_key, answer)
        return answer

    except requests.exceptions.Timeout:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error("LLM timeout | model=%s | latency_ms=%.2f", model, elapsed_ms)
        raise RuntimeError("The LLM took too long to answer")

    except requests.exceptions.RequestException as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        detail = ""
        if e.response is not None:
            detail = e.response.text[:150]

        logger.error(
            "LLM request failed | model=%s | latency_ms=%.2f | error=%s",
            model,
            elapsed_ms,
            str(e)[:100],
        )
        raise RuntimeError(
            "Could not get an answer from the LLM: "
            + str(e)[:80]
            + " "
            + detail
        )
