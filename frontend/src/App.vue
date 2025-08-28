<template>
  <div id="app">
    <AuthComponent v-if="!isAuthenticated" @auth-success="handleAuthSuccess" />

    <div v-else class="game-screen" @mousemove="updateMousePosition">
      <GameHeader :username="currentUser?.username" @logout="logout" />

      <div class="game-area" ref="gameArea">
        <div
          v-for="mouse in otherMousePositions"
          :key="mouse.user_id"
          class="mouse-cursor"
          :style="{ left: mouse.x + 'px', top: mouse.y + 'px' }"
        >
          <div class="cursor-pointer">🖱️</div>
          <div class="cursor-label">{{ mouse.username }}</div>
        </div>

        <TamagotchiSprite
          v-for="tamagotchi in allTamagotchis"
          :key="tamagotchi.id"
          :tamagotchi="tamagotchi"
          :currentUserId="currentUser?.id"
          @select="selectTamagotchi"
          @feed="feedTamagotchi"
          @play="playWithTamagotchi"
          @sleep="sleepTamagotchi"
        />
      </div>

      <div class="control-panel">
        <CreateTamagotchi @create="createTamagotchi" />

        <TamagotchiDetails
          v-if="selectedTamagotchi"
          :tamagotchi="selectedTamagotchi"
          :currentUserId="currentUser?.id"
          :ownerName="getOwnerName(selectedTamagotchi.ownerId)"
          @feed="feedTamagotchi"
          @play="playWithTamagotchi"
          @sleep="sleepTamagotchi"
        />

        <UserList :users="onlineUsers" :currentUserId="currentUser?.id" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useQuery, useMutation, useSubscription } from "@vue/apollo-composable";
import gql from "graphql-tag";

import AuthComponent from "./components/AuthComponent.vue";
import GameHeader from "./components/GameHeader.vue";
import TamagotchiSprite from "./components/TamagotchiSprite.vue";
import TamagotchiDetails from "./components/TamagotchiDetails.vue";
import CreateTamagotchi from "./components/CreateTamagotchi.vue";
import UserList from "./components/UserList.vue";

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
  components: {
    AuthComponent,
    GameHeader,
    TamagotchiSprite,
    TamagotchiDetails,
    CreateTamagotchi,
    UserList,
  },
  setup() {
    const isAuthenticated = ref(false);
    const currentUser = ref(null);
    const allTamagotchis = ref([]);
    const allUsers = ref([]);
    const selectedTamagotchi = ref(null);
    const otherMousePositions = ref([]);

    const ws = ref(null);

    const onlineUsers = computed(() =>
      allUsers.value.filter((user) => user.isOnline)
    );

    const { mutate: createTamagotchiMutation } = useMutation(CREATE_TAMAGOTCHI);

    const { result: tamagotchisResult, refetch: refetchTamagotchis } =
      useQuery(GET_ALL_TAMAGOTCHIS);
    const { result: usersResult, refetch: refetchUsers } =
      useQuery(GET_ALL_USERS);

    const { result: subscriptionResult } = useSubscription(
      TAMAGOTCHI_UPDATES_SUBSCRIPTION
    );

    watch(subscriptionResult, (newResult) => {
      if (newResult?.tamagotchiUpdates) {
        const update = newResult.tamagotchiUpdates;

        switch (update.type) {
          case "stats_update":
            if (update.tamagotchi) {
              const index = allTamagotchis.value.findIndex(
                (t) => t.id === update.tamagotchi.id
              );
              if (index !== -1) {
                Object.assign(allTamagotchis.value[index], update.tamagotchi);
              }
            }
            break;

          case "position_update":
            if (update.positions) {
              update.positions.forEach((pos) => {
                const tamagotchi = allTamagotchis.value.find(
                  (t) => t.id === pos.id
                );
                if (tamagotchi && tamagotchi.position) {
                  tamagotchi.position.x = pos.x;
                  tamagotchi.position.y = pos.y;
                  tamagotchi.position.direction = pos.direction;
                }
              });
            }
            break;

          case "tamagotchi_created":
            if (update.tamagotchi) {
              const exists = allTamagotchis.value.find(
                (t) => t.id === update.tamagotchi.id
              );
              if (!exists) {
                allTamagotchis.value.push(update.tamagotchi);
              }
            }
            break;
        }
      }
    });

    const handleAuthSuccess = (user) => {
      currentUser.value = user;
      isAuthenticated.value = true;
      connectWebSocket();
      loadGameData();
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

    const createTamagotchi = async (name) => {
      try {
        await createTamagotchiMutation({
          input: { name },
        });

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

    const feedTamagotchi = (tamagotchi) => {
      console.log("Feed tamagotchi:", tamagotchi?.id);
    };

    const playWithTamagotchi = (tamagotchi) => {
      console.log("Play with tamagotchi:", tamagotchi?.id);
    };

    const sleepTamagotchi = (tamagotchi) => {
      console.log("Sleep tamagotchi:", tamagotchi?.id);
    };

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
      isAuthenticated,
      currentUser,
      handleAuthSuccess,
      logout,

      allTamagotchis,
      allUsers,
      selectedTamagotchi,
      otherMousePositions,
      onlineUsers,

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

.game-screen {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.game-area {
  flex: 1;
  position: relative;
  background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%);
  overflow: hidden;
  min-height: 600px;
}

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

.control-panel {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

@media (max-width: 1024px) {
  .control-panel {
    grid-template-columns: 1fr;
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .control-panel {
    padding: 15px;
  }

  .actions {
    justify-content: center;
  }
}
</style>
