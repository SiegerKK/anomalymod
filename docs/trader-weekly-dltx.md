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
