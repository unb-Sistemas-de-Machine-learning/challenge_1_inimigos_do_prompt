import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { crx } from '@crxjs/vite-plugin';
import manifestJson from './manifest.json' with { type: 'json' };

const browserTarget = process.env.BROWSER || 'chrome';

// Clone o manifest para podermos alterar em tempo de execução
const manifest = JSON.parse(JSON.stringify(manifestJson));

if (browserTarget === 'firefox') {
  // Firefox usa sidebar_action em vez de side_panel
  if (manifest.side_panel) {
    manifest.sidebar_action = {
      default_panel: manifest.side_panel.default_path,
    };
    delete manifest.side_panel;
  }
  
  // Remove permissão sidePanel que não é suportada no Firefox
  if (manifest.permissions) {
    manifest.permissions = manifest.permissions.filter((p: string) => p !== 'sidePanel');
  }

  // Configurações específicas exigidas pelo Firefox (ID de extensão)
  manifest.browser_specific_settings = {
    gecko: {
      id: "inimigos-do-prompt@unb.br",
      strict_min_version: "109.0"
    }
  };

  // Firefox prefere scripts em vez de service_worker no Manifest V3
  if (manifest.background && manifest.background.service_worker) {
    manifest.background = {
      scripts: [manifest.background.service_worker]
    };
  }
}

export default defineConfig({
  plugins: [
    react(),
    crx({ 
      manifest, 
      browser: browserTarget === 'firefox' ? 'firefox' : 'chrome' 
    }),
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
    outDir: `dist-${browserTarget}`,
    emptyOutDir: true,
    rollupOptions: {
      input: {
        dashboard: 'dashboard.html',
      },
    },
  },
});
