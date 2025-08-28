<template>
  <div class="header">
    <h1>🐾 Multiplayer Tamagotchi 🐾</h1>
    <div class="user-info">
      <span>Welcome, {{ username }}!</span>
      <button @click="$emit('logout')" class="logout-btn">Logout</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "GameHeader",
  props: {
    username: {
      type: String,
      required: true
    }
  },
  emits: ["logout"]
};
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.95);
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logout-btn {
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .header {
    padding: 10px 15px;
  }

  .header h1 {
    font-size: 1.5em;
  }

  .user-info {
    flex-direction: column;
    gap: 5px;
  }
}
</style>