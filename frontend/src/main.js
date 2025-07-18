import { createApp } from 'vue'
import App from './App.vue'
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client/core'
import { DefaultApolloClient } from '@vue/apollo-composable'

// Apollo client setup
const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql',
})

const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
})

const app = createApp(App)
app.provide(DefaultApolloClient, apolloClient)
app.mount('#app')