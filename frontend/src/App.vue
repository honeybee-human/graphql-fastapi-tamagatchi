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
          <button class="online-modal-btn" ref="onlineBtnRef" @click="openOnlineModal">👥 Online</button>
          <span class="online-count">{{ onlineUsers.length }} users online</span><span class="online-indicator"></span>
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
          v-for="tamagotchi in visibleTamagotchis"
          :key="tamagotchi.id"
          class="tamagotchi-sprite"
          :class="{
            dead: !tamagotchi.isAlive,
            mine: tamagotchi.ownerId === currentUser?.id,
          }"
          :style="positionsById[tamagotchi.id] && {
            transform: `translate(${positionsById[tamagotchi.id].x}px, ${positionsById[tamagotchi.id].y}px)`
          }"
          @click="onSpriteClick(tamagotchi.id, $event)"
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
          <div class="sprite-status">{{ displayStatus(tamagotchi.status) }}</div>
          
          <!-- Action buttons below (only for owned and alive Tamagotchis) -->
          <div 
            v-if="tamagotchi.ownerId === currentUser?.id && tamagotchi.isAlive" 
            class="sprite-actions"
          >
            <button @click.stop="feedTamagotchi(tamagotchi)" class="mini-action-btn">🍎</button>
            <button @click.stop="playWithTamagotchi(tamagotchi)" class="mini-action-btn">🎮</button>
            <button @click.stop="sleepTamagotchi(tamagotchi)" class="mini-action-btn">😴</button>
          </div>
          <!-- Owner actions for knocked out pets -->
          <div 
            v-else-if="tamagotchi.ownerId === currentUser?.id && !tamagotchi.isAlive" 
            class="sprite-actions"
          >
            <button @click.stop="reviveTamagotchi(tamagotchi)" class="mini-action-btn">💉 Revive</button>
            <button @click.stop="releaseTamagotchi(tamagotchi)" class="mini-action-btn">🗑️ Release</button>
          </div>
          <!-- Other users' heart support (only for non-owners and alive) -->
          <div 
            v-if="tamagotchi.ownerId !== currentUser?.id && tamagotchi.isAlive" 
            class="sprite-actions"
          >
            <button @click.stop="supportTamagotchi(tamagotchi)" class="mini-action-btn">💚</button>
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
          <div class="filter-row">
            <label class="checkbox-label"><input type="checkbox" v-model="showMyKnockedOut" class="pretty-checkbox" /> <span>show my knocked out pets?</span></label>
          </div>
          <div class="previous-names">
            <h4>Previous Pets</h4>
            <div class="names-list">
              <button
                v-for="t in myTamagotchis"
                :key="t.id"
                class="name-item"
                @click="selectTamagotchi(t)"
              >
                {{ t.name }}
              </button>
            </div>
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
            This Tamagotchi is knocked out
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

      <!-- Online Users Modal -->
      <div v-if="showOnlineModal" class="modal-overlay" @click.self="showOnlineModal = false">
        <div class="modal anchored" :style="modalStyle">
          <div class="modal-header">
            <h3>Online Users</h3>
            <button class="close-btn" @click="showOnlineModal = false">✖</button>
          </div>
          <div class="modal-body">
            <div class="filter-row">
              <label class="checkbox-label"><input type="checkbox" v-model="showDeadPets" class="pretty-checkbox" /> <span>show other users' knocked out pets?</span></label>
            </div>
            <div class="user-toggle-list">
              <div v-for="user in onlineOthers" :key="user.id" class="toggle-item">
                <label class="checkbox-label">
                  <input type="checkbox" :value="user.id" v-model="selectedUserIds" class="pretty-checkbox" />
                  <span>{{ user.username }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast notifications -->
      <div class="toast-container">
        <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">{{ toast.message }}</div>
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

const SUPPORT_TAMAGOTCHI = gql`
  mutation SupportTamagotchi($id: ID!) {
    supportTamagotchi(id: $id) {
      id
      happiness
      hunger
      energy
      health
      isAlive
      status
    }
  }
`;

const REVIVE_TAMAGOTCHI = gql`
  mutation ReviveTamagotchi($id: ID!) {
    reviveTamagotchi(id: $id) {
      id
      happiness
      hunger
      energy
      health
      isAlive
      status
    }
  }
`;

const RELEASE_TAMAGOTCHI = gql`
  mutation ReleaseTamagotchi($id: ID!) {
    releaseTamagotchi(id: $id)
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
    const { positionsById, setTargetPosition, startTracking, stopTracking, hasTarget } = useTamagotchiMovement(allTamagotchis);
    const { saveAllLocations, startAutoSave, stopAutoSave } = useDebouncedPersistence(allTamagotchis, positionsById);
    const allUsers = ref([]);
    const selectedTamagotchi = ref(null);
    const newTamagotchiName = ref("");
    const otherMousePositions = ref([]);
    const gameArea = ref(null);
    const showOnlineModal = ref(false);
    const selectedUserIds = ref([]);
    const showDeadPets = ref(false);
    const showMyKnockedOut = ref(false);
    const onlineBtnRef = ref(null);
    const modalStyle = ref({ position: 'fixed', top: '80px', left: '20px' });
    const hiddenDeadMineIds = ref(new Set());
    const toasts = ref([]);

    // WebSocket connection
    const ws = ref(null);

    // Computed properties
    const onlineUsers = computed(() => allUsers.value.filter((user) => user.isOnline));
    const onlineOthers = computed(() => onlineUsers.value.filter((u) => u.id !== currentUser.value?.id));
    const myTamagotchis = computed(() => allTamagotchis.value.filter((t) => t.ownerId === currentUser.value?.id));
    const visibleTamagotchis = computed(() =>
      allTamagotchis.value.filter((t) => {
        const ownerSelected = selectedUserIds.value.length === 0
          ? true
          : selectedUserIds.value.includes(t.ownerId);
        const isMine = t.ownerId === currentUser.value?.id;
        const deadOk = t.isAlive ? true : (isMine ? showMyKnockedOut.value : showDeadPets.value);
        const hiddenMineDead = isMine && hiddenDeadMineIds.value.has(t.id);
        return ownerSelected && deadOk && !hiddenMineDead;
      })
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
    const { mutate: supportMutation } = useMutation(SUPPORT_TAMAGOTCHI);
    const { mutate: reviveMutation } = useMutation(REVIVE_TAMAGOTCHI);
    const { mutate: releaseMutation } = useMutation(RELEASE_TAMAGOTCHI);

    // Watch for subscription updates
    watch(subscriptionResult, (newResult) => {
      if (newResult?.tamagotchiUpdates) {
        const update = newResult.tamagotchiUpdates;
        
        switch (update.type) {
          case "stats_update":
            if (update.tamagotchi) {
              const u = update.tamagotchi;
              const prev = allTamagotchis.value.find((t) => t.id === u.id);
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
              if (prev && prev.isAlive && !u.isAlive) {
                if (prev.ownerId === currentUser.value?.id) {
                  setTimeout(() => { hiddenDeadMineIds.value.add(prev.id); }, 3000);
                }
                pushToast(`your pet ${prev.name} is knocked out!`, 'warning');
              }
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

          case "tamagotchi_removed":
            if (update.id) {
              const id = update.id;
              allTamagotchis.value = allTamagotchis.value.filter((t) => t.id !== id);
              if (selectedTamagotchi.value?.id === id) selectedTamagotchi.value = null;
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
      // Connect directly to backend to avoid dev proxy issues
      const backendHost = "127.0.0.1:8000";
      const wsUrl = `${protocol}//${backendHost}/ws/${currentUser.value.id}`;

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
          if (message.tamagotchi) {
            const exists = allTamagotchis.value.some((t) => t.id === message.tamagotchi.id);
            if (!exists) {
              allTamagotchis.value = [...allTamagotchis.value, message.tamagotchi];
            }
          }
          break;

        case "stats_update":
          if (Array.isArray(message.tamagotchis)) {
            const map = new Map(message.tamagotchis.map((u) => [u.id, u]));
            const before = new Map(allTamagotchis.value.map((t) => [t.id, t]));
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
            for (const [id, u] of map.entries()) {
              const prev = before.get(id);
              if (prev && prev.isAlive && !u.is_alive) {
                if (prev.ownerId === currentUser.value?.id) {
                  setTimeout(() => { hiddenDeadMineIds.value.add(prev.id); }, 3000);
                }
                pushToast(`your pet ${prev.name} is knocked out!`, 'warning');
              }
            }
          }
          // Also handle single tamagotchi updates
          if (message.tamagotchi) {
            const u = message.tamagotchi;
            const before = new Map(allTamagotchis.value.map((t) => [t.id, t]));
            allTamagotchis.value = allTamagotchis.value.map((t) =>
              t.id === u.id
                ? {
                    ...t,
                    ...u,
                    position: u.position
                      ? { ...u.position }
                      : t.position
                      ? { ...t.position }
                      : undefined,
                  }
                : t
            );
            const prev = before.get(u.id);
            if (prev && prev.isAlive && !u.is_alive) {
              if (prev.ownerId === currentUser.value?.id) {
                setTimeout(() => { hiddenDeadMineIds.value.add(prev.id); }, 3000);
              }
              pushToast(`your pet ${prev.name} is knocked out!`, 'warning');
            }
          }
          break;

        case "position_update":
          if (Array.isArray(message.positions)) {
            const posById = new Map(message.positions.map((p) => [p.id, p]));
            allTamagotchis.value = allTamagotchis.value.map((t) => {
              const p = posById.get(t.id);
              if (!p) return t;
              if (!t.isAlive) return t;
              const prev = t.position || {};
              return { ...t, position: { ...prev, x: p.x, y: p.y, direction: p.direction } };
            });

            // Drive UI positions for smooth movement (alive only)
            const next = { ...positionsById.value };
            for (const [id, p] of posById.entries()) {
              const tinfo = allTamagotchis.value.find((x) => x.id === id);
              if (!tinfo || !tinfo.isAlive) continue;
              if (hasTarget(id)) continue;
              next[id] = { x: p.x, y: p.y };
            }
            positionsById.value = next;
          }
          break;

        case "mouse_position":
          if (message.data.user_id !== currentUser.value?.id) {
            const existingIndex = otherMousePositions.value.findIndex(
              (m) => m.user_id === message.data.user_id
            );

            if (existingIndex !== -1) {
              otherMousePositions.value = otherMousePositions.value.map((m, i) =>
                i === existingIndex ? message.data : m
              );
            } else {
              otherMousePositions.value = [...otherMousePositions.value, message.data];
            }
          }
          break;

        case "tamagotchi_removed":
          if (message.id) {
            const id = message.id;
            allTamagotchis.value = allTamagotchis.value.filter((t) => t.id !== id);
            if (selectedTamagotchi.value?.id === id) selectedTamagotchi.value = null;
          }
          break;
      }
    };

    // Game methods
    const loadGameData = async () => {
      await refetchTamagotchis();
      await refetchUsers();

      if (tamagotchisResult.value?.allTamagotchis) {
        // Clone array and nested positions to avoid mutating Apollo-frozen data
        allTamagotchis.value = tamagotchisResult.value.allTamagotchis.map((t) => ({
          ...t,
          position: t.position ? { ...t.position } : undefined,
        }));
        // Seed UI positions
        const seeded = {};
        for (const t of allTamagotchis.value) {
          if (t.position) seeded[t.id] = { x: t.position.x, y: t.position.y };
        }
        positionsById.value = seeded;
      }

      if (usersResult.value?.allUsers) {
        // Clone array to avoid direct mutation of Apollo arrays
        allUsers.value = [...usersResult.value.allUsers];
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

    const onSpriteClick = (id, event) => {
      const rect = gameArea.value?.getBoundingClientRect?.();
      if (!rect) return;
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      setTargetPosition(id, { x, y });
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

    const displayStatus = (status) => (status === 'Dead' ? 'Knocked Out' : status);

    const pushToast = (message, type = 'info') => {
      const id = Math.random().toString(36).slice(2);
      toasts.value = [...toasts.value, { id, message, type }];
      setTimeout(() => { toasts.value = toasts.value.filter((t) => t.id !== id); }, 5000);
    };

    const supportTamagotchi = async (tamagotchi) => {
      try {
        await supportMutation({ id: tamagotchi.id });
        pushToast(`you sent love to ${tamagotchi.name}!`, 'success');
      } catch (e) {
        pushToast('failed to support pet', 'error');
      }
    };

    const reviveTamagotchi = async (tamagotchi) => {
      try {
        const res = await reviveMutation({ id: tamagotchi.id });
        const u = res?.data?.reviveTamagotchi;
        if (u) {
          allTamagotchis.value = allTamagotchis.value.map((t) => (t.id === u.id ? { ...t, ...u } : t));
          pushToast(`you revived ${tamagotchi.name}!`, 'success');
        } else {
          pushToast('failed to revive pet', 'error');
        }
      } catch (e) {
        pushToast('failed to revive pet', 'error');
      }
    };

    const releaseTamagotchi = async (tamagotchi) => {
      try {
        const res = await releaseMutation({ id: tamagotchi.id });
        const ok = res?.data?.releaseTamagotchi;
        if (ok) {
          allTamagotchis.value = allTamagotchis.value.filter((t) => t.id !== tamagotchi.id);
          if (selectedTamagotchi.value?.id === tamagotchi.id) selectedTamagotchi.value = null;
          pushToast(`you released ${tamagotchi.name}.`, 'info');
        } else {
          pushToast('failed to release pet', 'error');
        }
      } catch (e) {
        pushToast('failed to release pet', 'error');
      }
    };

    const openOnlineModal = () => {
      if (showOnlineModal.value) {
        showOnlineModal.value = false;
        return;
      }
      showOnlineModal.value = true;
      const ids = onlineOthers.value.map((u) => u.id);
      if (ids.length && selectedUserIds.value.length === 0) selectedUserIds.value = ids;
      const rect = onlineBtnRef.value?.getBoundingClientRect?.();
      if (rect) {
        modalStyle.value = { position: 'fixed', top: `${rect.bottom + 6}px`, left: `${rect.left}px` };
      }
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
      visibleTamagotchis,
      allUsers,
      selectedTamagotchi,
      newTamagotchiName,
      otherMousePositions,
      onlineUsers,
      onlineOthers,
      myTamagotchis,
      showOnlineModal,
      selectedUserIds,
      showDeadPets,
      showMyKnockedOut,
      onlineBtnRef,
      openOnlineModal,
      modalStyle,

      // Game methods
      createTamagotchi,
      selectTamagotchi,
      // Movement
      positionsById,
      setTargetPosition,
      onSpriteClick,
      updateMousePosition,
      getOwnerName,
      displayStatus,
      feedTamagotchi,
      playWithTamagotchi,
      sleepTamagotchi,
      reviveTamagotchi,
      releaseTamagotchi,
      supportTamagotchi,
      gameArea,
      toasts,
    };
  },
};
</script>

<style lang="scss">
@use './styles.scss' as *;
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.2); z-index: 9998; }
.modal.anchored { position: fixed; background: #fff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); z-index: 9999; padding: 16px; }
.online-modal-btn { background: #fff; border: 1px solid #ddd; color: #333; padding: 6px 10px; border-radius: 6px; }
.close-btn { background: #fff; border: 1px solid #ddd; color: #333; padding: 4px 8px; border-radius: 6px; cursor: pointer; }
.online-count { font-size: 14px; color: #333; }
.online-indicator { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #20bf6b; margin-left: 6px; animation: pulseOpacity 2s ease-in-out infinite alternate; }
@keyframes pulseOpacity { 0% { opacity: 0.3; } 100% { opacity: 1; } }
.checkbox-label { display: inline-flex; gap: 8px; align-items: center; }
.pretty-checkbox { appearance: none; width: 16px; height: 16px; border: 1px solid #ccc; border-radius: 4px; background: #fff; cursor: pointer; }
.pretty-checkbox:hover { border-color: #20bf6b; }
.pretty-checkbox:checked { background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%); border-color: #20bf6b; }
.toast-container { position: fixed; top: 12px; right: 12px; display: grid; gap: 8px; z-index: 2000; }
.toast { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 8px 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.toast.warning { border-color: #f39c12; }
.toast.success { border-color: #20bf6b; }
.toast.error { border-color: #e74c3c; }
</style>