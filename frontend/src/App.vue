<template>
  <div id="app">
    <div class="container">
      <h1>🐾 Tamagotchi Game 🐾</h1>
      
      <!-- Create new Tamagotchi -->
      <div v-if="!selectedTamagotchi" class="create-section">
        <h2>Create Your Tamagotchi</h2>
        <div class="input-group">
          <input 
            v-model="newTamagotchiName" 
            placeholder="Enter your Tamagotchi's name"
            @keyup.enter="createTamagotchi"
          />
          <button @click="createTamagotchi" :disabled="!newTamagotchiName.trim()">
            Create
          </button>
        </div>
      </div>

      <!-- Tamagotchi list -->
      <div v-if="tamagotchis.length > 0" class="tamagotchi-list">
        <h2>Your Tamagotchis</h2>
        <div class="tamagotchi-grid">
          <div 
            v-for="tamagotchi in tamagotchis" 
            :key="tamagotchi.id"
            class="tamagotchi-card"
            :class="{ selected: selectedTamagotchi?.id === tamagotchi.id, dead: !tamagotchi.isAlive }"
            @click="selectTamagotchi(tamagotchi)"
          >
            <h3>{{ tamagotchi.name }}</h3>
            <div class="status">{{ tamagotchi.status }}</div>
            <div class="age">Age: {{ tamagotchi.age }}h</div>
          </div>
        </div>
      </div>

      <!-- Selected Tamagotchi details -->
      <div v-if="selectedTamagotchi" class="tamagotchi-details">
        <button class="back-btn" @click="selectedTamagotchi = null">← Back to List</button>
        
        <div class="tamagotchi-main">
          <div class="tamagotchi-avatar">
            <div class="pet-emoji">{{ getPetEmoji(selectedTamagotchi) }}</div>
            <h2>{{ selectedTamagotchi.name }}</h2>
            <div class="status-badge" :class="selectedTamagotchi.status.toLowerCase()">
              {{ selectedTamagotchi.status }}
            </div>
          </div>

          <div class="stats">
            <div class="stat">
              <label>❤️ Happiness</label>
              <div class="stat-bar">
                <div class="stat-fill happiness" :style="{ width: selectedTamagotchi.happiness + '%' }"></div>
              </div>
              <span>{{ selectedTamagotchi.happiness }}/100</span>
            </div>

            <div class="stat">
              <label>🍎 Hunger</label>
              <div class="stat-bar">
                <div class="stat-fill hunger" :style="{ width: selectedTamagotchi.hunger + '%' }"></div>
              </div>
              <span>{{ selectedTamagotchi.hunger }}/100</span>
            </div>

            <div class="stat">
              <label>⚡ Energy</label>
              <div class="stat-bar">
                <div class="stat-fill energy" :style="{ width: selectedTamagotchi.energy + '%' }"></div>
              </div>
              <span>{{ selectedTamagotchi.energy }}/100</span>
            </div>

            <div class="stat">
              <label>💚 Health</label>
              <div class="stat-bar">
                <div class="stat-fill health" :style="{ width: selectedTamagotchi.health + '%' }"></div>
              </div>
              <span>{{ selectedTamagotchi.health }}/100</span>
            </div>
          </div>

          <div v-if="selectedTamagotchi.isAlive" class="actions">
            <button @click="feedTamagotchi" class="action-btn feed">🍎 Feed</button>
            <button @click="playWithTamagotchi" class="action-btn play">🎮 Play</button>
            <button @click="sleepTamagotchi" class="action-btn sleep">😴 Sleep</button>
          </div>
          
          <div v-else class="dead-message">
            💀 Your Tamagotchi has died. Take better care next time!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useQuery, useMutation } from '@vue/apollo-composable'
import gql from 'graphql-tag'

const GET_ALL_TAMAGOTCHIS = gql`
  query GetAllTamagotchis {
    allTamagotchis {
      id
      name
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
    }
  }
`

const CREATE_TAMAGOTCHI = gql`
  mutation CreateTamagotchi($input: CreateTamagotchiInput!) {
    createTamagotchi(input: $input) {
      id
      name
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
    }
  }
`

const FEED_TAMAGOTCHI = gql`
  mutation FeedTamagotchi($input: ActionInput!) {
    feedTamagotchi(input: $input) {
      id
      name
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
    }
  }
`

const PLAY_WITH_TAMAGOTCHI = gql`
  mutation PlayWithTamagotchi($input: ActionInput!) {
    playWithTamagotchi(input: $input) {
      id
      name
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
    }
  }
`

const SLEEP_TAMAGOTCHI = gql`
  mutation SleepTamagotchi($input: ActionInput!) {
    sleepTamagotchi(input: $input) {
      id
      name
      happiness
      hunger
      energy
      health
      age
      isAlive
      status
    }
  }
`

