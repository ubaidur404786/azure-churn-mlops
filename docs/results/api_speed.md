# Live API speed

Measured with `scripts/test_live_api.py`, from a laptop in France to the Container App in francecentral.
Each request is one `POST /predict` with the test customer (answer: `churn_probability` 0.728, `churn` true).
Before each run the API was left unused for about 10 minutes, so Azure had scaled it to 0 replicas.

| Measure | Run 1 (2026-10-12) | Run 2 (2026-10-12) |
|---|---|---|
| Cold start (first request after the app scaled to 0) | 25.91 s | 22.95 s |
| Average of 20 warm requests | 513 ms | 357 ms |
| Fastest warm request | 118 ms | 212 ms |
| Slowest warm request | 4523 ms | 673 ms |

## Reading the numbers

- **Cold start: about 23–26 s.** With min 0 replicas no container runs when nobody uses the API. The first request waits while Azure starts the container and loads the model.
- **Warm requests: about 0.2–0.4 s.** In run 1, the 2 requests right after the cold start were still slow (4.5 s and 1.7 s) because the container was still warming up. Without them, requests 3–20 average 223 ms (median of all 20: 238 ms). Run 2 had no such outliers: average 357 ms.
- Most of the warm time is the network round trip over HTTPS; the model itself predicts in a few milliseconds.

## Why

The app runs with min 0 replicas, so it costs nothing when idle. The price is the cold start. Min 1 replica would remove it, but one replica running all the time would use up the monthly free grant in about 2 days.
