import { ref, watch } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { SET_DIFFICULTY } from '../graphql/auth';

// Manages difficulty selection and mutation updates
export function useSettings(currentUser, pushToast) {
  const difficultyOptions = [
    { label: 'Easy (0.5x)', value: 0.5 },
    { label: 'Normal (1x)', value: 1.0 },
    { label: 'Hard (1.5x)', value: 1.5 },
    { label: 'Extreme (2x)', value: 2.0 },
  ];

  const selectedDifficulty = ref(1.0);
  const { mutate: setDifficultyMutation } = useMutation(SET_DIFFICULTY);

  const initDifficulty = () => {
    const d = Number(currentUser.value?.difficulty ?? 1.0);
    selectedDifficulty.value = isNaN(d) ? 1.0 : d;
  };

  watch(currentUser, () => initDifficulty(), { immediate: true });

  const updateDifficulty = async () => {
    try {
      const res = await setDifficultyMutation({ difficulty: Number(selectedDifficulty.value) });
      const u = res?.data?.setDifficulty;
      if (u) {
        // Reflect user changes locally
        currentUser.value = { ...(currentUser.value || {}), ...u };
        pushToast?.('difficulty updated', 'success');
      }
    } catch (e) {
      pushToast?.('failed to update difficulty', 'error');
    }
  };

  return { difficultyOptions, selectedDifficulty, updateDifficulty };
}