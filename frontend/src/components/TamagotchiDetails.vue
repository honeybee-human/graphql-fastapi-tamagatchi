<template>
  <div class="tamagotchi-details" v-if="tamagotchi">
    <h3>{{ tamagotchi.name }}</h3>
    <div class="owner-info">
      Owner: {{ ownerName }}
      <span
        v-if="tamagotchi.ownerId === currentUserId"
        class="mine-badge"
        >YOURS</span
      >
    </div>

    <div class="stats">
      <div class="stat">
        <label>❤️ Happiness</label>
        <div class="stat-bar">
          <div
            class="stat-fill happiness"
            :style="{ width: tamagotchi.happiness + '%' }"
          ></div>
        </div>
        <span>{{ tamagotchi.happiness }}/100</span>
      </div>

      <div class="stat">
        <label>🍎 Hunger</label>
        <div class="stat-bar">
          <div
            class="stat-fill hunger"
            :style="{ width: tamagotchi.hunger + '%' }"
          ></div>
        </div>
        <span>{{ tamagotchi.hunger }}/100</span>
      </div>

      <div class="stat">
        <label>⚡ Energy</label>
        <div class="stat-bar">
          <div
            class="stat-fill energy"
            :style="{ width: tamagotchi.energy + '%' }"
          ></div>
        </div>
        <span>{{ tamagotchi.energy }}/100</span>
      </div>

      <div class="stat">
        <label>💚 Health</label>
        <div class="stat-bar">
          <div
            class="stat-fill health"
            :style="{ width: tamagotchi.health + '%' }"
          ></div>
        </div>
        <span>{{ tamagotchi.health }}/100</span>
      </div>
    </div>

    <div class="age-info">
      Age: {{ tamagotchi.age }} days
    </div>

    <div v-if="!tamagotchi.isAlive" class="dead-message">
      This Tamagotchi has passed away 😢
    </div>

    <div
      v-else-if="tamagotchi.ownerId !== currentUserId"
      class="not-owner-message"
    >
      You can only interact with your own Tamagotchi
    </div>

    <div v-else class="actions">
      <button @click="$emit('feed', tamagotchi)" class="action-btn feed">
        Feed 🍎
      </button>
      <button @click="$emit('play', tamagotchi)" class="action-btn play">
        Play 🎮
      </button>
      <button @click="$emit('sleep', tamagotchi)" class="action-btn sleep">
        Sleep 😴
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "TamagotchiDetails",
  props: {
    tamagotchi: {
      type: Object,
      required: true,
    },
    currentUserId: {
      type: String,
      required: true,
    },
    ownerName: {
      type: String,
      required: true,
    },
  },
  emits: ["feed", "play", "sleep"],
};
</script>

<style scoped>
.tamagotchi-details h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.owner-info {
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.mine-badge {
  background: #667eea;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  margin-left: 5px;
}

.stats {
  margin-bottom: 15px;
}

.stat {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 10px;
  font-size: 14px;
}

.stat label {
  min-width: 80px;
  font-weight: bold;
}

.stat-bar {
  flex: 1;
  height: 12px;
  background: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  transition: width 0.3s;
}

.stat-fill.happiness {
  background: linear-gradient(90deg, #ff6b6b, #feca57);
}

.stat-fill.hunger {
  background: linear-gradient(90deg, #48dbfb, #ff6b6b);
}

.stat-fill.energy {
  background: linear-gradient(90deg, #0abde3, #006ba6);
}

.stat-fill.health {
  background: linear-gradient(90deg, #26de81, #20bf6b);
}

.stat span {
  min-width: 50px;
  text-align: right;
  font-weight: bold;
  font-size: 12px;
}

.age-info {
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s;
}

.action-btn.feed {
  background: #26de81;
  color: white;
}

.action-btn.feed:hover {
  background: #20bf6b;
}

.action-btn.play {
  background: #feca57;
  color: white;
}

.action-btn.play:hover {
  background: #ff9ff3;
}

.action-btn.sleep {
  background: #a55eea;
  color: white;
}

.action-btn.sleep:hover {
  background: #8854d0;
}

.dead-message,
.not-owner-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 5px;
  font-size: 14px;
  text-align: center;
}

.not-owner-message {
  background: #fff3cd;
  color: #856404;
}
</style>