import { nextTick } from "vue";
import { createRouter, createWebHistory, type RouteLocationNormalized } from "vue-router";
import {
  PhBriefcase,
  PhClipboardText,
  PhGridFour,
  PhHammer,
  PhShoppingBag,
  PhSquaresFour,
  PhTrendUp,
  PhUsers,
  PhWrench,
} from "@phosphor-icons/vue";

import { LOGGED_OUT_PATH, homePathForRole } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/",
    component: () => import("@/views/LandingView.vue"),
    meta: { layout: "public", title: "" },
    beforeEnter: () => {
      const auth = useAuthStore();
      if (auth.logged_in) return homePathForRole(auth.role);
      return true;
    },
  },
  {
    path: "/terms",
    component: () => import("@/views/TermsView.vue"),
    meta: { layout: "public", title: "Terms of Service" },
  },
  {
    path: "/privacy",
    component: () => import("@/views/PrivacyView.vue"),
    meta: { layout: "public", title: "Privacy Policy" },
  },
  {
    path: "/login",
    component: () => import("@/views/LoginView.vue"),
    meta: { requiresUnauth: true, layout: "auth", title: "Sign in" },
  },
  {
    path: "/register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { requiresUnauth: true, layout: "auth", title: "Create account" },
  },
  // Customer
  {
    path: "/home",
    component: () => import("@/views/DashboardTabsLayout.vue"),
    meta: {
      requiresAuth: true, role: "user", layout: "dashboard",
      tabs: [
        { label: "Browse",      to: "/home/browse",    icon: PhShoppingBag },
        { label: "Services",    to: "/home/services",  icon: PhGridFour },
        { label: "My requests", to: "/home/requests",  icon: PhClipboardText },
      ],
    },
    children: [
      { path: "", redirect: "/home/browse" },
      {
        path: "browse",
        component: () => import("@/views/customer/sections/BrowsePage.vue"),
        meta: { title: "Browse services" },
      },
      {
        path: "services",
        component: () => import("@/views/customer/sections/AllServicesPage.vue"),
        meta: { title: "Services" },
      },
      {
        path: "requests",
        component: () => import("@/views/customer/sections/MyRequestsPage.vue"),
        meta: { title: "My requests" },
      },
    ],
  },
  // Professional
  {
    path: "/professional",
    component: () => import("@/views/DashboardTabsLayout.vue"),
    meta: {
      requiresAuth: true, role: "professional", layout: "dashboard",
      tabs: [
        { label: "Overview",  to: "/professional/overview",  icon: PhSquaresFour },
        { label: "Requests",  to: "/professional/requests",  icon: PhClipboardText },
        { label: "Earnings",  to: "/professional/earnings",  icon: PhTrendUp },
      ],
    },
    children: [
      { path: "", redirect: "/professional/overview" },
      {
        path: "overview",
        component: () => import("@/views/professional/sections/OverviewPage.vue"),
        meta: { title: "Overview" },
      },
      {
        path: "requests",
        component: () => import("@/views/professional/sections/RequestsPage.vue"),
        meta: { title: "Requests" },
      },
      {
        path: "earnings",
        component: () => import("@/views/professional/sections/EarningsPage.vue"),
        meta: { title: "Earnings" },
      },
    ],
  },
  { path: "/professional-dashboard", redirect: "/professional/overview" },
  // Admin
  {
    path: "/admin",
    component: () => import("@/views/DashboardTabsLayout.vue"),
    meta: {
      requiresAuth: true, role: "admin", layout: "dashboard",
      tabs: [
        { label: "Overview",       to: "/admin/overview",      icon: PhSquaresFour },
        { label: "Services",       to: "/admin/services",      icon: PhWrench },
        { label: "Professionals",  to: "/admin/professionals", icon: PhBriefcase },
        { label: "Users",          to: "/admin/users",         icon: PhUsers },
        { label: "Requests",       to: "/admin/requests",      icon: PhClipboardText },
        { label: "Tools",          to: "/admin/tools",         icon: PhHammer },
      ],
    },
    children: [
      { path: "", redirect: "/admin/overview" },
      {
        path: "overview",
        component: () => import("@/views/admin/sections/OverviewPage.vue"),
        meta: { title: "Overview" },
      },
      {
        path: "services",
        component: () => import("@/views/admin/sections/ServicesPage.vue"),
        meta: { title: "Services" },
      },
      {
        path: "professionals",
        component: () => import("@/views/admin/sections/ProfessionalsPage.vue"),
        meta: { title: "Professionals" },
      },
      {
        path: "users",
        component: () => import("@/views/admin/sections/UsersPage.vue"),
        meta: { title: "Users" },
      },
      {
        path: "requests",
        component: () => import("@/views/admin/sections/RequestsPage.vue"),
        meta: { title: "Requests" },
      },
      {
        path: "tools",
        component: () => import("@/views/admin/sections/ToolsPage.vue"),
        meta: { title: "Admin tools" },
      },
      // Legacy redirects for the now-merged Export + Testing pages.
      { path: "export", redirect: "/admin/tools" },
      { path: "testing", redirect: "/admin/tools" },
    ],
  },
  { path: "/admin-dashboard", redirect: "/admin/overview" },
  {
    path: "/account",
    component: () => import("@/views/AccountView.vue"),
    meta: { requiresAuth: true, layout: "dashboard", title: "Account" },
  },
  {
    path: "/users/:id",
    component: () => import("@/views/AccountView.vue"),
    // Title is set dynamically in AccountView once the user loads.
    meta: { requiresAuth: true, layout: "dashboard", title: "User profile" },
    props: true,
  },
  {
    path: "/:pathMatch(.*)*",
    component: () => import("@/views/NotFoundView.vue"),
    meta: { layout: "public", title: "Page not found" },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash };
    return { top: 0, behavior: "instant" };
  },
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
    if (!auth.logged_in) return LOGGED_OUT_PATH;
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

const BRAND = "hearth";
router.afterEach((to) => {
  const titled = [...to.matched].reverse().find((r) => r.meta.title);
  const t = titled?.meta.title as string | undefined;
  document.title = t ? `${t} — ${BRAND}` : BRAND;
});

export default router;
