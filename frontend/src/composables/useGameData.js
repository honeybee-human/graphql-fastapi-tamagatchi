import { ref, computed, watch } from 'vue';
import { useQuery, useMutation, useSubscription } from '@vue/apollo-composable';
import { GET_ALL_TAMAGOTCHIS, GET_ALL_USERS, CREATE_TAMAGOTCHI, TAMAGOTCHI_UPDATES_SUBSCRIPTION } from '../graphql/tamagotchi';

// Handles GraphQL queries, subscriptions, refetch logic, and realtime message mapping
export function useGameData(pushToast, currentUser) {
  const allTamagotchis = ref([]);
  const allUsers = ref([]);
  const hiddenDeadMineIds = ref(new Set());
  const otherMousePositions = ref([]);

  const onlineUsers = computed(() => allUsers.value.filter((u) => u.isOnline));

  // Queries
  const { result: tamagotchisResult, refetch: refetchTamagotchis } = useQuery(GET_ALL_TAMAGOTCHIS);
  const { result: usersResult, refetch: refetchUsers } = useQuery(GET_ALL_USERS);
  const { mutate: createTamagotchiMutation } = useMutation(CREATE_TAMAGOTCHI);

  // Subscriptions
  const { result: subscriptionResult } = useSubscription(TAMAGOTCHI_UPDATES_SUBSCRIPTION);

  // Seed from queries
  watch(tamagotchisResult, (res) => {
    if (res?.allTamagotchis) {
      allTamagotchis.value = res.allTamagotchis.map((t) => ({
        ...t,
        position: t.position ? { ...t.position } : undefined,
      }));
    }
  });

  watch(usersResult, (res) => {
    if (res?.allUsers) {
      allUsers.value = [...res.allUsers];
    }
  });

  // Real-time updates from GraphQL subscriptions
  watch(subscriptionResult, (newResult) => {
    if (!newResult?.tamagotchiUpdates) return;
    const update = newResult.tamagotchiUpdates;

    switch (update.type) {
      case 'stats_update': {
        const u = update.tamagotchi;
        if (!u) break;
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
        // Knockout notification
        if (prev && prev.isAlive && !u.isAlive) {
          if (prev.ownerId === currentUser.value?.id) {
            setTimeout(() => { hiddenDeadMineIds.value.add(prev.id); }, 3000);
          }
          pushToast?.(`your pet ${prev.name} is knocked out!`, 'warning');
        }
        break;
      }
      case 'position_update': {
        if (update.positions) {
          const posById = new Map(update.positions.map((p) => [p.id, p]));
          allTamagotchis.value = allTamagotchis.value.map((t) => {
            const p = posById.get(t.id);
            if (!p) return t;
            const prev = t.position || {};
            return { ...t, position: { ...prev, x: p.x, y: p.y, direction: p.direction } };
          });
        }
        break;
      }
      case 'tamagotchi_created': {
        const nt = update.tamagotchi;
        if (nt && !allTamagotchis.value.find((t) => t.id === nt.id)) {
          allTamagotchis.value.push({ ...nt, position: nt.position ? { ...nt.position } : undefined });
        }
        break;
      }
      case 'tamagotchi_removed': {
        const id = update.id;
        if (id) {
          allTamagotchis.value = allTamagotchis.value.filter((t) => t.id !== id);
        }
        break;
      }
    }
  });

  const loadGameData = async () => {
    await refetchTamagotchis();
    await refetchUsers();
  };

  const createTamagotchi = async (name) => {
    if (!name || !name.trim()) return;
    await createTamagotchiMutation({ input: { name: name.trim() } });
    await loadGameData();
  };

  // WebSocket message handler (kept out of App.vue)
  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'tamagotchi_created': {
        const t = message.tamagotchi;
        if (t && !allTamagotchis.value.some((x) => x.id === t.id)) {
          allTamagotchis.value = [...allTamagotchis.value, t];
        }
        break;
      }
      case 'stats_update': {
        const items = Array.isArray(message.tamagotchis) ? message.tamagotchis : [];
        const single = message.tamagotchi || null;
        const map = new Map(items.map((u) => [u.id, u]));
        const before = new Map(allTamagotchis.value.map((t) => [t.id, t]));
        if (items.length) {
          allTamagotchis.value = allTamagotchis.value.map((t) => {
            const u = map.get(t.id);
            if (!u) return t;
            const nextAlive = u.isAlive ?? u.is_alive ?? t.isAlive;
            const next = {
              ...t,
              ...u,
              isAlive: nextAlive,
              position: u.position
                ? { ...u.position }
                : t.position
                ? { ...t.position }
                : undefined,
            };
            return next;
          });
        }
        if (single) {
          const u = single;
          const nextAlive = u.isAlive ?? u.is_alive;
          allTamagotchis.value = allTamagotchis.value.map((t) =>
            t.id === u.id
              ? {
                  ...t,
                  ...u,
                  isAlive: nextAlive,
                  position: u.position
                    ? { ...u.position }
                    : t.position
                    ? { ...t.position }
                    : undefined,
                }
              : t
          );
        }
        // KO notifications
        for (const [id, u] of map.entries()) {
          const prev = before.get(id);
          const nowAlive = u.isAlive ?? u.is_alive;
          if (prev && prev.isAlive && nowAlive === false) {
            if (prev.ownerId === currentUser.value?.id) {
              setTimeout(() => { hiddenDeadMineIds.value.add(prev.id); }, 3000);
            }
            pushToast?.(`your pet ${prev.name} is knocked out!`, 'warning');
          }
        }
        break;
      }
      case 'position_update': {
        if (Array.isArray(message.positions)) {
          const posById = new Map(message.positions.map((p) => [p.id, p]));
          allTamagotchis.value = allTamagotchis.value.map((t) => {
            const p = posById.get(t.id);
            if (!p) return t;
            if (!t.isAlive) return t;
            const prev = t.position || {};
            return { ...t, position: { ...prev, x: p.x, y: p.y, direction: p.direction } };
          });
        }
        break;
      }
      case 'mouse_position': {
        const uid = message?.data?.user_id;
        if (uid && uid !== currentUser.value?.id) {
          const idx = otherMousePositions.value.findIndex((m) => m.user_id === uid);
          if (idx !== -1) {
            otherMousePositions.value = otherMousePositions.value.map((m, i) => (i === idx ? message.data : m));
          } else {
            otherMousePositions.value = [...otherMousePositions.value, message.data];
          }
        }
        break;
      }
      case 'tamagotchi_removed': {
        const id = message.id;
        if (id) {
          allTamagotchis.value = allTamagotchis.value.filter((t) => t.id !== id);
        }
        break;
      }
    }
  };

  return {
    allTamagotchis,
    allUsers,
    onlineUsers,
    hiddenDeadMineIds,
    otherMousePositions,
    loadGameData,
    createTamagotchi,
    handleWebSocketMessage,
  };
}