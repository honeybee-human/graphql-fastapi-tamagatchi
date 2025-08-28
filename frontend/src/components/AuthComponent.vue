<template>
  <div class="auth-screen">
    <div class="auth-container">
      <h1>🐾 Multiplayer Tamagotchi 🐾</h1>

      <div class="auth-tabs">
        <button
          @click="authMode = 'login'"
          :class="{ active: authMode === 'login' }"
        >
          Login
        </button>
        <button
          @click="authMode = 'register'"
          :class="{ active: authMode === 'register' }"
        >
          Register
        </button>
      </div>

      <form @submit.prevent="handleAuth" class="auth-form">
        <input v-model="authData.username" placeholder="Username" required />
        <input
          v-model="authData.password"
          type="password"
          placeholder="Password"
          required
        />
        <button type="submit" :disabled="authLoading">
          {{
            authLoading
              ? "Loading..."
              : authMode === "login"
              ? "Login"
              : "Register"
          }}
        </button>
      </form>

      <div v-if="authError" class="error">{{ authError }}</div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useMutation } from "@vue/apollo-composable";
import gql from "graphql-tag";

const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      user {
        id
        username
        createdAt
      }
    }
  }
`;

const REGISTER_MUTATION = gql`
  mutation Register($input: CreateUserInput!) {
    register(input: $input) {
      token
      user {
        id
        username
        createdAt
      }
    }
  }
`;

export default {
  name: "AuthComponent",
  emits: ["auth-success"],
  setup(props, { emit }) {
    const authMode = ref("login");
    const authData = ref({ username: "", password: "" });
    const authLoading = ref(false);
    const authError = ref("");

    const { mutate: loginMutation } = useMutation(LOGIN_MUTATION);
    const { mutate: registerMutation } = useMutation(REGISTER_MUTATION);

    const handleAuth = async () => {
      authLoading.value = true;
      authError.value = "";

      try {
        const mutation =
          authMode.value === "login" ? loginMutation : registerMutation;
        const result = await mutation({ input: authData.value });

        const authResult = result.data[authMode.value];
        localStorage.setItem("token", authResult.token);
        localStorage.setItem("user", JSON.stringify(authResult.user));

        emit("auth-success", authResult.user);
      } catch (error) {
        authError.value = error.message || "Authentication failed";
      } finally {
        authLoading.value = false;
      }
    };

    return {
      authMode,
      authData,
      authLoading,
      authError,
      handleAuth,
    };
  },
};
</script>

<style scoped>
.auth-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.auth-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.auth-tabs {
  display: flex;
  margin-bottom: 20px;
  border-radius: 10px;
  overflow: hidden;
}

.auth-tabs button {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f0f0f0;
  cursor: pointer;
  transition: background 0.3s;
}

.auth-tabs button.active {
  background: #667eea;
  color: white;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.auth-form input {
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
}

.auth-form button {
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.auth-form button:hover:not(:disabled) {
  background: #5a6fd8;
}

.auth-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  margin-top: 10px;
  padding: 10px;
  background: #ffeaea;
  border-radius: 5px;
}
</style>