<template>
  <div class="game-area" ref="gameArea" @mousemove="onMouseMove">
    <!-- Other users' mouse positions -->
    <div
      v-for="pos in otherMousePositions"
      :key="pos.userId"
      class="mouse-cursor"
      :style="{ transform: `translate(${pos.x}px, ${pos.y}px)` }"
    >
      <span class="cursor-label">{{ pos.username }}</span>
    </div>

    <!-- My cursor (paw) -->
    <div v-if="myMouse"
      class="my-cursor"
      :style="{ transform: `translate(${myMouse.x}px, ${myMouse.y}px)` }"
    >🐾</div>

    <!-- Tamagotchi sprites -->
    <div
      v-for="tamagotchi in visibleTamagotchis"
      :key="tamagotchi.id"
      class="tamagotchi-sprite"
      :class="{ knocked: !tamagotchi.isAlive, dragging: draggingId === tamagotchi.id }"
      :style="spriteStyle(tamagotchi.id)"
      @click="onSpriteClick(tamagotchi.id, $event)"
      @mousedown.stop="onSpriteMouseDown(tamagotchi.id, $event)"
    >
      <div class="sprite-emoji">{{ tamagotchi.emoji }}</div>
      <div class="sprite-name">{{ tamagotchi.name }}</div>
      <div class="sprite-status">
        <span class="status-badge" :class="{ dead: !tamagotchi.isAlive }">
          {{ tamagotchi.isAlive ? 'Alive' : 'Knocked out' }}
        </span>
      </div>

      <!-- Stats mini-bars -->
      <div class="sprite-stats">
        <div class="mini-stat">
          <div class="stat-bar">
            <div class="stat-fill hunger" :style="{ width: `${tamagotchi.hunger}%` }"></div>
            <div class="stat-value">{{ tamagotchi.hunger }}</div>
          </div>
          <span>Hunger</span>
        </div>
        <div class="mini-stat">
          <div class="stat-bar">
            <div class="stat-fill happiness" :style="{ width: `${tamagotchi.happiness}%` }"></div>
            <div class="stat-value">{{ tamagotchi.happiness }}</div>
          </div>
          <span>Fun</span>
        </div>
        <div class="mini-stat">
          <div class="stat-bar">
            <div class="stat-fill health" :style="{ width: `${tamagotchi.health}%` }"></div>
            <div class="stat-value">{{ tamagotchi.health }}</div>
          </div>
          <span>Health</span>
        </div>
        <div class="mini-stat">
          <div class="stat-bar">
            <div class="stat-fill energy" :style="{ width: `${tamagotchi.energy}%` }"></div>
            <div class="stat-value">{{ tamagotchi.energy }}</div>
          </div>
          <span>Energy</span>
        </div>
      </div>

      <!-- Mini action buttons -->
      <div class="sprite-actions">
        <button class="mini-action-btn feed" :disabled="!canAct(tamagotchi)" @click.stop="$emit('feed', tamagotchi)">🍽️</button>
        <button class="mini-action-btn play" :disabled="!canAct(tamagotchi)" @click.stop="$emit('play', tamagotchi)">🎮</button>
        <button class="mini-action-btn sleep" :disabled="!canAct(tamagotchi)" @click.stop="$emit('sleep', tamagotchi)">🛌</button>
        <button class="mini-action-btn revive" v-if="!tamagotchi.isAlive && isOwner(tamagotchi)" @click.stop="$emit('revive', tamagotchi)">❤️‍🩹</button>
        <button class="mini-action-btn release" v-if="isOwner(tamagotchi)" @click.stop="$emit('release', tamagotchi)">🚪</button>
        <button class="mini-action-btn support" v-if="!isOwner(tamagotchi)" :disabled="!tamagotchi.isAlive" @click.stop="$emit('support', tamagotchi)">🤝</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameArea',
  props: {
    visibleTamagotchis: { type: Array, required: true },
    positionsById: { type: Object, required: true },
    currentUser: { type: Object, required: false, default: null },
    otherMousePositions: { type: Array, required: true }
  },
  emits: ['sprite-click', 'mouse-move', 'feed', 'play', 'sleep', 'revive', 'release', 'support', 'drag-start', 'dragging', 'drag-end'],
  data() {
    return {
      gameArea: null,
      myMouse: null,
      draggingId: null,
      dragOffset: { x: 0, y: 0 },
      spriteSize: 48,
    };
  },
  mounted() {
    this.gameArea = this.$refs.gameArea;
    window.addEventListener('mouseup', this.onDragEnd);
  },
  beforeUnmount() {
    window.removeEventListener('mouseup', this.onDragEnd);
  },
  methods: {
    spriteStyle(id) {
      const pos = this.positionsById?.[id];
      if (!pos) return {};
      return { transform: `translate(${pos.x}px, ${pos.y}px)` };
    },
    isOwner(t) {
      return this.currentUser && t.ownerId === this.currentUser.id;
    },
    canAct(t) {
      return t.isAlive && this.isOwner(t);
    },
    onSpriteClick(id, evt) {
      if (!this.gameArea) return;
      const rect = this.gameArea.getBoundingClientRect();
      const x = evt.clientX - rect.left;
      const y = evt.clientY - rect.top;
      this.$emit('sprite-click', { id, x, y });
    },
    onMouseMove(evt) {
      if (!this.gameArea) return;
      const rect = this.gameArea.getBoundingClientRect();
      const x = evt.clientX - rect.left;
      const y = evt.clientY - rect.top;
      this.myMouse = { x, y };
      this.$emit('mouse-move', { x, y });
      if (this.draggingId) this.onDragMove(x, y);
    },
    onSpriteMouseDown(id, evt) {
      if (!this.gameArea) return;
      const rect = this.gameArea.getBoundingClientRect();
      const x = evt.clientX - rect.left;
      const y = evt.clientY - rect.top;
      const current = this.positionsById?.[id] || { x: 0, y: 0 };
      this.dragOffset = { x: x - current.x, y: y - current.y };
      this.draggingId = id;
      this.$emit('drag-start', { id });
    },
    clamp(val, min, max) { return Math.min(max, Math.max(min, val)); },
    onDragMove(mouseX, mouseY) {
      if (!this.draggingId || !this.gameArea) return;
      const rect = this.gameArea.getBoundingClientRect();
      const areaW = rect.width;
      const areaH = rect.height;
      const radius = this.spriteSize / 2;
      const x = this.clamp(mouseX - this.dragOffset.x, 0, areaW - this.spriteSize);
      const y = this.clamp(mouseY - this.dragOffset.y, 0, areaH - this.spriteSize);

      // Emit dragging for parent to update position and handle collisions
      this.$emit('dragging', { id: this.draggingId, x, y, radius });
    },
    onDragEnd() {
      if (!this.draggingId) return;
      this.$emit('drag-end', { id: this.draggingId });
      this.draggingId = null;
    }
  }
};
</script>