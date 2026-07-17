# Weekly trader stock DLTX layer

This package is a compatibility-first first pass for Anomaly 1.5.3 running on AOEngine/Modded Exes and Anomaly Together.

## What it changes

For ordinary progression-gated trader profiles it overrides `[trader].buy_supplies` and points it to a new effective section:

```ini
![trader]
buy_supplies = supplies_weekly

@[supplies_weekly]:supplies_1,supplies_2,supplies_3,supplies_4,supplies_5
```

The effective section inherits all normal commercial tiers. This removes the ordinary goodwill / Heavy Pockets tier selector without copying the full vanilla files.

## What it deliberately does not change

- restock duration;
- prices and discounts;
- buy/sell conditions;
- item counts and probabilities inside the original tiers;
- fixed-stock specialists such as Butcher and Nimble;
- mission-only profiles and quest-gated stock;
- MagsRedux magazine injection.

The user can set the restock period in the economy settings. A later balance pass should override individual item quantities and probabilities in `supplies_weekly` after observing one or two in-game weeks.

## Covered profiles

- `trade_stalker_sidorovich`
- `trade_stalker_loris`
- `trade_stalker_owl`
- `trade_stalker_basic`
- `trade_csky_spore`
- `trade_ecolog_sakharov`
- `trade_ecolog_hermann`
- `trade_duty`
- `trade_freedom`
- `trade_military`
- `trade_military_esc`
- `trade_bandit`
- `trade_renegade`
- `trade_mercenary`
- `trade_isg`
- `trade_isg_light`
- `trade_greh`
- `trade_monolith`

## Excluded pending source audit

The following profiles should not be patched generically until their source sections are inspected:

- `trade_stalker_butcher` (`supplies_generic`, fixed specialist stock);
- `trade_stalker_nimble` (unique/order stock);
- `trade_stalker_flea_market*` (day/night special stock);
- `trade_ecolog_spirit`;
- `trade_mercenary_meeker`;
- `trade_isg_mission`;
- generic barman/medic/mechanic profiles;
- addon-only MLR profiles.

## Multiplayer authority

The host remains the only authority that performs trader restock and MagsRedux stock injection. Clients receive the resulting `trade_manager` state through the existing Anomaly Together synchronization.

## Audit/runtime notes for this phase

- Phase 1 is limited to **Remove merchandise progression gates**. The patch only combines the original commercial tiers that already exist in AOEngine/Anomaly 1.5.3; it does **not** claim seven-day quantities are balanced.
- The intended DLTX form uses `![trader]` to override `buy_supplies` and `@[supplies_weekly]:...` to add a section with inheritance. The audit script now treats `[section]`, `![section]`, and `@[section]` as section declarations and validates inherited parents against the effective source tree.
- Parent validation requires the real AOEngine/Anomaly 1.5.3 source tree. Run `tools/audit_trade_configs.py --source-root <aoengine-anomaly-1.5.3>` so the vanilla `trade_*.ltx` files are present beside these minimal `mod_trade_*_weekly_stock.ltx` patches.
- Known AOEngine/Anomaly 1.5.3 three-tier exceptions use `@[supplies_weekly]:supplies_3` and must not inherit missing `supplies_4` / `supplies_5`: `trade_stalker_basic`, `trade_isg_light`, and `trade_renegade`. Other covered profiles use a single accumulated top parent (`supplies_5`) rather than listing every tier.

## Smoke-test status

The in-game smoke-test matrix still needs to be run in a real AOEngine/Anomaly Together environment: new game, existing save, host, client, each changed trader UI, no missing-section logs, no goodwill/Heavy Pockets condlist use, host-side MagsRedux restock injection, and no client-side `trader_autoinject` execution.
