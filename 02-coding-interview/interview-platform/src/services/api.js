import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service for backend communication
export const apiService = {
  // Create a new interview session
  // Returns: { sessionId, joinUrl }
  async createSession() {
    try {
      const response = await apiClient.post('/sessions');
      return response.data;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  },

  // Get session information
  // Returns: { sessionId, code, language, participants, createdAt }
  async getSession(sessionId) {
    try {
      const response = await apiClient.get(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching session:', error);
      throw error;
    }
  },

  // Get list of supported languages
  // Returns: Array of language objects
  async getLanguages() {
    try {
      const response = await apiClient.get('/languages');
      return response.data;
    } catch (error) {
      console.error('Error fetching languages:', error);
      // Return local languages as fallback
      throw error;
    }
  },

  // Execute code on the backend (for languages that can't run in browser)
  // Returns: { output, error, executionTime }
  async executeCode(sessionId, code, language) {
    try {
      const response = await apiClient.post(`/sessions/${sessionId}/execute`, {
        code,
        language,
      });
      return response.data;
    } catch (error) {
      console.error('Error executing code:', error);
      throw error;
    }
  },
};
