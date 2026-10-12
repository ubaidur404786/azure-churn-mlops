# Live API speed

Measured with `scripts/test_live_api.py`, from a laptop in France to the Container App in francecentral.
Each request is one `POST /predict` with the test customer (answer: `churn_probability` 0.728, `churn` true).
Each run starts after the API has been idle long enough for Azure to scale it to 0 replicas.

## Reading the numbers

- **Cold start: about 23–28 s.** With min 0 replicas no container runs when nobody uses the API. The first request waits while Azure starts the container and loads the model.
- **Warm requests: about 0.2–0.5 s** in most runs. In run 1, the 2 requests right after the cold start were still slow (4.5 s and 1.7 s) while the container warmed up; without them, requests 3–20 average 223 ms (median of all 20: 238 ms). Run 3 was slower overall (1.6 s average), most likely network or a busy region at that moment.
- Most of the warm time is the HTTPS round trip; the model itself predicts in a few milliseconds.

## Why

The app runs with min 0 replicas, so it costs nothing when idle. The price is the cold start. Min 1 replica would remove it, but one replica running all the time would use up the monthly free grant in about 2 days.

## Runs

The script adds one row per run. A run where the first request takes under 5 s is not saved (the app was already awake, so it is not a cold start).

| Date | Cold start | Average of 20 warm requests | Fastest | Slowest |
|---|---|---|---|---|
| 2026-10-12 | 25.91 s | 513 ms | 118 ms | 4523 ms |
| 2026-10-12 | 22.95 s | 357 ms | 212 ms | 673 ms |
| 2026-10-13 | 27.98 s | 1562 ms | 386 ms | 2566 ms |
