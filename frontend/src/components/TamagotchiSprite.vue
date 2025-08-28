<template>
  <div
    class="tamagotchi-sprite"
    :class="{
      dead: !tamagotchi.isAlive,
      mine: isOwner,
    }"
    :style="{
      left: tamagotchi.position.x + 'px',
      top: tamagotchi.position.y + 'px',
    }"
    @click="$emit('select', tamagotchi)"
  >
    <div class="sprite-stats">
      <div class="mini-stat">❤️{{ tamagotchi.happiness }}</div>
      <div class="mini-stat">🍎{{ tamagotchi.hunger }}</div>
      <div class="mini-stat">⚡{{ tamagotchi.energy }}</div>
      <div class="mini-stat">💚{{ tamagotchi.health }}</div>
    </div>

    <div class="sprite-emoji">{{ tamagotchi.emoji }}</div>
    <div class="sprite-name">{{ tamagotchi.name }}</div>
    <div class="sprite-status">{{ tamagotchi.status }}</div>

    <div
      v-if="isOwner && tamagotchi.isAlive"
      class="sprite-actions"
    >
      <button
        @click.stop="$emit('feed', tamagotchi)"
        class="mini-action-btn"
      >
        🍎
      </button>
      <button
        @click.stop="$emit('play', tamagotchi)"
        class="mini-action-btn"
      >
        🎮
      </button>
      <button
        @click.stop="$emit('sleep', tamagotchi)"
        class="mini-action-btn"
      >
        😴
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "TamagotchiSprite",
  props: {
    tamagotchi: {
      type: Object,
      required: true,
    },
    currentUserId: {
      type: String,
      required: true,
    },
  },
  emits: ["select", "feed", "play", "sleep"],
  computed: {
    isOwner() {
      return this.tamagotchi.ownerId === this.currentUserId;
    },
  },
};
</script>

<style scoped>
.tamagotchi-sprite {
  position: absolute;
  cursor: pointer;
  text-align: center;
  transition: transform 0.1s;
  z-index: 5;
}

.tamagotchi-sprite:hover {
  transform: scale(1.1);
}

.tamagotchi-sprite.mine {
  filter: drop-shadow(0 0 5px #667eea);
}

.tamagotchi-sprite.dead {
  opacity: 0.5;
  filter: grayscale(100%);
}

.sprite-emoji {
  font-size: 32px;
  margin-bottom: 2px;
}

.sprite-name {
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 2px;
}

.sprite-status {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 1px 4px;
  border-radius: 8px;
  font-size: 10px;
}

.sprite-stats {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  font-size: 10px;
  white-space: nowrap;
}

.mini-stat {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 9px;
}

.sprite-actions {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
}

.mini-action-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.mini-action-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}
</style>