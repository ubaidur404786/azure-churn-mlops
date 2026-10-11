# Cost estimate (before building)

Written on 2026-10-11, before any Azure resource exists.
The final report (`docs/cost/COST_REPORT.md`, Phase 9) compares this estimate with the real cost of each feature.

## Assumptions

- Region: `francecentral`. Prices are rounded list prices in USD, and the credit is $200 (€175.99).
- Resources live for about **7 days**, from Phase 2 to Phase 8. Then everything is deleted.
- Training runs on the Azure ML cluster for about **1 hour in total**, for example 4–6 short jobs. The cluster scales down to 0 nodes after 120 s.
- The API gets a few hundred test requests. It scales to 0 replicas when idle.
- Logs and telemetry stay far below 1 GB.

## Estimate per feature

| feature tag | Service | Plan | How it is billed | Estimate for 7 days |
|---|---|---|---|---|
| `serving` | Container Apps env + app | Consumption, min 0, max 1 replica | per second while running; monthly free grant (180,000 vCPU-s, 360,000 GiB-s, 2M requests) | $0.00 |
| `registry` | Container Registry | Basic | fixed daily fee, about $0.167/day | about $1.20 |
| `training` | Azure ML workspace + compute cluster | 1 small CPU node, min 0 | per minute only while a node runs, about $0.20–0.30/hour | about $0.30 |
| `data` | Storage account | Standard LRS | per GB stored plus operations | under $0.10 |
| `secrets` | Key Vault + managed identity | Standard | about $0.03 per 10,000 operations; the identity is free | under $0.05 |
| `monitoring` | Log Analytics + Application Insights | Pay-as-you-go, first 5 GB/month free | per GB ingested | $0.00 |
| **Total** | | | | **about $1.70 (under $5)** |

## Biggest risks to the estimate

1. **Compute cluster left running.** If the minimum is not 0 nodes, it costs about $5–7 per day. Check: Phase 4.5 screenshot `04_cluster_zero_nodes.png`.
2. **Resources kept longer than planned.** ACR Basic keeps costing about $0.17 per day until it is deleted. Phase 8 deletes everything.
3. **Container App min replicas above 0.** One replica always on uses up the free grant in about 2 days. Keep min replicas at 0.

## Safety net

- A budget of 5 USD sends email alerts at 5%, 50%, 80% and 100% actual cost, and at 100% forecast (screenshot `00_budget.png`).
- Free account: when the credit ends, Azure stops the resources. The card is never charged unless the account is upgraded, and we never upgrade.
- Cost data arrives 8–48 hours late, so a cost of $0 in the first days is normal.

## Optional check

Rebuild this estimate in the Azure Pricing Calculator (https://azure.microsoft.com/pricing/calculator/), then paste the share link here:

- Pricing Calculator link: _not done yet_
