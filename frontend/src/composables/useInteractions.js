// Handles user input interactions: clicks, dragging, and mouse movement
export function useInteractions(allTamagotchis, positionsById, cancelTarget, setTargetPosition, sendMousePosition, selectedTamagotchi) {
  const onSpriteClick = ({ id, x, y }) => { setTargetPosition(id, { x, y }); };
  const onMouseMove = ({ x, y }) => { sendMousePosition?.(x, y); };

  const petRadius = 24; // approximate half-size of sprite for collisions
  const clamp = (val, min, max) => Math.min(max, Math.max(min, val));

  const onDragStart = ({ id }) => {
    cancelTarget(id);
    const sel = allTamagotchis.value.find((t) => t.id === id);
    if (sel) selectedTamagotchi.value = sel;
  };

  const onDragging = ({ id, x, y, radius }) => {
    const next = { ...positionsById.value };
    next[id] = { x, y };
    // Collision repulsion: push other pets slightly away if overlapping
    for (const t of allTamagotchis.value) {
      if (!t.isAlive) continue;
      const otherId = t.id;
      if (otherId === id) continue;
      const op = positionsById.value[otherId];
      if (!op) continue;
      const dx = op.x - x;
      const dy = op.y - y;
      const dist = Math.hypot(dx, dy);
      const minDist = (radius || petRadius) * 2;
      if (dist > 0 && dist < minDist) {
        const push = (minDist - dist) * 0.5; // push strength
        const ux = dx / dist;
        const uy = dy / dist;
        const nx = op.x + ux * push;
        const ny = op.y + uy * push;
        next[otherId] = { x: nx, y: ny };
      }
    }
    positionsById.value = next;
  };

  const onDragEnd = ({ id }) => {};

  return { onSpriteClick, onMouseMove, onDragStart, onDragging, onDragEnd };
}