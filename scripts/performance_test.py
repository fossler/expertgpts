#!/usr/bin/env python3
"""Performance comparison: CURL vs Framework API calls for Z.AI.

This script measures and compares the performance of:
1. Direct HTTP calls (simulating CURL)
2. Framework non-streaming calls (LLMClient.chat)
3. Framework streaming calls (LLMClient.chat_stream)
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
ZAI_API_KEY = "ab3e366bed0b468586b2bd9e7eab347a.IgKW2zzWtVB1Xs9B"
MODEL = "glm-5"
TEST_MESSAGES = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Hello, please introduce yourself."}
]
NUM_RUNS = 3


def test_framework_non_streaming():
    """Test framework non-streaming API calls."""
    from lib.llm.llm_client import LLMClient

    print("\n=== Framework Non-Streaming ===")

    # Measure client creation time
    start = time.time()
    client = LLMClient(provider="zai", api_key=ZAI_API_KEY)
    client_creation_time = time.time() - start
    print(f"Client creation: {client_creation_time:.3f}s")

    results = []

    for i in range(NUM_RUNS):
        start = time.time()
        try:
            response = client.chat(
                messages=TEST_MESSAGES,
                temperature=1.0,
                model=MODEL,
                system_prompt=None  # System prompt already in messages
            )
            total_time = time.time() - start
            response_len = len(response)
            results.append(total_time)
            print(f"Run {i+1}: Total={total_time:.3f}s, Response={response_len} chars")
        except Exception as e:
            print(f"Run {i+1}: ERROR - {e}")

    if results:
        avg = sum(results) / len(results)
        print(f"Average: {avg:.3f}s")

    return results, client_creation_time


def test_framework_streaming():
    """Test framework streaming API calls."""
    from lib.llm.llm_client import LLMClient

    print("\n=== Framework Streaming ===")

    # Reuse client for fair comparison
    client = LLMClient(provider="zai", api_key=ZAI_API_KEY)

    results = []

    for i in range(NUM_RUNS):
        start = time.time()
        first_chunk_time = None
        chunk_count = 0
        total_content = ""

        try:
            for chunk in client.chat_stream(
                messages=TEST_MESSAGES,
                temperature=1.0,
                model=MODEL,
                system_prompt=None
            ):
                if first_chunk_time is None:
                    first_chunk_time = time.time() - start
                chunk_count += 1
                total_content += chunk

            total_time = time.time() - start
            results.append({
                "first_chunk": first_chunk_time,
                "total": total_time,
                "chunks": chunk_count,
                "content_len": len(total_content)
            })
            print(f"Run {i+1}: First chunk={first_chunk_time:.3f}s, Total={total_time:.3f}s, Chunks={chunk_count}")
        except Exception as e:
            print(f"Run {i+1}: ERROR - {e}")

    if results:
        avg_first_chunk = sum(r["first_chunk"] for r in results) / len(results)
        avg_total = sum(r["total"] for r in results) / len(results)
        print(f"Average: First chunk={avg_first_chunk:.3f}s, Total={avg_total:.3f}s")

    return results


def test_httpx_direct():
    """Test direct HTTP call using httpx (what OpenAI SDK uses internally)."""
    import json
    import httpx

    print("\n=== Direct HTTP (httpx) ===")

    url = "https://api.z.ai/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZAI_API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": TEST_MESSAGES,
        "stream": False
    }

    results = []

    for i in range(NUM_RUNS):
        start = time.time()
        try:
            with httpx.Client() as http_client:
                response = http_client.post(url, headers=headers, json=payload, timeout=60.0)
                total_time = time.time() - start
                data = response.json()
                content_len = len(data["choices"][0]["message"]["content"])
                results.append(total_time)
                print(f"Run {i+1}: Total={total_time:.3f}s, Response={content_len} chars")
        except Exception as e:
            print(f"Run {i+1}: ERROR - {e}")

    if results:
        avg = sum(results) / len(results)
        print(f"Average: {avg:.3f}s")

    return results


def main():
    """Run all performance tests."""
    print("=" * 60)
    print("Z.AI API Performance Comparison")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Runs per test: {NUM_RUNS}")
    print(f"Message: '{TEST_MESSAGES[1]['content']}'")

    # CURL baseline (from manual test)
    print("\n=== CURL Baseline (from manual test) ===")
    curl_results = [7.352, 7.947, 6.451]  # From earlier CURL tests
    curl_avg = sum(curl_results) / len(curl_results)
    for i, t in enumerate(curl_results):
        print(f"Run {i+1}: Total={t:.3f}s")
    print(f"Average: {curl_avg:.3f}s")

    # Test direct HTTP
    httpx_results = test_httpx_direct()

    # Test framework non-streaming
    non_stream_results, client_creation = test_framework_non_streaming()

    # Test framework streaming
    stream_results = test_framework_streaming()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if curl_results:
        curl_avg = sum(curl_results) / len(curl_results)
        print(f"CURL average:         {curl_avg:.3f}s")

    if httpx_results:
        httpx_avg = sum(httpx_results) / len(httpx_results)
        print(f"Direct HTTP average:  {httpx_avg:.3f}s")

    if non_stream_results:
        ns_avg = sum(non_stream_results) / len(non_stream_results)
        print(f"Framework non-stream: {ns_avg:.3f}s (warm, client creation excluded)")

    if stream_results:
        s_first_chunk = sum(r["first_chunk"] for r in stream_results) / len(stream_results)
        s_total = sum(r["total"] for r in stream_results) / len(stream_results)
        print(f"Framework streaming:  First chunk={s_first_chunk:.3f}s, Total={s_total:.3f}s")

    # Overhead calculation
    if curl_results and non_stream_results:
        overhead = ns_avg - curl_avg
        overhead_pct = (overhead / curl_avg) * 100
        print(f"\nFramework overhead vs CURL: {overhead:.3f}s ({overhead_pct:.1f}%)")


if __name__ == "__main__":
    main()
