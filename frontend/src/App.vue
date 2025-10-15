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
        @drag-start="onDragStart"
        @dragging="onDragging"
        @drag-end="onDragEnd"
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
import { useTamagotchiMovement } from "./composables/useTamagotchiMovement";
import AuthScreen from './components/AuthScreen.vue';
import HeaderBar from './components/HeaderBar.vue';
import GameArea from './components/GameArea.vue';
import ControlPanel from './components/ControlPanel.vue';
import OnlineUsersModal from './components/OnlineUsersModal.vue';
import ToastContainer from './components/ToastContainer.vue';
import { useWebSocket } from './composables/useWebSocket';
import { useToasts } from './composables/useToasts';
import { useOnlineModal } from './composables/useOnlineModal';
import { useTamagotchiActions } from './composables/useTamagotchiActions';
import { useAuth } from './composables/useAuth';
import { useGameData } from './composables/useGameData';
import { useSettings } from './composables/useSettings';
import { useUIState } from './composables/useUIState';
import { useInteractions } from './composables/useInteractions';

// GraphQL queries and mutations

export default {
  name: "App",
  setup() {
    // Toasts
    const { toasts, pushToast } = useToasts();

    // Auth
    const { isAuthenticated, currentUser, authMode, authData, authLoading, authError, handleAuth, logout } = useAuth();

    // Game data and realtime
    const { allTamagotchis, allUsers, onlineUsers, hiddenDeadMineIds, otherMousePositions, loadGameData, createTamagotchi: createTamagotchiGD, handleWebSocketMessage } = useGameData(pushToast, currentUser);

    // Movement
    const { positionsById, setTargetPosition, startTracking, stopTracking, cancelTarget } = useTamagotchiMovement(allTamagotchis);

    // Online modal and filters
    const onlineOthers = computed(() => onlineUsers.value.filter((u) => u.id !== currentUser.value?.id));
    const { showOnlineModal, selectedUserIds, showDeadPets, modalStyle, openOnlineModal } = useOnlineModal(onlineOthers);

    // UI state
    const { selectedTamagotchi, newTamagotchiName, showMyKnockedOut, myTamagotchis, onlineOthers: onlineOthersUI, visibleTamagotchis, selectTamagotchi, getOwnerName, displayStatus } = useUIState(
      allTamagotchis,
      allUsers,
      currentUser,
      selectedUserIds,
      showDeadPets,
      hiddenDeadMineIds
    );

    // Actions
    const { feedTamagotchi, playWithTamagotchi, sleepTamagotchi, reviveTamagotchi, releaseTamagotchi, supportTamagotchi } = useTamagotchiActions(allTamagotchis, pushToast);

    // Settings (difficulty)
    const { difficultyOptions, selectedDifficulty, updateDifficulty } = useSettings(currentUser, pushToast);

    // WebSocket
    const { ws, connectWebSocket, close, sendMousePosition, setMessageHandler, flushSave } = useWebSocket(currentUser);
    const onBeforeUnloadFlush = () => { try { flushSave(); } catch (_) {} };

    // Interaction handlers
    const { onSpriteClick, onMouseMove, onDragStart, onDragging, onDragEnd } = useInteractions(
      allTamagotchis,
      positionsById,
      cancelTarget,
      setTargetPosition,
      sendMousePosition,
      selectedTamagotchi
    );
    const onSpriteClickFromChild = onSpriteClick;

    // Orchestration
    watch(isAuthenticated, async (authed) => {
      if (authed) {
        setMessageHandler(handleWebSocketMessage);
        connectWebSocket();
        await loadGameData();
        startTracking();
      } else {
        try { flushSave(); } catch (_) {}
        close();
        stopTracking();
      }
    });

    onMounted(() => {
      window.addEventListener('beforeunload', onBeforeUnloadFlush);
      document.title = "🐾 Multiplayer Tamagotchi 🐾";
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");
      if (token && user) {
        currentUser.value = JSON.parse(user);
        isAuthenticated.value = true;
      }
    });

    onUnmounted(() => {
      try { flushSave(); } catch (_) {}
      close();
      stopTracking();
      window.removeEventListener('beforeunload', onBeforeUnloadFlush);
    });

    const createTamagotchi = async () => {
      if (!newTamagotchiName.value.trim()) return;
      try {
        await createTamagotchiGD(newTamagotchiName.value.trim());
        newTamagotchiName.value = "";
      } catch (e) {
        // already handled
      }
    };

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
      onlineOthers: onlineOthersUI,
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
      onDragStart,
      onDragging,
      onDragEnd,
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
</style>