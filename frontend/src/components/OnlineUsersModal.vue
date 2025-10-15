<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal anchored" :style="modalStyle">
      <div class="modal-header">
        <h3>Online Users</h3>
        <button class="close-btn" @click="$emit('close')">✖</button>
      </div>
      <div class="modal-body">
        <div class="filter-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="localShowDeadPets" class="pretty-checkbox" />
            <span>show other users' knocked out pets?</span>
          </label>
        </div>
        <div class="user-toggle-list">
          <div v-for="user in onlineOthers" :key="user.id" class="toggle-item">
            <label class="checkbox-label">
              <input type="checkbox" :value="user.id" v-model="localSelectedUserIds" class="pretty-checkbox" />
              <span>{{ user.username }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OnlineUsersModal',
  props: {
    onlineOthers: { type: Array, required: true },
    selectedUserIds: { type: Array, required: true },
    showDeadPets: { type: Boolean, required: true },
    modalStyle: { type: Object, default: () => ({}) },
  },
  emits: ['close', 'update:selectedUserIds', 'update:showDeadPets'],
  data() {
    return {
      localSelectedUserIds: [...this.selectedUserIds],
      localShowDeadPets: this.showDeadPets,
    };
  },
  watch: {
    localSelectedUserIds(n) { this.$emit('update:selectedUserIds', n); },
    localShowDeadPets(n) { this.$emit('update:showDeadPets', n); },
    selectedUserIds(n) { this.localSelectedUserIds = [...n]; },
    showDeadPets(n) { this.localShowDeadPets = n; },
  },
};
</script>