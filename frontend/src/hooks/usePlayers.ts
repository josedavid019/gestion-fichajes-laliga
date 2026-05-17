import { useQuery } from "@tanstack/react-query";
import { fetchWithAuth } from "@/lib/fetchWithAuth";

interface Player {
  id: number;
  first_name: string;
  last_name: string;
  alias: string;
  age: number | null;
  position: string;
  nationality: {
    id: number;
    name: string;
    code: string;
    flag_url: string;
  } | null;
  current_club: {
    id: number;
    name: string;
    city: string;
    logo_url: string;
  } | null;
  shirt_number: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  preferred_foot: string;
  status: string;
  market_value_eur: string | null;
  photo_url: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export function usePlayers(params?: Record<string, string | number>) {
  return useQuery<Player[]>({
    queryKey: ["players", params],
    queryFn: async () => {
      // Optimized fetch:
      // - If a `search` param is provided, request a single page from the API
      //   and return results (server-side search).
      // - Otherwise, fetch a single page with a larger `limit` to avoid
      //   iterating over many pages on initial load.
      const queryParams = new URLSearchParams();

      const isSearch = Boolean(params && (params as any).search);
      const limit = isSearch ? 50 : 200;
      queryParams.append("limit", String(limit));
      queryParams.append("offset", "0");

      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          queryParams.append(key, String(value));
        });
      }

      const url = `/api/players/?${queryParams.toString()}`;
      console.log(`Fetching players from: ${url}`);

      const response = await fetchWithAuth(url);
      if (!response.ok) {
        console.error("API Error:", response.status, response.statusText);
        throw new Error(`Failed to fetch players: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.results && Array.isArray(data.results)) {
        return data.results as Player[];
      }

      if (Array.isArray(data)) return data as Player[];

      return [];
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000,
  });
}
