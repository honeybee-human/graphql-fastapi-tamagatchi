<template>
  <div id="app">
    <!-- Login/Register Screen -->
    <div v-if="!isAuthenticated" class="auth-screen">
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

    <!-- Game Screen -->
    <div v-else class="game-screen" @mousemove="updateMousePosition">
      <!-- Header -->
      <div class="header">
        <h1>🐾 Multiplayer Tamagotchi 🐾</h1>
        <div class="user-info">
          <span>Welcome, {{ currentUser?.username }}!</span>
          <button @click="logout" class="logout-btn">Logout</button>
        </div>
      </div>

      <!-- Game Area -->
      <div class="game-area" ref="gameArea">
        <!-- Other users' mouse cursors -->
        <div
          v-for="mouse in otherMousePositions"
          :key="mouse.user_id"
          class="mouse-cursor"
          :style="{ left: mouse.x + 'px', top: mouse.y + 'px' }"
        >
          <div class="cursor-pointer">🖱️</div>
          <div class="cursor-label">{{ mouse.username }}</div>
        </div>

        <!-- Tamagotchis -->
        <div
          v-for="tamagotchi in allTamagotchis"
          :key="tamagotchi.id"
          class="tamagotchi-sprite"
          :class="{
            dead: !tamagotchi.isAlive,
            mine: tamagotchi.ownerId === currentUser?.id,
          }"
          :style="{
            left: tamagotchi.position.x + 'px',
            top: tamagotchi.position.y + 'px',
          }"
          @click="selectTamagotchi(tamagotchi)"
        >
          <div class="sprite-emoji">{{ tamagotchi.emoji }}</div>
          <div class="sprite-name">{{ tamagotchi.name }}</div>
          <div class="sprite-status">{{ tamagotchi.status }}</div>
        </div>
      </div>

      <!-- Control Panel -->
      <div class="control-panel">
        <!-- Create Tamagotchi -->
        <div class="create-section">
          <h3>Create New Tamagotchi</h3>
          <div class="input-group">
            <input
              v-model="newTamagotchiName"
              placeholder="Tamagotchi name"
              @keyup.enter="createTamagotchi"
            />
            <button
              @click="createTamagotchi"
              :disabled="!newTamagotchiName.trim()"
            >
              Create
            </button>
          </div>
        </div>

        <!-- Selected Tamagotchi Details -->
        <div v-if="selectedTamagotchi" class="tamagotchi-details">
          <h3>{{ selectedTamagotchi.name }}</h3>
          <div class="owner-info">
            Owner: {{ getOwnerName(selectedTamagotchi.ownerId) }}
            <span
              v-if="selectedTamagotchi.ownerId === currentUser?.id"
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
                  :style="{ width: selectedTamagotchi.happiness + '%' }"
                ></div>
              </div>
              <span>{{ selectedTamagotchi.happiness }}/100</span>
            </div>

            <div class="stat">
              <label>🍎 Hunger</label>
              <div class="stat-bar">
                <div
                  class="stat-fill hunger"
                  :style="{ width: selectedTamagotchi.hunger + '%' }"
                ></div>
              </div>
              <span>{{ selectedTamagotchi.hunger }}/100</span>
            </div>

            <div class="stat">
              <label>⚡ Energy</label>
              <div class="stat-bar">
                <div
                  class="stat-fill energy"
                  :style="{ width: selectedTamagotchi.energy + '%' }"
                ></div>
              </div>
              <span>{{ selectedTamagotchi.energy }}/100</span>
            </div>

            <div class="stat">
              <label>💚 Health</label>
              <div class="stat-bar">
                <div
                  class="stat-fill health"
                  :style="{ width: selectedTamagotchi.health + '%' }"
                ></div>
              </div>
              <span>{{ selectedTamagotchi.health }}/100</span>
            </div>
          </div>

          <div class="age-info">
            Age: {{ Math.floor(selectedTamagotchi.age / 60) }} minutes,
            {{ selectedTamagotchi.age % 60 }} seconds
          </div>

          <!-- Actions (only for owned Tamagotchis) -->
          <div
            v-if="
              selectedTamagotchi.ownerId === currentUser?.id &&
              selectedTamagotchi.isAlive
            "
            class="actions"
          >
            <button @click="feedTamagotchi" class="action-btn feed">
              🍎 Feed
            </button>
            <button @click="playWithTamagotchi" class="action-btn play">
              🎮 Play
            </button>
            <button @click="sleepTamagotchi" class="action-btn sleep">
              😴 Sleep
            </button>
          </div>

          <div v-else-if="!selectedTamagotchi.isAlive" class="dead-message">
            💀 This Tamagotchi has died
          </div>

          <div v-else class="not-owner-message">
            👀 You can only interact with your own Tamagotchis
          </div>
        </div>

        <!-- Online Users -->
        <div class="online-users">
          <h3>Online Users ({{ onlineUsers.length }})</h3>
          <div class="user-list">
            <div v-for="user in onlineUsers" :key="user.id" class="user-item">
              <span class="user-name">{{ user.username }}</span>
              <span v-if="user.id === currentUser?.id" class="you-badge"
                >YOU</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useQuery, useMutation } from "@vue/apollo-composable";
