import { createRouter, createWebHistory } from "vue-router";
import { fetchMe } from "@/api/auth";
import FinPage from "@/views/FinPage.vue";
import IndexPage from "@/views/IndexPage.vue";
import RestAdminPage from "@/views/RestAdminPage.vue";
import RestPage from "@/views/RestPage.vue";

const router = createRouter({
  history: createWebHistory("/v2/"),
  routes: [
    {
      path: "/",
      name: "index",
      component: IndexPage,
      meta: { requiresAuth: true },
    },
    {
      path: "/fin",
      name: "fin",
      component: FinPage,
      meta: { requiresAuth: true },
    },
    {
      path: "/rest",
      name: "rest",
      component: RestPage,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/rest",
      name: "rest-admin",
      component: RestAdminPage,
      meta: { requiresAuth: true },
    },
  ],
});

function loginRedirect(path: string): void {
  const next = path.startsWith("/v2") ? path : `/v2${path}`;
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
