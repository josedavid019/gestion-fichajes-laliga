const API_URL = "http://127.0.0.1:8000/api";

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
  async register(
    email: string,
    first_name: string,
    last_name: string,
    password: string,
    password_confirm: string
  ): Promise<AuthResponse> {
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
  }

  async login(email: string, password: string): Promise<AuthResponse> {
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

    return response.json();
  }

  async logout(): Promise<void> {
    await fetch(`${API_URL}/auth/logout/`, {
      method: "POST",
      credentials: "include",
    });
  }

  async checkAuth(): Promise<AuthCheckResponse> {
    const response = await fetch(`${API_URL}/auth/check-auth/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to check authentication");
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_URL}/auth/me/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch current user");
    }

    return response.json();
  }
}

export const authService = new AuthService();
