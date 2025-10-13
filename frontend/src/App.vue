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
          :style="positionsById[tamagotchi.id] && {
            transform: `translate(${positionsById[tamagotchi.id].x}px, ${positionsById[tamagotchi.id].y}px)`
          }"
          @click="setTargetPosition(tamagotchi.id, $event)"
        >
          <!-- Stats above the icon -->
          <div class="sprite-stats">
            <div class="mini-stat">❤️{{ tamagotchi.happiness }}</div>
            <div class="mini-stat">🍎{{ tamagotchi.hunger }}</div>
            <div class="mini-stat">⚡{{ tamagotchi.energy }}</div>
            <div class="mini-stat">💚{{ tamagotchi.health }}</div>
          </div>
          
          <!-- Main sprite -->
          <div class="sprite-emoji">{{ tamagotchi.emoji }}</div>
          <div class="sprite-name">{{ tamagotchi.name }}</div>
          <div class="sprite-status">{{ tamagotchi.status }}</div>
          
          <!-- Action buttons below (only for owned and alive Tamagotchis) -->
          <div 
            v-if="tamagotchi.ownerId === currentUser?.id && tamagotchi.isAlive" 
            class="sprite-actions"
          >
            <button @click.stop="feedTamagotchi(tamagotchi)" class="mini-action-btn">🍎</button>
            <button @click.stop="playWithTamagotchi(tamagotchi)" class="mini-action-btn">🎮</button>
            <button @click.stop="sleepTamagotchi(tamagotchi)" class="mini-action-btn">😴</button>
          </div>
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
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useQuery, useMutation, useSubscription } from "@vue/apollo-composable";
import gql from "graphql-tag";
import { useTamagotchiMovement } from "./composables/useTamagotchiMovement";
import { useDebouncedPersistence } from "./composables/usePersistence";

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

const TAMAGOTCHI_UPDATES_SUBSCRIPTION = gql`
  subscription TamagotchiUpdates {
    tamagotchiUpdates {
      type
      tamagotchi {
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
      positions {
        id
        x
        y
        direction
      }
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
    const { positionsById, setTargetPosition, startTracking, stopTracking } = useTamagotchiMovement(allTamagotchis);
    const { saveAllLocations, startAutoSave, stopAutoSave } = useDebouncedPersistence(allTamagotchis, positionsById);
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

    // GraphQL subscriptions
    const { result: subscriptionResult } = useSubscription(TAMAGOTCHI_UPDATES_SUBSCRIPTION);

    // Watch for subscription updates
    watch(subscriptionResult, (newResult) => {
      if (newResult?.tamagotchiUpdates) {
        const update = newResult.tamagotchiUpdates;
        
        switch (update.type) {
          case "stats_update":
            if (update.tamagotchi) {
              const u = update.tamagotchi;
              allTamagotchis.value = allTamagotchis.value.map((t) =>
                t.id === u.id
                  ? {
                      ...t,
                      ...u,
                      // clone nested position to avoid mutating frozen objects later
                      position: u.position
                        ? { ...u.position }
                        : t.position
                        ? { ...t.position }
                        : undefined,
                    }
                  : t
              );
            }
            break;
            
          case "position_update":
            if (update.positions) {
              const posById = new Map(update.positions.map((p) => [p.id, p]));
              allTamagotchis.value = allTamagotchis.value.map((t) => {
                const p = posById.get(t.id);
                if (!p) return t;
                const prev = t.position || {};
                return {
                  ...t,
                  position: { ...prev, x: p.x, y: p.y, direction: p.direction },
                };
              });
            }
            break;
            
          case "tamagotchi_created":
            if (update.tamagotchi) {
              const exists = allTamagotchis.value.find(
                (t) => t.id === update.tamagotchi.id
              );
              if (!exists) {
                // store a cloned object to avoid carrying frozen nested structures
                const newT = update.tamagotchi;
                allTamagotchis.value.push({
                  ...newT,
                  position: newT.position ? { ...newT.position } : undefined,
                });
              }
            }
            break;
        }
      }
    });

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
          if (Array.isArray(message.tamagotchis)) {
            const map = new Map(message.tamagotchis.map((u) => [u.id, u]));
            allTamagotchis.value = allTamagotchis.value.map((t) => {
              const u = map.get(t.id);
              if (!u) return t;
              return {
                ...t,
                ...u,
                position: u.position
                  ? { ...u.position }
                  : t.position
                  ? { ...t.position }
                  : undefined,
              };
            });
          }
          break;

        case "position_update":
          if (Array.isArray(message.positions)) {
            const posById = new Map(message.positions.map((p) => [p.id, p]));
            allTamagotchis.value = allTamagotchis.value.map((t) => {
              const p = posById.get(t.id);
              if (!p) return t;
              const prev = t.position || {};
              return { ...t, position: { ...prev, x: p.x, y: p.y, direction: p.direction } };
            });
          }
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
        
        // Manually refetch data to ensure the new Tamagotchi appears
        await loadGameData();
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
    const feedTamagotchi = (tamagotchi = null) => {
      const target = tamagotchi || selectedTamagotchi.value;
      console.log("Feed tamagotchi:", target?.id);
    };

    const playWithTamagotchi = (tamagotchi = null) => {
      const target = tamagotchi || selectedTamagotchi.value;
      console.log("Play with tamagotchi:", target?.id);
    };

    const sleepTamagotchi = (tamagotchi = null) => {
      const target = tamagotchi || selectedTamagotchi.value;
      console.log("Sleep tamagotchi:", target?.id);
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
      startTracking();
      startAutoSave();
      window.addEventListener('beforeunload', saveAllLocations);
    });

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close();
      }
      stopTracking();
      stopAutoSave();
      saveAllLocations();
      window.removeEventListener('beforeunload', saveAllLocations);
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
      // Movement
      positionsById,
      setTargetPosition,
      updateMousePosition,
      getOwnerName,
      feedTamagotchi,
      playWithTamagotchi,
      sleepTamagotchi,
    };
  },
};
</script>

<style lang="scss">
@use './styles.scss' as *;
</style>