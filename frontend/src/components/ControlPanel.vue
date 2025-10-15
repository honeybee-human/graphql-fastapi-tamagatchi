<template>
  <div class="control-panel">
    <!-- Create section -->
    <section class="create-section">
      <h2>Create New Tamagotchi</h2>
      <div class="input-group">
        <input
          type="text"
          placeholder="Enter name"
          :value="newTamagotchiName"
          @input="$emit('update:newTamagotchiName', $event.target.value)"
        />
        <button class="btn create" @click="$emit('create-tamagotchi')">Create</button>
      </div>

      <div class="filters">
        <label>
          <input type="checkbox" :checked="showMyKnockedOut" @change="$emit('update:showMyKnockedOut', $event.target.checked)" />
          Show my knocked out
        </label>
      </div>

      <div class="previous-names" v-if="myTamagotchis && myTamagotchis.length">
        <h3>Previous Pets</h3>
        <div class="tamagotchi-list">
          <button
            v-for="pet in myTamagotchis"
            :key="pet.id"
            class="details-btn"
            @click="$emit('select-tamagotchi', pet)"
          >
            {{ pet.name }} {{ pet.isAlive ? '' : '💀' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Owner info and difficulty -->
    <section class="owner-info" v-if="currentUser">
      <div class="info-row">
        <span class="label">Owner:</span>
        <span class="value">{{ currentUser.username }}</span>
      </div>
      <div class="info-row">
        <span class="label">My difficulty:</span>
        <select class="difficulty-select" :value="selectedDifficulty" @change="$emit('update-difficulty', $event.target.value)">
          <option v-for="opt in difficultyOptions" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </div>
    </section>

    <!-- Selected Tamagotchi details -->
    <section class="details-section" v-if="selectedTamagotchi">
      <h2>Selected Tamagotchi</h2>
      <div class="details-card" :class="{ knocked: !selectedTamagotchi.isAlive }">
        <div class="header">
          <span class="emoji">{{ selectedTamagotchi.emoji }}</span>
          <span class="name">{{ selectedTamagotchi.name }}</span>
          <span class="owner" v-if="ownerName">by {{ ownerName }}</span>
        </div>

        <div class="stats">
          <div class="stat-row">
            <span>Hunger</span>
            <div class="stat-bar"><div class="stat-fill hunger" :style="{ width: `${selectedTamagotchi.hunger}%` }"></div><div class="stat-value">{{ selectedTamagotchi.hunger }}</div></div>
          </div>
          <div class="stat-row">
            <span>Fun</span>
            <div class="stat-bar"><div class="stat-fill happiness" :style="{ width: `${selectedTamagotchi.happiness}%` }"></div><div class="stat-value">{{ selectedTamagotchi.happiness }}</div></div>
          </div>
          <div class="stat-row">
            <span>Health</span>
            <div class="stat-bar"><div class="stat-fill health" :style="{ width: `${selectedTamagotchi.health}%` }"></div><div class="stat-value">{{ selectedTamagotchi.health }}</div></div>
          </div>
          <div class="stat-row">
            <span>Energy</span>
            <div class="stat-bar"><div class="stat-fill energy" :style="{ width: `${selectedTamagotchi.energy}%` }"></div><div class="stat-value">{{ selectedTamagotchi.energy }}</div></div>
          </div>
        </div>

        <div class="age-info" v-if="selectedTamagotchi.ageSeconds != null">
          <span>Age:</span>
          <span class="value">{{ ageMinutes }}m {{ ageSecondsOnly }}s</span>
        </div>

        <div class="actions">
          <button class="btn feed" :disabled="!canAct" @click="$emit('feed', selectedTamagotchi)">Feed</button>
          <button class="btn play" :disabled="!canAct" @click="$emit('play', selectedTamagotchi)">Play</button>
          <button class="btn sleep" :disabled="!canAct" @click="$emit('sleep', selectedTamagotchi)">Sleep</button>
          <button class="btn heal" v-if="!selectedTamagotchi.isAlive && isOwner" @click="$emit('revive', selectedTamagotchi)">Revive</button>
          <button class="btn remove" v-if="isOwner" @click="$emit('release', selectedTamagotchi)">Release</button>
          <button class="btn support" v-if="!isOwner" :disabled="!selectedTamagotchi.isAlive" @click="$emit('support', selectedTamagotchi)">Support</button>
        </div>

        <p class="not-owner-message" v-if="!isOwner">You are viewing a Tamagotchi you don't own. You can support it!</p>
        <p class="dead-message" v-if="!selectedTamagotchi.isAlive">This Tamagotchi is knocked out. You can revive it if you own it.</p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'ControlPanel',
  props: {
    selectedTamagotchi: { type: Object, required: false, default: null },
    currentUser: { type: Object, required: false, default: null },
    myTamagotchis: { type: Array, required: false, default: () => [] },
    showMyKnockedOut: { type: Boolean, required: false, default: false },
    newTamagotchiName: { type: String, required: false, default: '' },
    difficultyOptions: { type: Array, required: false, default: () => ['EASY','MEDIUM','HARD'] },
    selectedDifficulty: { type: String, required: false, default: 'MEDIUM' },
    allUsers: { type: Array, required: false, default: () => [] }
  },
  emits: [
    'update:showMyKnockedOut',
    'update:newTamagotchiName',
    'create-tamagotchi',
    'update-difficulty',
    'select-tamagotchi',
    'feed','play','sleep','revive','release','support'
  ],
  computed: {
    isOwner() {
      return this.currentUser && this.selectedTamagotchi && this.selectedTamagotchi.ownerId === this.currentUser.id;
    },
    canAct() {
      return this.selectedTamagotchi && this.selectedTamagotchi.isAlive && this.isOwner;
    },
    ownerName() {
      if (!this.selectedTamagotchi || !this.allUsers) return '';
      const owner = this.allUsers.find(u => u.id === this.selectedTamagotchi.ownerId);
      return owner ? owner.username : '';
    },
    ageMinutes() {
      const s = this.selectedTamagotchi?.ageSeconds ?? 0;
      return Math.floor(s / 60);
    },
    ageSecondsOnly() {
      const s = this.selectedTamagotchi?.ageSeconds ?? 0;
      return s % 60;
    }
  }
};
</script>