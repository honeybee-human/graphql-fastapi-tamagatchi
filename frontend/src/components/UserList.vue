<template>
  <div class="online-users">
    <h3>Online Users ({{ users.length }})</h3>
    <div class="user-list">
      <div v-for="user in users" :key="user.id" class="user-item">
        <span class="user-name">{{ user.username }}</span>
        <span v-if="user.id === currentUserId" class="you-badge">YOU</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserList",
  props: {
    users: {
      type: Array,
      required: true,
    },
    currentUserId: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped>
.online-users h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.user-list {
  max-height: 150px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.user-name {
  font-size: 14px;
}

.you-badge {
  background: #28a745;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}
</style>