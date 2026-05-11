import { useCallback, useState, useEffect } from "react";

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  role: "admin" | "director" | "scout";
  date_joined: string;
}

const STORAGE_KEY = "admin_users_mock";

// Initial mock users for admin management
const INITIAL_USERS: AdminUser[] = [
  {
    id: 1,
    email: "admin@example.com",
    username: "admin",
    first_name: "Admin",
    last_name: "User",
    is_active: true,
    is_staff: true,
    is_superuser: true,
    role: "admin",
    date_joined: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    email: "scout@example.com",
    username: "scout",
    first_name: "Scout",
    last_name: "Pro",
    is_active: true,
    is_staff: false,
    is_superuser: false,
    role: "scout",
    date_joined: "2026-01-02T00:00:00Z",
  },
  {
    id: 3,
    email: "director@example.com",
    username: "director",
    first_name: "Director",
    last_name: "General",
    is_active: true,
    is_staff: false,
    is_superuser: false,
    role: "director",
    date_joined: "2026-01-03T00:00:00Z",
  },
  {
    id: 4,
    email: "juan.perez@example.com",
    username: "juanperez",
    first_name: "Juan",
    last_name: "Pérez",
    is_active: true,
    is_staff: false,
    is_superuser: false,
    role: "scout",
    date_joined: "2026-01-04T00:00:00Z",
  },
];

export const useAdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load users from localStorage or initialize with default
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setUsers(JSON.parse(stored));
      } catch {
        setUsers(INITIAL_USERS);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_USERS));
      }
    } else {
      setUsers(INITIAL_USERS);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_USERS));
    }
    setIsLoading(false);
  }, []);

  // Save users to localStorage
  const saveUsers = useCallback((updatedUsers: AdminUser[]) => {
    setUsers(updatedUsers);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedUsers));
  }, []);

  // Create user
  const createUser = useCallback(
    (userData: Omit<AdminUser, "id" | "date_joined">) => {
      const newUser: AdminUser = {
        ...userData,
        id: Math.max(...users.map((u) => u.id), 0) + 1,
        date_joined: new Date().toISOString(),
      };
      saveUsers([...users, newUser]);
      return newUser;
    },
    [users, saveUsers],
  );

  // Update user
  const updateUser = useCallback(
    (id: number, userData: Partial<AdminUser>) => {
      const updatedUsers = users.map((user) =>
        user.id === id ? { ...user, ...userData } : user,
      );
      saveUsers(updatedUsers);
    },
    [users, saveUsers],
  );

  // Delete user
  const deleteUser = useCallback(
    (id: number) => {
      const updatedUsers = users.filter((user) => user.id !== id);
      saveUsers(updatedUsers);
    },
    [users, saveUsers],
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
    createUser,
    updateUser,
    deleteUser,
    getUserById,
  };
};
