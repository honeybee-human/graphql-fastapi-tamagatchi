import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useTamagotchiMovement(tamagotchisRef) {
  const positionsById = ref({});
  const targetsById = ref({});
  let rafId = null;

  const setTargetPosition = (id, evtOrPos) => {
    const pos = evtOrPos?.clientX !== undefined
      ? { x: evtOrPos.clientX, y: evtOrPos.clientY }
      : evtOrPos;
    targetsById.value[id] = pos;
  };

  const step = () => {
    const speed = 3; // px per frame
    const positions = positionsById.value;
    const targets = targetsById.value;
    for (const id in targets) {
      const t = targets[id];
      const p = positions[id] || { x: 0, y: 0 };
      const dx = t.x - p.x;
      const dy = t.y - p.y;
      const dist = Math.hypot(dx, dy);
      if (dist < speed) {
        positions[id] = { x: t.x, y: t.y };
        delete targets[id];
      } else {
        positions[id] = { x: p.x + (dx / dist) * speed, y: p.y + (dy / dist) * speed };
      }
    }
    rafId = requestAnimationFrame(step);
  };

  const startTracking = () => { if (!rafId) rafId = requestAnimationFrame(step); };
  const stopTracking = () => { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } };

  onMounted(() => {
    const list = tamagotchisRef?.value || [];
    list.forEach((t) => { positionsById.value[t.id] = t.position ? { x: t.position.x, y: t.position.y } : { x: 0, y: 0 }; });
  });

  onBeforeUnmount(stopTracking);

  return { positionsById, setTargetPosition, startTracking, stopTracking };
}