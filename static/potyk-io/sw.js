/* potyk.io offline service worker — version injected as __CACHE_VERSION__ */
const CACHE_VERSION = "__CACHE_VERSION__";
const CACHE_NAME = "potyk-io-" + CACHE_VERSION;

async function precacheFromManifest() {
  const res = await fetch("/offline.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error("offline.json " + res.status);
  }
  const data = await res.json();
  const urls = Array.isArray(data.urls) ? data.urls : [];
  const cache = await caches.open(CACHE_NAME);
  await Promise.all(
    urls.map(async (url) => {
      try {
        const response = await fetch(url, { cache: "reload" });
        if (response.ok) {
          await cache.put(url, response);
        }
      } catch (e) {
        /* skip failed URL — don't fail whole install */
      }
    })
  );
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    precacheFromManifest()
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
              (key.startsWith("potyk-io-") || key.startsWith("potyk-food-")) &&
              key !== CACHE_NAME
          )
          .map((key) => caches.delete(key))
      );
      await self.clients.claim();
    })()
  );
});

function isHomePath(pathname) {
  return pathname === "/";
}

function isFoodPath(pathname) {
  return pathname === "/food" || pathname.startsWith("/food/");
}

function isAppPath(pathname) {
  return isHomePath(pathname) || isFoodPath(pathname);
}

function isStaticPath(pathname) {
  return pathname.startsWith("/static/");
}

async function revalidate(cache, request) {
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) {
      await cache.put(request, fresh.clone());
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
      const cache = await caches.open(CACHE_NAME);

      if (stat) {
        const cachedStatic = await cache.match(request);
        if (cachedStatic) {
          return cachedStatic;
        }
        return fetch(request);
      }

      const cached = await cache.match(request, { ignoreSearch: true });
      if (cached) {
        event.waitUntil(revalidate(cache, request));
        return cached;
      }

      try {
        const fresh = await fetch(request);
        if (fresh && fresh.ok) {
          await cache.put(request, fresh.clone());
        }
        return fresh;
      } catch (e) {
        if (request.mode === "navigate") {
          const fallback =
            (await cache.match("/")) ||
            (await cache.match("/food/offline")) ||
            (await cache.match("/food"));
          if (fallback) {
            return fallback;
          }
        }
        throw e;
      }
    })()
  );
});
