import { nextTick } from "vue";
import { createRouter, createWebHistory, type RouteLocationNormalized } from "vue-router";

import { homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/",
    component: () => import("@/views/LandingView.vue"),
    meta: { layout: "public" },
    beforeEnter: () => {
      const auth = useAuthStore();
      if (auth.logged_in) return homePathForRole(auth.role);
      return true;
    },
  },
  {
    path: "/terms",
    component: () => import("@/views/TermsView.vue"),
    meta: { layout: "public" },
  },
  {
    path: "/privacy",
    component: () => import("@/views/PrivacyView.vue"),
    meta: { layout: "public" },
  },
  {
    path: "/login",
    component: () => import("@/views/LoginView.vue"),
    meta: { requiresUnauth: true, layout: "auth" },
  },
  {
    path: "/register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { requiresUnauth: true, layout: "auth" },
  },
  // Customer
  {
    path: "/home",
    component: () => import("@/views/customer/CustomerLayout.vue"),
    meta: { requiresAuth: true, role: "user", layout: "dashboard" },
    children: [
      { path: "", redirect: "/home/browse" },
      { path: "browse", component: () => import("@/views/customer/sections/BrowsePage.vue") },
      {
        path: "requests",
        component: () => import("@/views/customer/sections/MyRequestsPage.vue"),
      },
    ],
  },
  // Professional
  {
    path: "/professional",
    component: () => import("@/views/professional/ProfessionalLayout.vue"),
    meta: { requiresAuth: true, role: "professional", layout: "dashboard" },
    children: [
      { path: "", redirect: "/professional/overview" },
      {
        path: "overview",
        component: () => import("@/views/professional/sections/OverviewPage.vue"),
      },
      {
        path: "requests",
        component: () => import("@/views/professional/sections/RequestsPage.vue"),
      },
      {
        path: "earnings",
        component: () => import("@/views/professional/sections/EarningsPage.vue"),
      },
    ],
  },
  { path: "/professional-dashboard", redirect: "/professional/overview" },
  // Admin
  {
    path: "/admin",
    component: () => import("@/views/admin/AdminTabsLayout.vue"),
    meta: { requiresAuth: true, role: "admin", layout: "dashboard" },
    children: [
      { path: "", redirect: "/admin/overview" },
      { path: "overview", component: () => import("@/views/admin/sections/OverviewPage.vue") },
      { path: "services", component: () => import("@/views/admin/sections/ServicesPage.vue") },
      {
        path: "professionals",
        component: () => import("@/views/admin/sections/ProfessionalsPage.vue"),
      },
      { path: "users", component: () => import("@/views/admin/sections/UsersPage.vue") },
      { path: "requests", component: () => import("@/views/admin/sections/RequestsPage.vue") },
      { path: "export", component: () => import("@/views/admin/sections/ExportPage.vue") },
      { path: "testing", component: () => import("@/views/admin/sections/TestingPage.vue") },
    ],
  },
  { path: "/admin-dashboard", redirect: "/admin/overview" },
  {
    path: "/account",
    component: () => import("@/views/AccountView.vue"),
    meta: { requiresAuth: true, layout: "dashboard" },
  },
  {
    path: "/users/:id",
    component: () => import("@/views/AccountView.vue"),
    meta: { requiresAuth: true, layout: "dashboard" },
    props: true,
  },
  {
    path: "/:pathMatch(.*)*",
    component: () => import("@/views/NotFoundView.vue"),
    meta: { layout: "public" },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// View Transitions API: snapshot the current DOM, run the navigation, then
// crossfade into the new DOM. Skipped on first load (no matched "from" route)
// and on browsers without support. The `await nextTick()` inside the callback
// gives Vue Router time to mount the new route before the API takes its snapshot.
router.beforeResolve((to, from) => {
  // Initial app load — no DOM to morph from.
  if (!from.matched.length) return;
  // Same-path navigation (e.g., query change) — nothing to morph.
  if (from.path === to.path) return;
  if (typeof document === "undefined") return;
  const startViewTransition = (
    document as Document & {
      startViewTransition?: (cb: () => Promise<void>) => unknown;
    }
  ).startViewTransition;
  if (!startViewTransition) return;
  return new Promise<void>((resolve) => {
    startViewTransition.call(document, async () => {
      resolve();
      await nextTick();
    });
  });
});

router.beforeEach((to: RouteLocationNormalized) => {
  const auth = useAuthStore();

  if (to.matched.some((r) => r.meta.requiresAuth)) {
    if (!auth.logged_in) return "/login";
    const requiredRole = to.meta.role as string | undefined;
    if (requiredRole && auth.role !== requiredRole) {
      return homePathForRole(auth.role);
    }
  }

  if (to.matched.some((r) => r.meta.requiresUnauth)) {
    if (auth.logged_in) return homePathForRole(auth.role);
  }

  return true;
});

export default router;
