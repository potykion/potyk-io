import { createRouter, createWebHistory } from "vue-router";
import { fetchMe } from "@/api/auth";
import FinPage from "@/views/FinPage.vue";

const router = createRouter({
  history: createWebHistory("/v2/"),
  routes: [
    {
      path: "/",
      redirect: { name: "fin" },
    },
    {
      path: "/fin",
      name: "fin",
      component: FinPage,
      meta: { requiresAuth: true },
    },
  ],
});

function loginRedirect(path: string): void {
  const next = path.startsWith("/v2") ? path : `/v2${path === "/" ? "/fin" : path}`;
  window.location.href = `/auth/login?next=${encodeURIComponent(next)}`;
}

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    return true;
  }
  const me = await fetchMe();
  if (!me) {
    loginRedirect(to.fullPath);
    return false;
  }
  return true;
});

export default router;
