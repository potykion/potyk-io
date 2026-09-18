/**
 * Telegram Bot API reverse proxy (Cloudflare Worker).
 * Bot calls: https://<worker>/bot<TOKEN>/<method>
 * Worker forwards to: https://api.telegram.org/bot<TOKEN>/<method>
 */

export default {
  async fetch(request, env) {
    return handleRequest(request, env);
  },
};

async function handleRequest(request, env) {
  const url = new URL(request.url);

  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders() });
  }

  if (url.pathname === "/" || url.pathname === "/health") {
    return Response.json(
      {
        status: "ok",
        service: "telegram-api-proxy",
        usage: "Set TELEGRAM_API_BASE_URL to https://<this-host>/bot",
      },
      { headers: corsHeaders() },
    );
  }

  const isBot = url.pathname.startsWith("/bot");
  const isFile = url.pathname.startsWith("/file/bot");
  if (!isBot && !isFile) {
    return Response.json(
      { error: "Expected /bot<TOKEN>/<method> or /file/bot<TOKEN>/..." },
      { status: 400, headers: corsHeaders() },
    );
  }

  if (env.ALLOWED_TOKENS) {
    const match = url.pathname.match(/^\/(?:file\/)?bot([^/]+)/);
    const token = match?.[1];
    const allowed = env.ALLOWED_TOKENS.split(",").map((t) => t.trim());
    if (!token || !allowed.includes(token)) {
      return Response.json(
        { error: "Token not allowed" },
        { status: 403, headers: corsHeaders() },
      );
    }
  }

  const telegramUrl = `https://api.telegram.org${url.pathname}${url.search}`;

  try {
    const upstream = await fetch(telegramUrl, {
      method: request.method,
      headers: filterHeaders(request.headers),
      body:
        request.method !== "GET" && request.method !== "HEAD"
          ? request.body
          : undefined,
      redirect: "follow",
    });

    const headers = new Headers(upstream.headers);
    for (const [k, v] of Object.entries(corsHeaders())) {
      headers.set(k, v);
    }

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers,
    });
  } catch (error) {
    return Response.json(
      {
        error: "Failed to proxy request to Telegram",
        message: String(error?.message || error),
      },
      { status: 502, headers: corsHeaders() },
    );
  }
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

function filterHeaders(headers) {
  const filtered = new Headers();
  for (const name of ["content-type", "accept", "accept-language", "content-length"]) {
    const value = headers.get(name);
    if (value) filtered.set(name, value);
  }
  return filtered;
}
