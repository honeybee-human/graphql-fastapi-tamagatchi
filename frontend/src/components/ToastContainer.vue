<template>
  <div class="toast-container">
    <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script>
export default {
  name: 'ToastContainer',
  props: { toasts: { type: Array, default: () => [] } },
};
</script>