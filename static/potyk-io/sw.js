/* potyk.io offline service worker — version injected as __CACHE_VERSION__ */
const CACHE_VERSION = "__CACHE_VERSION__";
const SHELL_CACHE = "potyk-io-shell-" + CACHE_VERSION;
const RUNTIME_CACHE = "potyk-io-runtime";

const APP_PREFIXES = [
  "/food",
  "/travel",
  "/tech",
  "/culture",
  "/mu",
  "/findings",
  "/prikols",
  "/docs",
  "/money",
  "/invest",
];

async function putInCache(cache, url, response) {
  const body = await response.blob();
  const cached = new Response(body, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
  await cache.put(url, cached);
}

async function precacheShell() {
  const res = await fetch("/offline.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error("offline.json " + res.status);
  }
  const data = await res.json();
  const urls = Array.isArray(data.shell)
    ? data.shell
    : Array.isArray(data.urls)
      ? data.urls
      : [];
  const cache = await caches.open(SHELL_CACHE);
  await Promise.all(
    urls.map(async (url) => {
      try {
        const response = await fetch(url, { cache: "reload", redirect: "follow" });
        if (response.ok) {
          await putInCache(cache, url, response);
        }
      } catch (e) {
        /* skip failed URL */
      }
    })
  );
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    precacheShell()
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(
            (key) =>
              key.startsWith("potyk-io-shell-") &&
              key !== SHELL_CACHE
          )
          .map((key) => caches.delete(key))
      );
      // legacy full-precache caches
      await Promise.all(
        keys
          .filter(
            (key) =>
              key.startsWith("potyk-io-") &&
              !key.startsWith("potyk-io-shell-") &&
              key !== RUNTIME_CACHE
          )
          .map((key) => caches.delete(key))
      );
      await Promise.all(
        keys
          .filter((key) => key.startsWith("potyk-food-"))
          .map((key) => caches.delete(key))
      );
      await self.clients.claim();
    })()
  );
});

function isBlockedPath(pathname) {
  return (
    pathname === "/fin" ||
    pathname.startsWith("/fin/") ||
    pathname === "/invest/deals" ||
    pathname.startsWith("/invest/deals/")
  );
}

function isAppPath(pathname) {
  if (isBlockedPath(pathname)) {
    return false;
  }
  if (pathname === "/") {
    return true;
  }
  return APP_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(prefix + "/")
  );
}

function isStaticPath(pathname) {
  return pathname.startsWith("/static/");
}

async function matchCaches(request, ignoreSearch) {
  const opts = ignoreSearch ? { ignoreSearch: true } : undefined;
  const shell = await caches.open(SHELL_CACHE);
  const fromShell = await shell.match(request, opts);
  if (fromShell) {
    return fromShell;
  }
  const runtime = await caches.open(RUNTIME_CACHE);
  return runtime.match(request, opts);
}

async function putRuntime(request, response) {
  const runtime = await caches.open(RUNTIME_CACHE);
  await runtime.put(request, response);
}

async function revalidate(request) {
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) {
      await putRuntime(request, fresh.clone());
    }
  } catch (e) {
    /* ignore */
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") {
    return;
  }

  let url;
  try {
    url = new URL(request.url);
  } catch (e) {
    return;
  }

  if (url.origin !== self.location.origin) {
    return;
  }

  const path = url.pathname;
  const app = isAppPath(path);
  const stat = isStaticPath(path);
  if (!app && !stat) {
    return;
  }

  event.respondWith(
    (async () => {
      if (stat) {
        const cachedStatic = await matchCaches(request, false);
        if (cachedStatic) {
          return cachedStatic;
        }
        const fresh = await fetch(request);
        if (fresh && fresh.ok) {
          await putRuntime(request, fresh.clone());
        }
        return fresh;
      }

      const cached = await matchCaches(request, true);
      if (cached) {
        event.waitUntil(revalidate(request));
        return cached;
      }

      try {
        const fresh = await fetch(request);
        if (fresh && fresh.ok) {
          await putRuntime(request, fresh.clone());
        }
        return fresh;
      } catch (e) {
        if (request.mode === "navigate") {
          const fallback =
            (await matchCaches(new Request("/"), true)) ||
            (await matchCaches(new Request("/food/offline"), true)) ||
            (await matchCaches(new Request("/food"), true));
          if (fallback) {
            return fallback;
          }
        }
        throw e;
      }
    })()
  );
});
