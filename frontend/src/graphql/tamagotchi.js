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

export const REVIVE_TAMAGOTCHI = gql`
  mutation ReviveTamagotchi($id: ID!) {
    reviveTamagotchi(id: $id) {
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

export const RELEASE_TAMAGOTCHI = gql`
  mutation ReleaseTamagotchi($id: ID!) {
    releaseTamagotchi(id: $id)
  }
`;

export const FEED_TAMAGOTCHI = gql`
  mutation FeedTamagotchi($id: ID!) {
    feedTamagotchi(id: $id) {
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

export const PLAY_TAMAGOTCHI = gql`
  mutation PlayTamagotchi($id: ID!) {
    playTamagotchi(id: $id) {
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

export const SLEEP_TAMAGOTCHI = gql`
  mutation SleepTamagotchi($id: ID!) {
    sleepTamagotchi(id: $id) {
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