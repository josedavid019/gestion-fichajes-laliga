import { authService } from "./authService";

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Custom fetch wrapper that automatically includes JWT authentication headers
 */
export async function fetchWithAuth(
  url: string,
  options: FetchOptions = {},
): Promise<Response> {
  const authHeaders = authService.getAuthHeaders();

  const mergedOptions: FetchOptions = {
    ...options,
    headers: {
      ...authHeaders,
      ...(options.headers || {}),
    },
    credentials: options.credentials || "include",
  };

  return fetch(url, mergedOptions);
}

/**
 * Get headers with authentication
 */
export function getAuthHeaders(): Record<string, string> {
  return authService.getAuthHeaders();
}
