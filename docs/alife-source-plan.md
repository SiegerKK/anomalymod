# ALife source import plan

Do not import the whole vanilla script tree. Start with a read-only reference snapshot under `references/aoengine-anomaly-1.5.3/` or a documentation manifest, then copy only files that are actually patched.

## Phase 1: squad target selection and smart-terrain routing

Reference/import candidates:

- `gamedata/scripts/sim_board.script`
- `gamedata/scripts/simulation_objects.script`
- `gamedata/configs/misc/simulation_objects_props.ltx`
- `gamedata/configs/ai_tweaks/simulation_objects.ltx`
- `gamedata/scripts/smart_terrain.script`
- `gamedata/scripts/smart_terrain_control.script` if used by the selected baseline
- `gamedata/scripts/squad_manager.script` if present
- otherwise, the actual module that performs squad-manager duties in this AOEngine baseline

These files cover target evaluation, target preconditions, squad-to-smart assignment, occupancy and smart properties.

## Phase 2: online NPC behavior after a squad reaches its destination

Reference/import candidates:

- `gamedata/scripts/xr_logic.script`
- `gamedata/scripts/xr_walker.script`
- `gamedata/scripts/xr_animpoint.script`
- `gamedata/scripts/xr_reach_task.script` if present
- `gamedata/scripts/state_mgr.script`
- `gamedata/scripts/state_lib.script`
- `gamedata/scripts/job_manager.script`
- the smart-terrain jobs module actually used by this AOEngine baseline
- relevant smart-terrain LTX files only for test locations

These files cover logic-section switching, movement/animation states, job selection and arrival behavior.

## Phase 3: persistence and multiplayer authority

Existing project files that must be integrated rather than replaced:

- `gamedata/scripts/MPMain_Client_STOGETHER.script`
- `gamedata/scripts/MPMain_STOGETHER.script`
- `gamedata/scripts/MServerCall_STOGETHER.script`
- `gamedata/scripts/MPMain_QuestPatches_STOGETHER.script`
- `gamedata/scripts/MPMain_GamePatches_STOGETHER.script`

Any new ALife decision code must run only on the host. Client patches currently disable squad creation, smart updates, respawn and multiple AI actions; that firewall must remain intact.

## Recommended first ALife experiment

Do not start with a complete trader-visit system. Add one host-only diagnostic target modifier:

1. select one faction and one test smart terrain;
2. add a temporary priority bonus under a config flag;
3. log target evaluation and assignment;
4. verify offline travel and online arrival in co-op;
5. remove the test flag before expanding the feature.
