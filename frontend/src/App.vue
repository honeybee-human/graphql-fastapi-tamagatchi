<template>
  <div id="app">
    <!-- Login/Register Screen -->
    <AuthScreen
      v-if="!isAuthenticated"
      :auth-mode="authMode"
      :auth-data="authData"
      :auth-loading="authLoading"
      :auth-error="authError"
      @set-auth-mode="val => authMode = val"
      @submit="handleAuth"
    />

    <!-- Game Screen -->
    <div v-else class="game-screen">
      <!-- Header -->
      <HeaderBar
        :current-user="currentUser"
        :selected-difficulty="selectedDifficulty"
        :difficulty-options="difficultyOptions"
        :online-users-count="onlineUsers.length"
        @open-online-modal="openOnlineModal"
        @logout="logout"
        @update-difficulty="val => { selectedDifficulty = val; updateDifficulty(); }"
      />

      <!-- Game Area -->
      <GameArea
        :visible-tamagotchis="visibleTamagotchis"
        :positions-by-id="positionsById"
        :current-user="currentUser"
        :other-mouse-positions="otherMousePositions"
        @sprite-click="onSpriteClickFromChild"
        @mouse-move="onMouseMove"
        @feed="t => feedTamagotchi(t)"
        @play="t => playWithTamagotchi(t)"
        @sleep="t => sleepTamagotchi(t)"
        @revive="t => reviveTamagotchi(t)"
        @release="t => releaseTamagotchi(t)"
        @support="t => supportTamagotchi(t)"
      />

      <!-- Control Panel -->
      <ControlPanel
        :selected-tamagotchi="selectedTamagotchi"
        :current-user="currentUser"
        :my-tamagotchis="myTamagotchis"
        :show-my-knocked-out="showMyKnockedOut"
        :new-tamagotchi-name="newTamagotchiName"
        :difficulty-options="difficultyOptions"
        :selected-difficulty="selectedDifficulty"
        :all-users="allUsers"
        @update:showMyKnockedOut="val => showMyKnockedOut = val"
        @update:newTamagotchiName="val => newTamagotchiName = val"
        @create-tamagotchi="createTamagotchi"
        @update-difficulty="val => { selectedDifficulty = val; updateDifficulty(); }"
        @select-tamagotchi="selectTamagotchi"
        @feed="t => feedTamagotchi(t)"
        @play="t => playWithTamagotchi(t)"
        @sleep="t => sleepTamagotchi(t)"
        @revive="t => reviveTamagotchi(t)"
        @release="t => releaseTamagotchi(t)"
        @support="t => supportTamagotchi(t)"
      />

      <!-- Online Users Modal -->
      <OnlineUsersModal
        v-if="showOnlineModal"
        :online-others="onlineOthers"
        :selected-user-ids="selectedUserIds"
        :show-dead-pets="showDeadPets"
        :modal-style="modalStyle"
        @close="showOnlineModal = false"
        @update:selectedUserIds="val => selectedUserIds = val"
        @update:showDeadPets="val => showDeadPets = val"
      />

      <!-- Toast notifications -->
      <ToastContainer :toasts="toasts" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useQuery, useMutation, useSubscription } from "@vue/apollo-composable";
import { useTamagotchiMovement } from "./composables/useTamagotchiMovement";
import { useDebouncedPersistence } from "./composables/usePersistence";
import AuthScreen from './components/AuthScreen.vue';
import HeaderBar from './components/HeaderBar.vue';
import GameArea from './components/GameArea.vue';
import ControlPanel from './components/ControlPanel.vue';
import OnlineUsersModal from './components/OnlineUsersModal.vue';
import ToastContainer from './components/ToastContainer.vue';
import { useWebSocket } from './composables/useWebSocket';
import { useTamagotchiActions } from './composables/useTamagotchiActions';
import { LOGIN_MUTATION, REGISTER_MUTATION, SET_DIFFICULTY } from './graphql/auth';
import { GET_ALL_TAMAGOTCHIS, GET_ALL_USERS, CREATE_TAMAGOTCHI, TAMAGOTCHI_UPDATES_SUBSCRIPTION } from './graphql/tamagotchi';

