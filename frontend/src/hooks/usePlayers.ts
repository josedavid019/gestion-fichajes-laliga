import { useQuery } from "@tanstack/react-query";

interface Player {
  id: number;
  first_name: string;
  last_name: string;
  alias: string;
  age: number | null;
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

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function usePlayers(params?: Record<string, string | number>) {
  return useQuery<Player[]>({
    queryKey: ["players", params],
    queryFn: async () => {
      console.log("Fetching all players with pagination...");
      let allPlayers: Player[] = [];
      let offset = 0;
      const limit = 50;
      let hasMore = true;

      while (hasMore) {
        const queryParams = new URLSearchParams();
        queryParams.append("limit", limit.toString());
        queryParams.append("offset", offset.toString());

        if (params) {
          Object.entries(params).forEach(([key, value]) => {
            queryParams.append(key, String(value));
          });
        }

        const url = `${API_BASE_URL}/api/players/?${queryParams.toString()}`;
        console.log(`[Page ${offset / limit + 1}] Fetching from: ${url}`);

        try {
          const response = await fetch(url);
          if (!response.ok) {
            console.error("API Error:", response.status, response.statusText);
            throw new Error(`Failed to fetch players: ${response.statusText}`);
          }

          const data = await response.json();

          let batch: Player[] = [];

          // Handle paginated response
          if (data.results) {
            batch = data.results;
            console.log(`[Page ${offset / limit + 1}] Received ${batch.length} players (Total: ${data.count})`);
          }
          // Handle direct array response
          else if (Array.isArray(data)) {
            batch = data;
            console.log(`[Page ${offset / limit + 1}] Received ${batch.length} players`);
          }

          if (batch.length === 0) {
            hasMore = false;
          } else {
            allPlayers = [...allPlayers, ...batch];
            offset += limit;

            // Safety check
            if (allPlayers.length >= 500) {
              hasMore = false;
            }
          }
        } catch (err) {
          console.error("Error fetching page:", err);
          hasMore = false;
        }
      }

      console.log(`✓ Total players fetched: ${allPlayers.length}`);
      return allPlayers;
    },
    retry: 1,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