export default {
  name: 'App',
  setup() {
    const newTamagotchiName = ref('')
    const selectedTamagotchi = ref(null)
    
    const { result, refetch } = useQuery(GET_ALL_TAMAGOTCHIS)
    const tamagotchis = ref([])
    
    const { mutate: createTamagotchiMutation } = useMutation(CREATE_TAMAGOTCHI)
    const { mutate: feedTamagotchiMutation } = useMutation(FEED_TAMAGOTCHI)
    const { mutate: playWithTamagotchiMutation } = useMutation(PLAY_WITH_TAMAGOTCHI)
    const { mutate: sleepTamagotchiMutation } = useMutation(SLEEP_TAMAGOTCHI)
    
    const loadTamagotchis = async () => {
      await refetch()
      if (result.value?.allTamagotchis) {
        tamagotchis.value = result.value.allTamagotchis
      }
    }
    
    const createTamagotchi = async () => {
      if (!newTamagotchiName.value.trim()) return
      
      try {
        await createTamagotchiMutation({
          input: { name: newTamagotchiName.value.trim() }
        })
        newTamagotchiName.value = ''
        await loadTamagotchis()
      } catch (error) {
        console.error('Error creating Tamagotchi:', error)
      }
    }
    
    const selectTamagotchi = (tamagotchi) => {
      selectedTamagotchi.value = tamagotchi
    }
    
    const feedTamagotchi = async () => {
      if (!selectedTamagotchi.value) return
      
      try {
        const result = await feedTamagotchiMutation({
          input: { tamagotchiId: selectedTamagotchi.value.id }
        })
        if (result.data?.feedTamagotchi) {
          selectedTamagotchi.value = result.data.feedTamagotchi
        }
        await loadTamagotchis()
      } catch (error) {
        console.error('Error feeding Tamagotchi:', error)
      }
    }
    
    const playWithTamagotchi = async () => {
      if (!selectedTamagotchi.value) return
      
      try {
        const result = await playWithTamagotchiMutation({
          input: { tamagotchiId: selectedTamagotchi.value.id }
        })
        if (result.data?.playWithTamagotchi) {
          selectedTamagotchi.value = result.data.playWithTamagotchi
        }
        await loadTamagotchis()
      } catch (error) {
        console.error('Error playing with Tamagotchi:', error)
      }
    }
    
    const sleepTamagotchi = async () => {
      if (!selectedTamagotchi.value) return
      
      try {
        const result = await sleepTamagotchiMutation({
          input: { tamagotchiId: selectedTamagotchi.value.id }
        })
        if (result.data?.sleepTamagotchi) {
          selectedTamagotchi.value = result.data.sleepTamagotchi
        }
        await loadTamagotchis()
      } catch (error) {
        console.error('Error making Tamagotchi sleep:', error)
      }
    }
    
    const getPetEmoji = (tamagotchi) => {
      if (!tamagotchi.isAlive) return '💀'
      if (tamagotchi.happiness > 80) return '😊'
      if (tamagotchi.happiness > 60) return '🙂'
      if (tamagotchi.happiness > 40) return '😐'
      if (tamagotchi.happiness > 20) return '😟'
      return '😢'
    }
    
    onMounted(() => {
      loadTamagotchis()
      // Auto-refresh every 30 seconds
      setInterval(loadTamagotchis, 30000)
    })
    
    return {
      newTamagotchiName,
      selectedTamagotchi,
      tamagotchis,
      createTamagotchi,
      selectTamagotchi,
      feedTamagotchi,
      playWithTamagotchi,
      sleepTamagotchi,
      getPetEmoji
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2.5em;
}

h2 {
  color: #555;
  margin-bottom: 20px;
}

.create-section {
  text-align: center;
  margin-bottom: 30px;
}

.input-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

input {
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  min-width: 200px;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

button {
  padding: 12px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

button:hover {
  background: #5a6fd8;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.tamagotchi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.tamagotchi-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.tamagotchi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.tamagotchi-card.selected {
  border-color: #667eea;
  background: #f0f2ff;
}

.tamagotchi-card.dead {
  background: #f8d7da;
  border-color: #f5c6cb;
}

.tamagotchi-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.status {
  font-weight: bold;
  margin-bottom: 5px;
}

.age {
  color: #666;
  font-size: 14px;
}

.tamagotchi-details {
  margin-top: 30px;
}

.back-btn {
  background: #6c757d;
  margin-bottom: 20px;
}

.back-btn:hover {
  background: #5a6268;
}

.tamagotchi-main {
  text-align: center;
}

.tamagotchi-avatar {
  margin-bottom: 30px;
}

.pet-emoji {
  font-size: 80px;
  margin-bottom: 15px;
}

.status-badge {
  display: inline-block;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 12px;
}

.status-badge.happy {
  background: #d4edda;
  color: #155724;
}

.status-badge.sad {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.tired {
  background: #fff3cd;
  color: #856404;
}

.status-badge.starving {
  background: #f5c6cb;
  color: #721c24;
}

.status-badge.dead {
  background: #343a40;
  color: white;
}

.stats {
  margin: 30px 0;
}

.stat {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 15px;
}

.stat label {
  min-width: 100px;
  font-weight: bold;
}

.stat-bar {
  flex: 1;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  transition: width 0.3s;
}

.stat-fill.happiness {
  background: linear-gradient(90deg, #ff6b6b, #feca57);
}

.stat-fill.hunger {
  background: linear-gradient(90deg, #48dbfb, #ff6b6b);
}

.stat-fill.energy {
  background: linear-gradient(90deg, #0abde3, #006ba6);
}

.stat-fill.health {
  background: linear-gradient(90deg, #26de81, #20bf6b);
}

.stat span {
  min-width: 60px;
  text-align: right;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.action-btn {
  padding: 15px 25px;
  font-size: 18px;
  border-radius: 15px;
}

.action-btn.feed {
  background: #26de81;
}

.action-btn.feed:hover {
  background: #20bf6b;
}

.action-btn.play {
  background: #feca57;
}

.action-btn.play:hover {
  background: #ff9ff3;
}

.action-btn.sleep {
  background: #a55eea;
}

.action-btn.sleep:hover {
  background: #8854d0;
}

.dead-message {
  background: #f8d7da;
  color: #721c24;
  padding: 20px;
  border-radius: 10px;
  margin-top: 20px;
  font-weight: bold;
}

@media (max-width: 600px) {
  .container {
    padding: 20px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .stat {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
  }
  
  .stat label {
    min-width: auto;
  }
}
</style>