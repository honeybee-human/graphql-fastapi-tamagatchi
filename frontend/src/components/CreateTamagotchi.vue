<template>
  <div class="create-section">
    <h3>Create New Tamagotchi</h3>
    <div class="input-group">
      <input
        v-model="name"
        placeholder="Tamagotchi name"
        @keyup.enter="createTamagotchi"
      />
      <button
        @click="createTamagotchi"
        :disabled="!name.trim()"
      >
        Create
      </button>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";

export default {
  name: "CreateTamagotchi",
  emits: ["create"],
  setup(props, { emit }) {
    const name = ref("");

    const createTamagotchi = () => {
      if (!name.value.trim()) return;
      emit("create", name.value.trim());
      name.value = "";
    };

    return {
      name,
      createTamagotchi,
    };
  },
};
</script>

<style scoped>
.create-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.input-group {
  display: flex;
  gap: 10px;
}

.input-group input {
  flex: 1;
  padding: 8px;
  border: 2px solid #ddd;
  border-radius: 5px;
}

.input-group button {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.input-group button:hover:not(:disabled) {
  background: #5a6fd8;
}

.input-group button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>