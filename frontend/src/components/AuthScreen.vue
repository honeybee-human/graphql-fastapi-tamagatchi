<template>
  <div class="auth-screen">
    <div class="auth-container">
      <h1>🐾 Multiplayer Tamagotchi 🐾</h1>

      <div class="auth-tabs">
        <button @click="$emit('set-auth-mode', 'login')" :class="{ active: authMode === 'login' }">Login</button>
        <button @click="$emit('set-auth-mode', 'register')" :class="{ active: authMode === 'register' }">Register</button>
      </div>

      <form @submit.prevent="$emit('submit')" class="auth-form">
        <input v-model="authData.username" placeholder="Username" required />
        <input v-model="authData.password" type="password" placeholder="Password" required />
        <button type="submit" :disabled="authLoading">
          {{
            authLoading
              ? 'Loading...'
              : authMode === 'login'
              ? 'Login'
              : 'Register'
          }}
        </button>
      </form>

      <div v-if="authError" class="error">{{ authError }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthScreen',
  props: {
    authMode: { type: String, required: true },
    authData: { type: Object, required: true },
    authLoading: { type: Boolean, required: true },
    authError: { type: String, default: '' },
  },
  emits: ['submit', 'set-auth-mode'],
};
</script>