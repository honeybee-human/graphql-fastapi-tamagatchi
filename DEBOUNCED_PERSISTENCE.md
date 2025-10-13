# Debounced Persistence Strategy

This project implements client-side movement for Tamagotchis and persists positions to the backend in a debounced, low-frequency manner to avoid excessive writes and maintain responsiveness.

## Goals

- Keep UI responsive with smooth local animation using `requestAnimationFrame` and CSS transforms.
- Persist latest known positions reliably without hammering the database.
- Provide resilience against page reloads or browser crashes.

## How It Works

- Movement is handled locally by `useTamagotchiMovement`, which maintains `positionsById` and animates icons toward user-selected targets.
- The composable `useDebouncedPersistence` watches `positionsById` and schedules a save after inactivity (`delayMs`, default 30s). It also runs a periodic save (`intervalMs`, default 60s) as a safety net.
- On `beforeunload` and component unmount, all positions are persisted immediately to minimize loss.

## Tuning Parameters

- `delayMs`: Debounce delay after last position change before saving. Increase to reduce write frequency; decrease for quicker persistence.
- `intervalMs`: Heartbeat interval for periodic saves. Increase to lighten load; decrease to strengthen resilience.

## Data Written

For each Tamagotchi currently loaded, the latest `{ x, y }` in `positionsById` is saved via `UPDATE_TAMAGOTCHI_LOCATION` mutation. Writes are skipped when a position is missing.

## Failure Handling

- Save errors are logged and swallowed to avoid disrupting UX.
- Next scheduled or periodic save will retry naturally.

## Integration Points

- `App.vue` initializes and starts movement tracking and auto-save on mount.
- `App.vue` triggers final save and stops timers on unmount.

## Trade-offs

- Positions may lag in the backend by up to `delayMs` (plus heartbeat interval) during active movement; this is acceptable for smooth UX and reduced server load.
- Real-time multi-user views should use WebSocket broadcast for live cursor or movement, while persistence remains infrequent.

## Future Enhancements

- Persist only owned Tamagotchis to reduce unnecessary writes.
- Batch server updates in a single mutation for efficiency.
- Add exponential backoff for consecutive failures.