# Live API speed

Measured on 2026-10-12 with `scripts/test_live_api.py`, from a laptop in France to the Container App in francecentral.
Each request is one `POST /predict` with the test customer (answer: {'churn_probability': 0.728, 'churn': True}).

| Measure | Value |
|---|---|
| Cold start (first request after the app scaled to 0) | 25.91 s |
| Average of 20 warm requests | 513 ms |
| Fastest warm request | 118 ms |
| Slowest warm request | 4523 ms |

## Reading the numbers

- The 2 requests right after the cold start were still slow (4.5 s and 1.7 s): the container had started but was still warming up. They pull the average up to 513 ms.
- Without those 2, requests 3–20 average **223 ms**. The median of all 20 is **238 ms**.
- So: about **26 s** for the first request after idle, then about **0.2 s** per request.

## Why

The app runs with min 0 replicas, so it costs nothing when idle. The price is the cold start: the first request after a few idle minutes waits while Azure starts the container.
