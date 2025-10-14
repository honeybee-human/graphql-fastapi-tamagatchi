import { ref, computed, watch } from 'vue';
import { useQuery, useMutation, useSubscription } from '@vue/apollo-composable';
import { GET_ALL_TAMAGOTCHIS, GET_ALL_USERS, CREATE_TAMAGOTCHI, TAMAGOTCHI_UPDATES_SUBSCRIPTION } from '../graphql/tamagotchi';

export function useGame() {
  const allTamagotchis = ref([]);
  const allUsers = ref([]);
  const selectedTamagotchi = ref(null);
  const newTamagotchiName = ref('');
  const otherMousePositions = ref([]);

  const onlineUsers = computed(() => allUsers.value.filter((u) => u.isOnline));

  const { result: tamagotchisResult, refetch: refetchTamagotchis } = useQuery(GET_ALL_TAMAGOTCHIS);
  const { result: usersResult, refetch: refetchUsers } = useQuery(GET_ALL_USERS);
  const { mutate: createTamagotchiMutation } = useMutation(CREATE_TAMAGOTCHI);
  const { result: subscriptionResult } = useSubscription(TAMAGOTCHI_UPDATES_SUBSCRIPTION);

  watch(tamagotchisResult, (res) => { if (res?.allTamagotchis) allTamagotchis.value = res.allTamagotchis; });
  watch(usersResult, (res) => { if (res?.allUsers) allUsers.value = res.allUsers; });

  watch(subscriptionResult, (newResult) => {
    if (newResult?.tamagotchiUpdates) {
      const update = newResult.tamagotchiUpdates;
      switch (update.type) {
        case 'stats_update':
          if (update.tamagotchi) {
            const u = update.tamagotchi;
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
          }
          break;
        case 'position_update':
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
        case 'tamagotchi_created':
          if (update.tamagotchi && !allTamagotchis.value.find((t) => t.id === update.tamagotchi.id)) {
            allTamagotchis.value = [...allTamagotchis.value, update.tamagotchi];
          }
          break;
      }
    }
  });

  const loadGameData = async () => {
    await Promise.all([refetchTamagotchis(), refetchUsers()]);
  };

  const createTamagotchi = async () => {
    if (!newTamagotchiName.value.trim()) return;
    await createTamagotchiMutation({ input: { name: newTamagotchiName.value } });
    newTamagotchiName.value = '';
    await loadGameData();
  };

  const selectTamagotchi = (t) => { selectedTamagotchi.value = t; };

  return { allTamagotchis, allUsers, selectedTamagotchi, newTamagotchiName, otherMousePositions, onlineUsers, loadGameData, createTamagotchi, selectTamagotchi };
}