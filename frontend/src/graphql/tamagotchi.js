import gql from 'graphql-tag';

export const GET_ALL_TAMAGOTCHIS = gql`
  query GetAllTamagotchis {
    allTamagotchis {
      id name ownerId happiness hunger energy health age isAlive status
      position { x y direction speed }
      emoji
    }
  }
`;

export const GET_ALL_USERS = gql`
  query GetAllUsers {
    allUsers { id username isOnline }
  }
`;

export const CREATE_TAMAGOTCHI = gql`
  mutation CreateTamagotchi($input: CreateTamagotchiInput!) {
    createTamagotchi(input: $input) {
      id name ownerId happiness hunger energy health age isAlive status
      position { x y direction speed }
      emoji
    }
  }
`;

export const TAMAGOTCHI_UPDATES_SUBSCRIPTION = gql`
  subscription TamagotchiUpdates {
    tamagotchiUpdates {
      type
      tamagotchi {
        id name ownerId happiness hunger energy health age isAlive status
        position { x y direction speed }
        emoji
      }
      positions { id x y direction }
    }
  }
`;

export const UPDATE_TAMAGOTCHI_LOCATION = gql`
  mutation UpdateTamagotchiLocation($id: ID!, $x: Float!, $y: Float!) {
    updateTamagotchiLocation(id: $id, x: $x, y: $y) {
      id
      position { x y }
    }
  }
`;

export const SUPPORT_TAMAGOTCHI = gql`
  mutation SupportTamagotchi($id: ID!) {
    supportTamagotchi(id: $id) {
      id
      happiness
      hunger
      energy
      health
      isAlive
      status
    }
  }
`;