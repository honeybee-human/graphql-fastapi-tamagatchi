<template>
  <div class="header">
    <h1>🐾 Multiplayer Tamagotchi 🐾</h1>
    <div class="user-info">
      <div class="difficulty-control" v-if="currentUser">
        <label for="difficulty-select">Difficulty:</label>
        <select id="difficulty-select" v-model.number="localDifficulty" @change="onDifficultyChange">
          <option v-for="opt in difficultyOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <button class="online-modal-btn" @click="emitOpenModal">👥 Online</button>
      <span class="online-count">{{ onlineUsersCount }} users online</span><span class="online-indicator"></span>
      <span>Welcome, {{ currentUser?.username }}!</span>
      <button @click="$emit('logout')" class="logout-btn">Logout</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HeaderBar',
  props: {
    currentUser: { type: Object, default: null },
    selectedDifficulty: { type: Number, required: true },
    difficultyOptions: { type: Array, required: true },
    onlineUsersCount: { type: Number, required: true },
  },
  emits: ['logout', 'open-online-modal', 'update-difficulty'],
  data() {
    return { localDifficulty: this.selectedDifficulty };
  },
  watch: {
    selectedDifficulty(n) { this.localDifficulty = n; },
  },
  methods: {
    onDifficultyChange() { this.$emit('update-difficulty', Number(this.localDifficulty)); },
    emitOpenModal(e) {
      const rect = e?.target?.getBoundingClientRect ? e.target.getBoundingClientRect() : null;
      this.$emit('open-online-modal', rect);
    }
  },
};
</script>