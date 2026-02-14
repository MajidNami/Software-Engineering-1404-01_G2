import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  base: '/team11/', // Assets will now be linked as /team11/assets/...
  plugins: [react(), tailwindcss(),],
  server: {
    port: 3005,
    host: true,
    // This allows you to visit localhost:3005 and redirected to /team11/
    open: '/team11/',

    // Enable CORS for dev server
    cors: {
      origin: '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization'],
      credentials: true,
    },
    proxy: {
      // Direct API calls to your Docker Gateway
      '/api': {
        target: 'http://localhost:9151',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
      },
      '/auth': {
        target: 'http://localhost:9151',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})