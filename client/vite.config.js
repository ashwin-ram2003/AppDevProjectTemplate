import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Project convention keeps React source files at .js (see this plan's
  // files_modified list), so tell esbuild to treat them as JSX both for the
  // dev server's dependency pre-bundling and for the production build.
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.js$/,
    // Vite's esbuild plugin defaults `exclude` to /\.js$/ when unset, which
    // silently overrides `include` above and skips JSX stripping for every
    // .js file. Must be explicitly cleared.
    exclude: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5050',
    },
  },
});
