import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        // Backend currently running on 8001 (see user note)
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
