# Cost story

How the cost was planned, watched and kept near zero. Real numbers only.

## 1. Plan before building

Before creating anything, [docs/cost/estimate.md](../cost/estimate.md) estimated each feature for 7 days: about **$1.70 in total**.

The biggest risk named in advance: a compute cluster left running (about $5–7 per day).

## 2. Safety nets

- **Free credit only:** $200 (€175.99). The account is never upgraded, so the card is never charged.
- **Budget alert:** $5 per month, with emails at 5%, 50%, 80% and 100% of the actual cost and at 100% of the forecast.

## 3. Design choices that keep the cost near zero

| Choice | Effect |
|---|---|
| Azure ML cluster: min 0 nodes, off after 120 s idle | pays only about 3 minutes per training job |
| Container App: min 0 replicas | €0 when idle, inside the monthly free grant |
| Curated Azure ML environment | no image build, no second registry |
| Container Registry Basic, no extras | the only fixed daily fee (about €0.16 per day) |
| Log Analytics: 0.5 GB daily cap | stays inside the free 5 GB per month |
| Everything in one resource group | one command deletes it all |

## 4. Track the cost per feature

- **Tags:** every resource has a `feature` tag (`data`, `training`, `registry`, `serving`, `secrets`, `monitoring`), so Cost Management can group costs by feature.
- **Cost log:** a snapshot at the start and end of every phase in [docs/cost/COST_LOG.md](../cost/COST_LOG.md).
- **Delay:** cost data arrives 8–48 hours late, so the first days always show €0.

## 5. The real result (before shutdown)

| Resource | Feature | Cost |
|---|---|---|
| Azure ML workspace (includes the cluster runs) | training | €0.06 |
| Container Registry | registry | €0.06 |
| Key Vault | secrets | under €0.01 |
| Storage account | data | under €0.01 |
| Log Analytics + Application Insights | monitoring | €0.00 |
| Container App + environment | serving | €0.00 |
| **Total** | | **€0.12** |

Credit left: $199.86 of $200.

The estimate was about $1.70 for 7 days. The real cost was lower because the resources lived for a shorter time, and the cluster ran only a few minutes in total.

The final report, with the cost grouped by feature tag, is written 1–2 days after the shutdown, once all cost data has arrived: `docs/cost/COST_REPORT.md`.

## 6. Three lessons

1. **Fixed fees beat usage fees on small projects.** The registry's daily fee was as large as all the training.
2. **Scale to zero works.** The API and the cluster cost €0 when idle. The price is a cold start of about 25 s.
3. **Tags must be planned from day one.** They cannot be added to cost data afterwards.
