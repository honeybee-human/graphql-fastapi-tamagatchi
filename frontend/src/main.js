import { createApp } from 'vue'
import App from './App.vue'
import './styles/base.css'
import { ApolloClient, InMemoryCache, createHttpLink, split } from '@apollo/client/core'
import { setContext } from '@apollo/client/link/context'
import { getMainDefinition } from '@apollo/client/utilities'
import { GraphQLWsLink } from '@apollo/client/link/subscriptions'
import { createClient } from 'graphql-ws'
import { DefaultApolloClient } from '@vue/apollo-composable'

const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql',
})

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token')
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  }
})

// Create a WebSocket link for subscriptions
const wsLink = new GraphQLWsLink(createClient({
  url: 'ws://localhost:8000/graphql',
  connectionParams: () => {
    const token = localStorage.getItem('token')
    return {
      Authorization: token ? `Bearer ${token}` : "",
    }
  },
}))

// Use the split function to direct traffic based on operation type
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  authLink.concat(httpLink)
);

const apolloClient = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
})

const app = createApp(App)
app.provide(DefaultApolloClient, apolloClient)
app.mount('#app')