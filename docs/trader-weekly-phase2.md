# Phase 2: Balance weekly quantities and probabilities

Phase 2 is **Balance weekly quantities and probabilities**. This phase is review-only until the AOEngine/Anomaly 1.5.3 effective assortment is generated and checked.

Generate the current effective assortment table with:

```sh
python3 tools/audit_trade_configs.py --source-root references/aoengine-anomaly-1.5.3 --format csv --output docs/trader-weekly-audit.csv
```

Review `quantity`, `probability`, `original_tiers`, `declared_section`, `introduced_at_tier`, `effective_section`, and `category`, then propose explicit per-item quantity/probability changes. Do not auto-scale all tiers to a seven-day restock period and do not change balance before the table is reviewed.
