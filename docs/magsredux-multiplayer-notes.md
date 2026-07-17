# MagsRedux multiplayer unload notes

- Multiplayer magazine unload requests are routed through the host for player inventory, stashes, corpses, and inventory boxes; clients only send the magazine id plus the parent container id they see.
- True singleplayer falls back to the original `OLDUNJECMAGS` path. The multiplayer path checks `IIsHosted()` / `IIsConnected()` instead of assuming that `not IIsHost()` means a networked client.
- Multiplayer unload is temporarily atomic until a cancel RPC is added. This avoids slow client-side unload divergence.
- The host verifies that the magazine is still owned by the requested parent/container before creating ammo.
- Rounds are removed from `mag_data.loaded` only after host-side `create_ammo` succeeds; failed creation restores the original loaded-round list and resyncs the magazine.
- RLE payload `version = 2` is a wire-format requirement: all participants must run the same mod version or magazine state synchronization can decode incorrectly.
