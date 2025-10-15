import { ref } from 'vue';

export function useOnlineModal(onlineOthers) {
  const showOnlineModal = ref(false);
  const selectedUserIds = ref([]);
  const showDeadPets = ref(false);
  const modalStyle = ref({ position: 'fixed', top: '80px', left: '20px' });

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

  return { showOnlineModal, selectedUserIds, showDeadPets, modalStyle, openOnlineModal };
}