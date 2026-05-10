import { useQuery } from "@tanstack/react-query";

export interface PredictionResponse {
  player: {
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
    status: string;
    market_value_eur: string | null;
    photo_url: string;
    height_cm: number | null;
    weight_kg: number | null;
    preferred_foot: string;
  };
  predicted_value_eur: number;
  confidence: number;
  shap_values?: {
    top_features?: string[];
    [key: string]: any;
  };
  model_version?: string;
}

export interface MLModel {
  id: number;
  name: string;
  model_type: string;
  version: string;
  algorithm: string;
  status: string;
  created_at: string;
}

export interface TopPerformer {
  player: {
    id: number;
    alias: string;
    position: string;
    club: string;
    photo_url: string;
  };
  predicted_value_eur: number;
  confidence: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export function usePrediction(playerId?: number) {
  return useQuery<PredictionResponse | null>({
    queryKey: ["prediction", playerId],
    queryFn: async () => {
      if (!playerId) return null;

      try {
        const url = `/api/predictions/player/?player_id=${playerId}`;
        const response = await fetch(url);
        if (!response.ok) {
          console.error("API Error:", response.status, response.statusText);
          throw new Error(`Failed to fetch prediction: ${response.statusText}`);
        }

        const data = await response.json();
        return data as PredictionResponse;
      } catch (err) {
        console.error("Error fetching prediction:", err);
        throw err;
      }
    },
    enabled: !!playerId,
    retry: 1,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useModels() {
  return useQuery<MLModel[]>({
    queryKey: ["ml-models"],
    queryFn: async () => {
      try {
        const url = "/api/predictions/models/";
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to fetch models: ${response.statusText}`);
        }

        const data = await response.json();
        return Array.isArray(data) ? data : [];
      } catch (err) {
        console.error("Error fetching models:", err);
        throw err;
      }
    },
    retry: 1,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}

export function useTopPerformers(limit = 10) {
  return useQuery<TopPerformer[]>({
    queryKey: ["top-performers", limit],
    queryFn: async () => {
      try {
        const url = `/api/predictions/top_performers/?limit=${limit}`;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to fetch top performers: ${response.statusText}`);
        }

        const data = await response.json();
        return Array.isArray(data) ? data : [];
      } catch (err) {
        console.error("Error fetching top performers:", err);
        throw err;
      }
    },
    retry: 1,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}
