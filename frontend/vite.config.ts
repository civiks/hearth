import { execSync } from "node:child_process";
import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

// Allow overriding the base path at build time so GitHub Pages can serve
// from repo while local dev + Vercel serve from /.
//
//   VITE_BASE=/hearth/ pnpm build:demo
//
const base = process.env.VITE_BASE ?? "/";

// Per-build identifier (short git SHA). Used as the demo-state cache key so
// every deploy auto-invalidates.
const buildId = (() => {
  try {
    return execSync("git rev-parse --short HEAD").toString().trim();
  } catch {
    return "dev";
  }
})();

export default defineConfig({
  base,
  define: {
    "import.meta.env.VITE_BUILD_ID": JSON.stringify(buildId),
  },
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
  },
  build: {
    modulePreload: {
      resolveDependencies: (_filename, deps) =>
        deps.filter(
          (dep) =>
            !dep.includes("admin-pages") &&
            !dep.includes("pro-pages") &&
            !dep.includes("customer-pages"),
        ),
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("/src/components/ui/")) return "ui";
          if (id.includes("/src/lib/demo/")) return "demo";
          if (
            id.includes("/src/views/LoginView") ||
            id.includes("/src/views/RegisterView") ||
            id.includes("/src/views/LandingView") ||
            id.includes("/src/views/AccountView") ||
            id.includes("/src/views/SettingsView")
          )
            return "public-views";
          if (id.includes("/src/views/admin/sections/")) return "admin-pages";
          if (id.includes("/src/views/professional/sections/")) return "pro-pages";
          if (id.includes("/src/views/customer/sections/")) return "customer-pages";
        },
      },
    },
  },
});
