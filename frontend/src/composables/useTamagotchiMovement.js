import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useTamagotchiMovement(tamagotchisRef) {
  const positionsById = ref({});
  const targetsById = ref({});
  let rafId = null;

  const setTargetPosition = (id, evtOrPos) => {
    const list = tamagotchisRef?.value || [];
    const t = list.find((x) => x.id === id);
    if (!t || !t.isAlive) return;
    const pos = evtOrPos?.clientX !== undefined
      ? { x: evtOrPos.clientX, y: evtOrPos.clientY }
      : evtOrPos;
    targetsById.value[id] = pos;
  };

  const step = () => {
    const speed = 3; // px per frame
    const currentPositions = positionsById.value;
    const targets = targetsById.value;
    const nextPositions = { ...currentPositions };
    const list = tamagotchisRef?.value || [];
    for (const id in targets) {
      const tinfo = list.find((x) => x.id === id);
      if (!tinfo || !tinfo.isAlive) {
        delete targets[id];
        continue;
      }
      const t = targets[id];
      const p = currentPositions[id] || { x: 0, y: 0 };
      const dx = t.x - p.x;
      const dy = t.y - p.y;
      const dist = Math.hypot(dx, dy);
      if (dist < speed) {
        nextPositions[id] = { x: t.x, y: t.y };
        delete targets[id];
      } else {
        nextPositions[id] = { x: p.x + (dx / dist) * speed, y: p.y + (dy / dist) * speed };
      }
    }
    positionsById.value = nextPositions;
    rafId = requestAnimationFrame(step);
  };

  const startTracking = () => { if (!rafId) rafId = requestAnimationFrame(step); };
  const stopTracking = () => { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } };

  onMounted(() => {
    const list = tamagotchisRef?.value || [];
    list.forEach((t) => { positionsById.value[t.id] = t.position ? { x: t.position.x, y: t.position.y } : { x: 0, y: 0 }; });
  });

  onBeforeUnmount(stopTracking);

  const hasTarget = (id) => !!targetsById.value[id];
  return { positionsById, setTargetPosition, startTracking, stopTracking, hasTarget };
}