import gql from "graphql-tag";

// GraphQL queries and mutations
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

const GET_ALL_TAMAGOTCHIS = gql`
  query GetAllTamagotchis {
    allTamagotchis {
      id
      name
      ownerId
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
      position {
        x
        y
        direction
        speed
      }
      emoji
    }
  }
`;

const GET_ALL_USERS = gql`
  query GetAllUsers {
    allUsers {
      id
      username
      isOnline
    }
  }
`;

const CREATE_TAMAGOTCHI = gql`
  mutation CreateTamagotchi($input: CreateTamagotchiInput!) {
    createTamagotchi(input: $input) {
      id
      name
      ownerId
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
      position {
        x
        y
        direction
        speed
      }
      emoji
    }
  }
`;

export default {
  name: "App",
  setup() {
    // Authentication state
    const isAuthenticated = ref(false);
    const currentUser = ref(null);
    const authMode = ref("login");
    const authData = ref({ username: "", password: "" });
    const authLoading = ref(false);
    const authError = ref("");

    // Game state
    const allTamagotchis = ref([]);
    const allUsers = ref([]);
    const selectedTamagotchi = ref(null);
    const newTamagotchiName = ref("");
    const otherMousePositions = ref([]);

    // WebSocket connection
    const ws = ref(null);

    // Computed properties
    const onlineUsers = computed(() =>
      allUsers.value.filter((user) => user.isOnline)
    );

    // GraphQL mutations
    const { mutate: loginMutation } = useMutation(LOGIN_MUTATION);
    const { mutate: registerMutation } = useMutation(REGISTER_MUTATION);
    const { mutate: createTamagotchiMutation } = useMutation(CREATE_TAMAGOTCHI);

    // GraphQL queries
    const { result: tamagotchisResult, refetch: refetchTamagotchis } =
      useQuery(GET_ALL_TAMAGOTCHIS);
    const { result: usersResult, refetch: refetchUsers } =
      useQuery(GET_ALL_USERS);

    // Authentication methods
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

        currentUser.value = authResult.user;
        isAuthenticated.value = true;

        // Connect to WebSocket
        connectWebSocket();

        // Load initial data
        await loadGameData();
      } catch (error) {
        authError.value = error.message || "Authentication failed";
      } finally {
        authLoading.value = false;
      }
    };

    const logout = () => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      currentUser.value = null;
      isAuthenticated.value = false;

      if (ws.value) {
        ws.value.close();
        ws.value = null;
      }
    };

    // WebSocket methods
    const connectWebSocket = () => {
      if (!currentUser.value) return;

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/ws/${currentUser.value.id}`;

      ws.value = new WebSocket(wsUrl);

      ws.value.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      };

      ws.value.onclose = () => {
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    };

    const handleWebSocketMessage = (message) => {
      switch (message.type) {
        case "tamagotchi_created":
          allTamagotchis.value.push(message.tamagotchi);
          break;

        case "stats_update":
          message.tamagotchis.forEach((updatedTama) => {
            const index = allTamagotchis.value.findIndex(
              (t) => t.id === updatedTama.id
            );
            if (index !== -1) {
              Object.assign(allTamagotchis.value[index], updatedTama);
            }
          });
          break;

        case "position_update":
          message.positions.forEach((pos) => {
            const tamagotchi = allTamagotchis.value.find(
              (t) => t.id === pos.id
            );
            if (tamagotchi) {
              tamagotchi.position.x = pos.x;
              tamagotchi.position.y = pos.y;
              tamagotchi.position.direction = pos.direction;
            }
          });
          break;

        case "mouse_position":
          if (message.data.user_id !== currentUser.value?.id) {
            const existingIndex = otherMousePositions.value.findIndex(
              (m) => m.user_id === message.data.user_id
            );

            if (existingIndex !== -1) {
              otherMousePositions.value[existingIndex] = message.data;
            } else {
              otherMousePositions.value.push(message.data);
            }
          }
          break;
      }
    };

    // Game methods
    const loadGameData = async () => {
      await refetchTamagotchis();
      await refetchUsers();

      if (tamagotchisResult.value?.allTamagotchis) {
        allTamagotchis.value = tamagotchisResult.value.allTamagotchis;
      }

      if (usersResult.value?.allUsers) {
        allUsers.value = usersResult.value.allUsers;
      }
    };

    const createTamagotchi = async () => {
      if (!newTamagotchiName.value.trim()) return;

      try {
        await createTamagotchiMutation({
          input: { name: newTamagotchiName.value.trim() },
        });
        newTamagotchiName.value = "";
      } catch (error) {
        console.error("Error creating Tamagotchi:", error);
      }
    };

    const selectTamagotchi = (tamagotchi) => {
      selectedTamagotchi.value = tamagotchi;
    };

    const updateMousePosition = (event) => {
      if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;

      const rect = event.currentTarget.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      ws.value.send(
        JSON.stringify({
          type: "mouse_position",
          x: x,
          y: y,
        })
      );
    };

    const getOwnerName = (ownerId) => {
      const owner = allUsers.value.find((user) => user.id === ownerId);
      return owner ? owner.username : "Unknown";
    };

    // Placeholder action methods (implement with GraphQL mutations)
    const feedTamagotchi = () => {
      console.log("Feed tamagotchi:", selectedTamagotchi.value?.id);
    };

    const playWithTamagotchi = () => {
      console.log("Play with tamagotchi:", selectedTamagotchi.value?.id);
    };

    const sleepTamagotchi = () => {
      console.log("Sleep tamagotchi:", selectedTamagotchi.value?.id);
    };

    // Initialize
    onMounted(() => {
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");

      if (token && user) {
        currentUser.value = JSON.parse(user);
        isAuthenticated.value = true;
        connectWebSocket();
        loadGameData();
      }
    });

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close();
      }
    });

    return {
      // Authentication
      isAuthenticated,
      currentUser,
      authMode,
      authData,
      authLoading,
      authError,
      handleAuth,
      logout,

      // Game state
      allTamagotchis,
      allUsers,
      selectedTamagotchi,
      newTamagotchiName,
      otherMousePositions,
      onlineUsers,

      // Game methods
      createTamagotchi,
      selectTamagotchi,
      updateMousePosition,
      getOwnerName,
      feedTamagotchi,
      playWithTamagotchi,
      sleepTamagotchi,
    };
  },
};
</script>

<style>
/* Base styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Arial", sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

/* Authentication Screen */
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

/* Game Screen */
.game-screen {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

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

/* Game Area */
.game-area {
  flex: 1;
  position: relative;
  background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%);
  overflow: hidden;
  min-height: 600px;
}

/* Mouse Cursors */
.mouse-cursor {
  position: absolute;
  pointer-events: none;
  z-index: 10;
}

.cursor-pointer {
  font-size: 16px;
}

.cursor-label {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  margin-top: 2px;
  white-space: nowrap;
}

/* Tamagotchi Sprites */
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

/* Control Panel */
.control-panel {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

.create-section h3,
.tamagotchi-details h3,
.online-users h3 {
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

/* Tamagotchi Details */
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

/* Online Users */
.user-list {
  max-height: 150px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.user-name {
  font-size: 14px;
}

.you-badge {
  background: #28a745;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

/* Responsive */
@media (max-width: 1024px) {
  .control-panel {
    grid-template-columns: 1fr;
    max-height: 300px;
  }
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

  .control-panel {
    padding: 15px;
  }

  .actions {
    justify-content: center;
  }
}
</style>
