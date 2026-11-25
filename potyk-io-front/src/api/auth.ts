export type MeResponse = {
  authenticated: boolean;
};

export async function fetchMe(): Promise<MeResponse | null> {
  try {
    const res = await fetch("/v2/api/me", {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    if (res.status === 401) {
      return null;
    }
    if (!res.ok) {
      return null;
    }
    return (await res.json()) as MeResponse;
  } catch {
    return null;
  }
}
