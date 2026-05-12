import { useCallback, useState, useEffect } from "react";
import { authService } from "@/lib/authService";

const API_URL = "http://127.0.0.1:8000/api";

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  role: "admin" | "director" | "scout" | null;
  phone: string;
  bio: string;
  avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateUserData extends Omit<
  AdminUser,
  "id" | "created_at" | "updated_at" | "avatar"
> {
  avatar?: File | null;
  password?: string;
}

export const useAdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch users from backend
  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/users/`, {
        method: "GET",
        headers: authService.getAuthHeaders(),
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch users: ${response.status}`);
      }

      const data = await response.json();
      setUsers(data);
    } catch (err: any) {
      console.error("Error fetching users:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load users on mount
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Create user
  const createUser = useCallback(
    async (userData: CreateUserData) => {
      try {
        const formData = new FormData();

        // Add basic user data
        formData.append("email", userData.email);
        formData.append("username", userData.username);
        formData.append("first_name", userData.first_name);
        formData.append("last_name", userData.last_name);
        formData.append("is_active", userData.is_active.toString());
        formData.append("is_staff", userData.is_staff.toString());
        formData.append("is_superuser", userData.is_superuser.toString());

        // Add password - use provided password or default
        const password = userData.password || "TempPassword123!";
        formData.append("password", password);

        // Add role if provided
        if (userData.role) {
          formData.append("role", userData.role);
        }

        // Add profile data
        if (userData.phone) {
          formData.append("phone", userData.phone);
        }
        if (userData.bio) {
          formData.append("bio", userData.bio);
        }
        if (userData.avatar) {
          formData.append("avatar", userData.avatar);
        }

        const response = await fetch(`${API_URL}/auth/users/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${authService.getAccessToken()}`,
          },
          credentials: "include",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(JSON.stringify(errorData));
        }

        const newUser = await response.json();
        await fetchUsers();
        return newUser.user || newUser;
      } catch (err: any) {
        console.error("Error creating user:", err);
        throw err;
      }
    },
    [users],
  );

  // Update user
  const updateUser = useCallback(
    async (
      id: number,
      userData: Partial<Omit<AdminUser, "avatar">> & {
        password?: string;
        avatar?: File | null;
      },
    ) => {
      try {
        const formData = new FormData();

        // Add basic user data
        if (userData.email !== undefined)
          formData.append("email", userData.email);
        if (userData.username !== undefined)
          formData.append("username", userData.username);
        if (userData.first_name !== undefined)
          formData.append("first_name", userData.first_name);
        if (userData.last_name !== undefined)
          formData.append("last_name", userData.last_name);
        if (userData.is_active !== undefined)
          formData.append("is_active", userData.is_active.toString());
        if (userData.is_staff !== undefined)
          formData.append("is_staff", userData.is_staff.toString());
        if (userData.is_superuser !== undefined)
          formData.append("is_superuser", userData.is_superuser.toString());

        // Add password if provided
        if (userData.password) {
          formData.append("password", userData.password);
        }

        // Add role if provided
        if (userData.role) {
          formData.append("role", userData.role);
        }

        // Add profile data
        if (userData.phone !== undefined) {
          formData.append("phone", userData.phone);
        }
        if (userData.bio !== undefined) {
          formData.append("bio", userData.bio);
        }
        if (userData.avatar) {
          formData.append("avatar", userData.avatar);
        }

        const response = await fetch(`${API_URL}/auth/users/${id}/`, {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${authService.getAccessToken()}`,
          },
          credentials: "include",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(JSON.stringify(errorData));
        }

        const updatedUser = await response.json();
        await fetchUsers();
        return updatedUser;
      } catch (err: any) {
        console.error("Error updating user:", err);
        throw err;
      }
    },
    [users],
  );

  // Delete user
  const deleteUser = useCallback(
    async (id: number) => {
      try {
        const response = await fetch(`${API_URL}/auth/users/${id}/`, {
          method: "DELETE",
          headers: authService.getAuthHeaders(),
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`Failed to delete user: ${response.status}`);
        }

        setUsers(users.filter((user) => user.id !== id));
      } catch (err: any) {
        console.error("Error deleting user:", err);
        throw err;
      }
    },
    [users],
  );

  // Get user by id
  const getUserById = useCallback(
    (id: number) => {
      return users.find((user) => user.id === id);
    },
    [users],
  );

  return {
    users,
    isLoading,
    error,
    createUser,
    updateUser,
    deleteUser,
    getUserById,
    refetch: fetchUsers,
  };
};
