import { createApp } from 'vue'
import App from './App.vue'
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client/core'
import { setContext } from '@apollo/client/link/context'
import { DefaultApolloClient } from '@vue/apollo-composable'

// HTTP link - connect directly to backend in dev
const httpLink = createHttpLink({
  uri: 'http://127.0.0.1:8000/graphql',
})

// Auth link to add JWT token to headers
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token')
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  }
})

// Apollo client setup with auth link
const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
})

const app = createApp(App)
app.provide(DefaultApolloClient, apolloClient)
app.mount('#app')