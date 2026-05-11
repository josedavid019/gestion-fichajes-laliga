// Mock users for development - frontend only testing
export const MOCK_USERS = [
  {
    id: 1,
    email: "admin@example.com",
    password: "admin123",
    first_name: "Admin",
    last_name: "User",
    is_active: true,
    date_joined: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    email: "scout@example.com",
    password: "scout123",
    first_name: "Scout",
    last_name: "Pro",
    is_active: true,
    date_joined: "2026-01-02T00:00:00Z",
  },
  {
    id: 3,
    email: "director@example.com",
    password: "director123",
    first_name: "Director",
    last_name: "General",
    is_active: true,
    date_joined: "2026-01-03T00:00:00Z",
  },
  {
    id: 4,
    email: "juan.perez@example.com",
    password: "password123",
    first_name: "Juan",
    last_name: "Pérez",
    is_active: true,
    date_joined: "2026-01-04T00:00:00Z",
  },
];

export const findMockUser = (email: string, password: string) => {
  return MOCK_USERS.find(
    (user) => user.email === email && user.password === password,
  );
};
