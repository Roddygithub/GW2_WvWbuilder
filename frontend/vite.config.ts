import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@lib": path.resolve(__dirname, "./src/lib"),
    },
  },
  server: {
    proxy: {
      // Proxy /api requests to the backend server
      "/api": {
        target: "http://127.0.0.1:8000", // Your backend address
        changeOrigin: true,
        // No need to rewrite the path, as the backend endpoints don't have /api
      },
    },
  },
  // Désactiver les erreurs de type "failed to load module" pour les imports non résolus
  // Cela nous permettra de démarrer l'application même si certaines dépendances sont manquantes
  optimizeDeps: {
    exclude: []
  }
});
