import { ref } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { LOGIN_MUTATION, REGISTER_MUTATION } from '../graphql/auth';

export function useAuth() {
  const isAuthenticated = ref(false);
  const currentUser = ref(null);
  const authMode = ref('login');
  const authData = ref({ username: '', password: '' });
  const authLoading = ref(false);
  const authError = ref('');

  const { mutate: loginMutation } = useMutation(LOGIN_MUTATION);
  const { mutate: registerMutation } = useMutation(REGISTER_MUTATION);

  const handleAuth = async () => {
    authLoading.value = true;
    authError.value = '';
    try {
      const mutation = authMode.value === 'login' ? loginMutation : registerMutation;
      const result = await mutation({ input: authData.value });
      const authResult = result.data[authMode.value];
      localStorage.setItem('token', authResult.token);
      localStorage.setItem('user', JSON.stringify(authResult.user));
      currentUser.value = authResult.user;
      isAuthenticated.value = true;
    } catch (error) {
      authError.value = error.message || 'Authentication failed';
    } finally {
      authLoading.value = false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    currentUser.value = null;
    isAuthenticated.value = false;
  };

  return { isAuthenticated, currentUser, authMode, authData, authLoading, authError, handleAuth, logout };
}