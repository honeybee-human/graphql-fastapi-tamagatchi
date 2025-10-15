import { ref, computed, watch } from 'vue';

// Tracks UI state: selected pet, form inputs, filters, and derived lists
export function useUIState(allTamagotchis, allUsers, currentUser, selectedUserIds, showDeadPets, hiddenDeadMineIds) {
  const selectedTamagotchi = ref(null);
  const newTamagotchiName = ref('');
  const showMyKnockedOut = ref(false);

  const myTamagotchis = computed(() => allTamagotchis.value.filter((t) => t.ownerId === currentUser.value?.id));

  const onlineUsers = computed(() => allUsers.value.filter((user) => user.isOnline));
  const onlineOthers = computed(() => onlineUsers.value.filter((u) => u.id !== currentUser.value?.id));

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

  const selectTamagotchi = (t) => { selectedTamagotchi.value = t; };

  // Keep selected pet matched with live list updates
  watch(allTamagotchis, (list) => {
    const sel = selectedTamagotchi.value;
    if (!sel) return;
    const updated = list.find((t) => t.id === sel.id);
    if (updated) selectedTamagotchi.value = updated;
  });

  const getOwnerName = (ownerId) => {
    const owner = allUsers.value.find((user) => user.id === ownerId);
    return owner ? owner.username : 'Unknown';
  };

  const displayStatus = (status) => (status === 'Dead' ? 'Knocked Out' : status);

  return {
    selectedTamagotchi,
    newTamagotchiName,
    showMyKnockedOut,
    myTamagotchis,
    onlineOthers,
    visibleTamagotchis,
    selectTamagotchi,
    getOwnerName,
    displayStatus,
  };
}