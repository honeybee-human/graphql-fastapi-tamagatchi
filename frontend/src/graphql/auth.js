import gql from 'graphql-tag';

export const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      user { id username createdAt difficulty }
    }
  }
`;

export const REGISTER_MUTATION = gql`
  mutation Register($input: CreateUserInput!) {
    register(input: $input) {
      token
      user { id username createdAt difficulty }
    }
  }
`;

export const SET_DIFFICULTY = gql`
  mutation SetDifficulty($difficulty: Float!) {
    setDifficulty(difficulty: $difficulty) {
      id
      username
      difficulty
    }
  }
`;