# MagsRedux multiplayer unload notes

- Multiplayer magazine unload requests are routed through the host for every non-host client parent, including player inventory, stashes, corpses/NPC loot, and inventory boxes; clients send the magazine id, the parent container id they see, and their netid.
- True singleplayer falls back to the original `OLDUNJECMAGS` path. The multiplayer path checks `IIsHosted()` / `IIsConnected()` instead of assuming that `not IIsHost()` means a networked client.
- Multiplayer unload is temporarily atomic until a cancel RPC is added. This avoids slow client-side unload divergence.
- The host verifies that the magazine is still under the requested parent/container before creating ammo and resolves the requester netid against `db.actors` when checking direct actor inventory. The current Lua RPC layer does not expose an unspoofable sender argument to this callback, so non-actor container authority is limited to host-side parent/type validation until a sender-bound RPC is available.
- Rollback is transactional for partial spawn failure: host tracks created ammo entities, releases them if a later `create_ammo` call fails, restores the original loaded-round list, and resyncs the magazine.
- RLE payload `version = 2` is a wire-format requirement: all participants must run the same mod version or magazine state synchronization can decode incorrectly.
