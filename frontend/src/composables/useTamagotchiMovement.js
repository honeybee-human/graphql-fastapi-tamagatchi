import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useTamagotchiMovement(tamagotchisRef) {
  const positionsById = ref({});
  const targetsById = ref({});
  // Movement metadata for easing: start position, target, start time, duration
  const movementMetaById = ref({});
  let rafId = null;

  const setTargetPosition = (id, evtOrPos) => {
    const list = tamagotchisRef?.value || [];
    const t = list.find((x) => x.id === id);
    if (!t || !t.isAlive) return;
    const pos = evtOrPos?.clientX !== undefined
      ? { x: evtOrPos.clientX, y: evtOrPos.clientY }
      : evtOrPos;
    targetsById.value[id] = pos;
    const start = positionsById.value[id] || { x: 0, y: 0 };
    const dx = pos.x - start.x;
    const dy = pos.y - start.y;
    const dist = Math.hypot(dx, dy);
    // Duration scales with distance, clamped for UX (ms)
    const duration = Math.min(2000, Math.max(200, dist * 5));
    movementMetaById.value[id] = {
      startX: start.x,
      startY: start.y,
      targetX: pos.x,
      targetY: pos.y,
      startedAt: performance.now(),
      duration,
    };
  };

  const cancelTarget = (id) => {
    delete targetsById.value[id];
    delete movementMetaById.value[id];
  };

  // Easing function: easeInOutSine
  const easeInOut = (t) => 0.5 * (1 - Math.cos(Math.PI * t));

  const step = () => {
    const now = performance.now();
    const currentPositions = positionsById.value;
    const nextPositions = { ...currentPositions };
    const list = tamagotchisRef?.value || [];

    // Advance all easing animations by time
    for (const id of Object.keys(movementMetaById.value)) {
      const meta = movementMetaById.value[id];
      const tinfo = list.find((x) => x.id === id);
      if (!tinfo || !tinfo.isAlive) {
        delete movementMetaById.value[id];
        delete targetsById.value[id];
        continue;
      }
      const elapsed = now - meta.startedAt;
      const p = Math.min(1, Math.max(0, elapsed / meta.duration));
      const e = easeInOut(p);
      const nx = meta.startX + (meta.targetX - meta.startX) * e;
      const ny = meta.startY + (meta.targetY - meta.startY) * e;
      nextPositions[id] = { x: nx, y: ny };
      if (p >= 1) {
        // Animation complete
        nextPositions[id] = { x: meta.targetX, y: meta.targetY };
        delete movementMetaById.value[id];
        delete targetsById.value[id];
      }
    }

    positionsById.value = nextPositions;
    rafId = requestAnimationFrame(step);
  };

  const startTracking = () => { if (!rafId) rafId = requestAnimationFrame(step); };
  const stopTracking = () => { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } };

  onMounted(() => {
    const list = tamagotchisRef?.value || [];
    const W = 800, H = 600;
    list.forEach((t) => { positionsById.value[t.id] = { x: Math.random() * W, y: Math.random() * H }; });
  });

  onBeforeUnmount(stopTracking);

  const hasTarget = (id) => !!movementMetaById.value[id];
  return { positionsById, setTargetPosition, startTracking, stopTracking, hasTarget, cancelTarget };
}