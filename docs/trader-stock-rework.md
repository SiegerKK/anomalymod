# Trader stock rework audit

Target baseline: S.T.A.L.K.E.R. Anomaly 1.5.3 trade profiles. This repository currently does not contain `gamedata/configs/items/trade/trade_*.ltx`; therefore this change does not import or rewrite base trade files. Only the review tooling is added here so the weekly-stock conversion can be validated against Anomaly 1.5.3 files when they are present.

## Restock interval

No Lua, LTX, `trade_manager.script`, `game_difficulties`, or economy preset restock values are changed. The weekly cadence remains a user/game-setting concern.

## Source policy for future imported trade files

If a `trade_*.ltx` file is added later, it must come from Anomaly 1.5.3, preserve original `#include` lines, and include only the modified trade config rather than a full extracted `gamedata` import.

## Profile inventory

| trade config | NPC/role | faction | location | source supply sections | new final section |
| --- | --- | --- | --- | --- | --- |
| trade_stalker_sidorovich | Sidorovich / rookie trader | stalker | Cordon rookie village | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_loris | Loris / stalker trader | stalker | Rostok / 100 Rads area | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_owl | Owl / general trader | stalker | Zaton Skadovsk | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_butcher | Butcher / hunter trader | stalker | Garbage flea market | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_nimble | Nimble / special-order trader | stalker | Zaton Skadovsk | supplies_1..supplies_5 plus special stock in Anomaly 1.5.3 source | supplies_weekly plus gated special-order sections |
| trade_stalker_flea_market | Flea market day trader | stalker | Garbage flea market | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_flea_market_night | Flea market night trader | stalker | Garbage flea market | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_csky_spore | Spore / Clear Sky trader | csky | Great Swamps Clear Sky base | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_ecolog_sakharov | Sakharov / scientist trader | ecolog | Yantar mobile lab | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_ecolog_hermann | Hermann / scientist trader | ecolog | Jupiter bunker | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_ecolog_spirit | Spirit / medic-scientist trader | ecolog | Yantar / ecologist areas | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_duty | Duty quartermaster | duty | Rostok / Duty base | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_freedom | Freedom quartermaster | freedom | Army Warehouses Freedom base | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_military | Military quartermaster | military | Military bases / checkpoints | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_military_esc | Cordon military trader | military | Cordon checkpoint | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_bandit | Bandit trader | bandit | Dark Valley / bandit bases | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_bandit_basic | Basic bandit trader | bandit | bandit camps | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_renegade | Renegade trader | renegade | Great Swamps renegade areas | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_mercenary | Mercenary quartermaster | killer | Dead City mercenary base | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_mercenary_basic | Basic mercenary trader | killer | mercenary squads / camps | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_mercenary_meeker | Meeker / mission trader | killer | Outskirts mercenary area | commercial supplies plus mission/special sections in Anomaly 1.5.3 source | supplies_weekly plus gated mission sections |
| trade_isg | ISG trader | isg | ISG areas | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_isg_light | Light ISG trader | isg | ISG areas | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_isg_mission | ISG mission trader | isg | ISG mission flow | commercial supplies plus mission sections in Anomaly 1.5.3 source | supplies_weekly plus gated mission sections |
| trade_greh | Sin trader | greh | Sin bases | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_monolith | Monolith trader | monolith | Monolith bases | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_monolith_basic | Basic Monolith trader | monolith | Monolith squads / bases | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_generic | Generic trader profile | mixed | shared NPC config | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_generic_barman | Generic bartender | mixed | shared bar configs | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_generic_mechanic | Generic mechanic | mixed | shared mechanic configs | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_generic_medic | Generic medic | mixed | shared medic configs | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_stalker_basic | Basic stalker trader | stalker | stalker squads / camps | supplies_1..supplies_5 in Anomaly 1.5.3 source | supplies_weekly |
| trade_main_base_mlr | Main-base MLR trader | mixed | MLR base traders | supplies_1..supplies_5 in source addon/base config | supplies_weekly |

## Quest and special stock intentionally kept gated

No quest stock was made public in this repository because no base trade files were imported or changed. For a future Anomaly 1.5.3 import, mission-only sections in profiles such as `trade_mercenary_meeker` and `trade_isg_mission`, and Nimble special-order stock, must remain under their original story/order conditions unless each item is reviewed against its quest script usage.
