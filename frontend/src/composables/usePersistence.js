import { watch, onMounted, onBeforeUnmount } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { UPDATE_TAMAGOTCHI_LOCATION } from '../graphql/tamagotchi';

export function useDebouncedPersistence(allTamagotchis, positionsById, delayMs = 30000, intervalMs = 60000) {
  const { mutate: updateLocation } = useMutation(UPDATE_TAMAGOTCHI_LOCATION);
  let timeoutId = null;
  let intervalId = null;

  const saveAllLocations = async () => {
    try {
      for (const t of allTamagotchis.value || []) {
        if (!t.isAlive) continue;
        const pos = positionsById.value?.[t.id];
        if (pos) await updateLocation({ id: t.id, x: pos.x, y: pos.y });
      }
    } catch (e) {
      // swallow errors to avoid UX disruption
      console.warn('saveAllLocations error', e);
    }
  };

  const scheduleSave = () => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(saveAllLocations, delayMs);
  };

  const startAutoSave = () => {
    if (!intervalId) intervalId = setInterval(saveAllLocations, intervalMs);
  };

  const stopAutoSave = () => {
    if (intervalId) { clearInterval(intervalId); intervalId = null; }
    if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; }
  };

  watch(positionsById, () => scheduleSave(), { deep: true });

  onMounted(() => {
    startAutoSave();
    window.addEventListener('beforeunload', saveAllLocations);
  });

  onBeforeUnmount(() => {
    stopAutoSave();
    saveAllLocations();
    window.removeEventListener('beforeunload', saveAllLocations);
  });

  return { saveAllLocations, scheduleSave, startAutoSave, stopAutoSave };
}