import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { crx } from '@crxjs/vite-plugin';
import manifest from './manifest.json' with { type: 'json' };

export default defineConfig({
  plugins: [
    react(),
    crx({ manifest }),
  ],
  server: {
    port: 5173,
    strictPort: true,
    host: '127.0.0.1',
    hmr: {
      port: 5173,
      host: '127.0.0.1',
    },
  },
  build: {
    emptyOutDir: true,
    rollupOptions: {
      input: {
        dashboard: 'dashboard.html',
      },
    },
  },
});
