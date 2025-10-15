import { ref } from 'vue';

export function useToasts(ttlMs = 5000) {
  const toasts = ref([]);

  const pushToast = (message, type = 'info') => {
    const id = Math.random().toString(36).slice(2);
    toasts.value = [...toasts.value, { id, message, type }];
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id);
    }, ttlMs);
  };

  return { toasts, pushToast };
}