// GraphQL queries and mutations

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

    // WebSocket connection handled via composable below

    // Computed properties
    const onlineUsers = computed(() => allUsers.value.filter((user) => user.isOnline));
    const onlineOthers = computed(() => onlineUsers.value.filter((u) => u.id !== currentUser.value?.id));
    const myTamagotchis = computed(() => allTamagotchis.value.filter((t) => t.ownerId === currentUser.value?.id));
    const visibleTamagotchis = computed(() =>
      allTamagotchis.value.filter((t) => {
        const isMine = t.ownerId === currentUser.value?.id;
        const ownerSelected = isMine
          ? true
          : selectedUserIds.value.length === 0
            ? true
            : selectedUserIds.value.includes(t.ownerId);
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
    const { mutate: setDifficultyMutation } = useMutation(SET_DIFFICULTY);

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
        setMessageHandler(handleWebSocketMessage);
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
      close();
    };
    // WebSocket via composable
    const { ws, connectWebSocket, close, sendMousePosition, setMessageHandler } = useWebSocket(currentUser);

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

    const onSpriteClickFromChild = ({ id, x, y }) => { setTargetPosition(id, { x, y }); };
    const onMouseMove = ({ x, y }) => { sendMousePosition(x, y); };

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

    // Action functions now provided by useTamagotchiActions composable

    const openOnlineModal = (rect) => {
      if (showOnlineModal.value) {
        showOnlineModal.value = false;
        return;
      }
      showOnlineModal.value = true;
      const ids = onlineOthers.value.map((u) => u.id);
      if (ids.length && selectedUserIds.value.length === 0) selectedUserIds.value = ids;
      if (rect) { modalStyle.value = { position: 'fixed', top: `${rect.bottom + 6}px`, left: `${rect.left}px` }; }
    };

    // Placeholder action methods (implement with GraphQL mutations)
    // Centralized actions via composable
    const { feedTamagotchi, playWithTamagotchi, sleepTamagotchi, reviveTamagotchi, releaseTamagotchi, supportTamagotchi } = useTamagotchiActions(allTamagotchis, pushToast);

    // Difficulty control
    const difficultyOptions = [
      { label: 'Easy (0.5x)', value: 0.5 },
      { label: 'Normal (1x)', value: 1.0 },
      { label: 'Hard (1.5x)', value: 1.5 },
      { label: 'Extreme (2x)', value: 2.0 },
    ];
    const selectedDifficulty = ref(1.0);
    const initDifficulty = () => {
      const d = Number(currentUser.value?.difficulty ?? 1.0);
      selectedDifficulty.value = isNaN(d) ? 1.0 : d;
    };
    watch(currentUser, () => initDifficulty(), { immediate: true });

    // Keep selected pet panel in sync with real-time updates
    watch(allTamagotchis, (list) => {
      const sel = selectedTamagotchi.value;
      if (!sel) return;
      const updated = list.find((t) => t.id === sel.id);
      if (updated) selectedTamagotchi.value = updated;
    });
    const updateDifficulty = async () => {
      try {
        const res = await setDifficultyMutation({ difficulty: Number(selectedDifficulty.value) });
        const u = res?.data?.setDifficulty;
        if (u) {
          currentUser.value = { ...(currentUser.value || {}), ...u };
          pushToast('difficulty updated', 'success');
        }
      } catch (e) {
        pushToast('failed to update difficulty', 'error');
      }
    };

    // Initialize
    onMounted(() => {
      // Update browser tab title
      document.title = "🐾 Multiplayer Tamagotchi 🐾";
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");

      if (token && user) {
        currentUser.value = JSON.parse(user);
        isAuthenticated.value = true;
        setMessageHandler(handleWebSocketMessage);
        connectWebSocket();
        loadGameData();
      }
      startTracking();
      startAutoSave();
      window.addEventListener('beforeunload', saveAllLocations);
    });

    onUnmounted(() => {
      close();
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
      openOnlineModal,
      modalStyle,
      difficultyOptions,
      selectedDifficulty,
      updateDifficulty,

      // Game methods
      createTamagotchi,
      selectTamagotchi,
      // Movement
      positionsById,
      setTargetPosition,
      onSpriteClickFromChild,
      onMouseMove,
      getOwnerName,
      displayStatus,
      feedTamagotchi,
      playWithTamagotchi,
      sleepTamagotchi,
      reviveTamagotchi,
      releaseTamagotchi,
      supportTamagotchi,
      toasts,
    };
  },
  components: { AuthScreen, HeaderBar, GameArea, ControlPanel, OnlineUsersModal, ToastContainer },
};
</script>

<style lang="scss">
@use './styles/index.scss' as *;
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