const API_URL = "http://127.0.0.1:8000/api";

// Import mock users for development
import { MOCK_USERS, findMockUser } from "./mockUsers";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
}

export interface AuthResponse {
  message: string;
  user: User;
}

export interface AuthCheckResponse {
  authenticated: boolean;
  user?: User;
}

class AuthService {
  private readonly STORAGE_KEY = "auth_user";
  private readonly MOCK_MODE = "mock_mode";

  async register(
    email: string,
    first_name: string,
    last_name: string,
    password: string,
    password_confirm: string,
  ): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_URL}/auth/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          first_name,
          last_name,
          password,
          password_confirm,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(JSON.stringify(error));
      }

      return response.json();
    } catch (error) {
      // Fallback to mock mode if backend is not available
      console.warn("Backend not available, using mock mode for testing", error);

      // Check if user already exists in mock data
      if (MOCK_USERS.some((u) => u.email === email)) {
        throw new Error(
          JSON.stringify({ email: "Este email ya está registrado." }),
        );
      }

      const newMockUser: User = {
        id: MOCK_USERS.length + 1,
        email,
        first_name,
        last_name,
        is_active: true,
        date_joined: new Date().toISOString(),
      };

      // Save to localStorage for mock mode
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newMockUser));
      localStorage.setItem(this.MOCK_MODE, "true");

      return {
        message: "Usuario registrado exitosamente (modo prueba)",
        user: newMockUser,
      };
    }
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_URL}/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(JSON.stringify(error));
      }

      const data = await response.json();
      localStorage.removeItem(this.MOCK_MODE);
      return data;
    } catch (error) {
      // Fallback to mock mode if backend is not available
      console.warn("Backend not available, using mock mode for testing", error);

      const user = findMockUser(email, password);
      if (!user) {
        throw new Error("Email o contraseña incorrectos.");
      }

      // Save to localStorage for mock mode
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(user));
      localStorage.setItem(this.MOCK_MODE, "true");

      return {
        message: "Autenticación exitosa (modo prueba)",
        user,
      };
    }
  }

  async logout(): Promise<void> {
    try {
      await fetch(`${API_URL}/auth/logout/`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.warn("Logout error (mock mode)", error);
    }

    localStorage.removeItem(this.STORAGE_KEY);
    localStorage.removeItem(this.MOCK_MODE);
  }

  async checkAuth(): Promise<AuthCheckResponse> {
    // First check localStorage for mock mode
    const mockUser = localStorage.getItem(this.STORAGE_KEY);
    if (mockUser) {
      return {
        authenticated: true,
        user: JSON.parse(mockUser),
      };
    }

    try {
      const response = await fetch(`${API_URL}/auth/check-auth/`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to check authentication");
      }

      return response.json();
    } catch (error) {
      console.warn("Check auth error", error);
      return { authenticated: false };
    }
  }

  async getCurrentUser(): Promise<User> {
    // First check localStorage for mock mode
    const mockUser = localStorage.getItem(this.STORAGE_KEY);
    if (mockUser) {
      return JSON.parse(mockUser);
    }

    try {
      const response = await fetch(`${API_URL}/auth/me/`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch current user");
      }

      return response.json();
    } catch (error) {
      throw new Error("Failed to fetch current user");
    }
  }
}

export const authService = new AuthService();
