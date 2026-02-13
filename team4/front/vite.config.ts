import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  base: '/static/team4/',  // IMPORTANT
  build: {
    outDir: path.resolve(__dirname, '../static/team4'),
    emptyOutDir: true,
  }
});
