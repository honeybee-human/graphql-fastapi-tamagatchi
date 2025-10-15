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

    <!-- Tamagotchi sprites -->
    <div
      v-for="tamagotchi in visibleTamagotchis"
      :key="tamagotchi.id"
      class="tamagotchi-sprite"
      :class="{ knocked: !tamagotchi.isAlive }"
      :style="spriteStyle(tamagotchi.id)"
      @click="onSpriteClick(tamagotchi.id, $event)"
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
  emits: ['sprite-click', 'mouse-move', 'feed', 'play', 'sleep', 'revive', 'release', 'support'],
  data() {
    return {
      gameArea: null
    };
  },
  mounted() {
    this.gameArea = this.$refs.gameArea;
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
      this.$emit('mouse-move', { x, y });
    }
  }
};
</script>