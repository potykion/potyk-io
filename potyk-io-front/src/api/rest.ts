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
  updated?: RestRestaurant;
};

export type RestWritePayload = {
  name: string;
  cuisine: string;
  tier: string;
  maps_url: string;
  logo?: File | null;
};

function toFormData(payload: RestWritePayload): FormData {
  const body = new FormData();
  body.append("name", payload.name);
  body.append("cuisine", payload.cuisine);
  body.append("tier", payload.tier);
  body.append("maps_url", payload.maps_url);
  if (payload.logo) {
    body.append("logo", payload.logo);
  }
  return body;
}

export function fetchRest(): Promise<RestState> {
  return apiJson<RestState>("/v2/api/rest");
}

export function createRest(payload: RestWritePayload): Promise<RestState> {
  return apiJson<RestState>("/v2/api/rest", {
    method: "POST",
    body: toFormData(payload),
  });
}

export function updateRest(id: number, payload: RestWritePayload): Promise<RestState> {
  return apiJson<RestState>(`/v2/api/rest/${id}`, {
    method: "PUT",
    body: toFormData(payload),
  });
}

export function deleteRest(id: number): Promise<RestState> {
  return apiJson<RestState>(`/v2/api/rest/${id}`, {
    method: "DELETE",
  });
}
