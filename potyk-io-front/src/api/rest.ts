import { apiJson } from "@/api/client";

export type RestRestaurant = {
  id: number;
  name: string;
  cuisine: string;
  tier: string;
  logo: string;
  maps_url: string;
};

export type RestState = {
  restaurants: RestRestaurant[];
  cuisines: string[];
  created?: RestRestaurant;
};

export type RestCreatePayload = {
  name: string;
  cuisine: string;
  tier: string;
  maps_url: string;
  logo?: File | null;
};

export function fetchRest(): Promise<RestState> {
  return apiJson<RestState>("/v2/api/rest");
}

export function createRest(payload: RestCreatePayload): Promise<RestState> {
  const body = new FormData();
  body.append("name", payload.name);
  body.append("cuisine", payload.cuisine);
  body.append("tier", payload.tier);
  body.append("maps_url", payload.maps_url);
  if (payload.logo) {
    body.append("logo", payload.logo);
  }
  return apiJson<RestState>("/v2/api/rest", {
    method: "POST",
    body,
  });
}
