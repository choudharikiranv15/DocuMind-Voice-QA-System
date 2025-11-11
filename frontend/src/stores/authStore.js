import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      // Login function
      login: async (email, password) => {
        try {
          const response = await api.post('/auth/login', { email, password });

          if (response.data.success) {
            const { token, user } = response.data;
            set({
              user,
              token,
              isAuthenticated: true
            });

            // Set token in API headers for future requests
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

            return { success: true };
          }

          return { success: false, message: response.data.message };
        } catch (error) {
          const message = error.response?.data?.message || 'Login failed';
          return { success: false, message };
        }
      },

      // Signup function
      signup: async (email, password) => {
        try {
          const response = await api.post('/auth/signup', { email, password });

          if (response.data.success) {
            const { token, user } = response.data;
            set({
              user,
              token,
              isAuthenticated: true
            });

            // Set token in API headers
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

            return { success: true };
          }

          return { success: false, message: response.data.message };
        } catch (error) {
          const message = error.response?.data?.message || 'Signup failed';
          return { success: false, message };
        }
      },

      // Logout function
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        });

        // Remove token from API headers
        delete api.defaults.headers.common['Authorization'];
      },

      // Initialize auth on app load
      initializeAuth: () => {
        const { token } = get();
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
      }
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

export default useAuthStore;
