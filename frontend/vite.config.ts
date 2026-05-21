import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// Allow overriding the base path at build time so GitHub Pages can serve us
// from /<repo-name>/ while local dev + Vercel serve from /.
//
//   VITE_BASE=/hearth/ pnpm build:demo
//
const base = process.env.VITE_BASE ?? "/";

export default defineConfig({
  base,
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "apple-touch-icon-180x180.png"],
      manifest: {
        name: "hearth",
        short_name: "hearth",
        description: "Household services platform",
        theme_color: "#161616",
        background_color: "#ffffff",
        display: "standalone",
        start_url: base,
        scope: base,
        icons: [
          { src: "pwa-64x64.png", sizes: "64x64", type: "image/png" },
          { src: "pwa-192x192.png", sizes: "192x192", type: "image/png" },
          { src: "pwa-512x512.png", sizes: "512x512", type: "image/png" },
          {
            src: "maskable-icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
  },
  build: {
    rollupOptions: {
      output: {
        // Group each role's tab sub-pages into one chunk. First tab visit
        // downloads ~30KB once; subsequent tab switches are in-memory.
        manualChunks(id) {
          if (id.includes("/src/views/admin/sections/")) return "admin-pages";
          if (id.includes("/src/views/professional/sections/")) return "pro-pages";
          if (id.includes("/src/views/customer/sections/")) return "customer-pages";
        },
      },
    },
  },
});
