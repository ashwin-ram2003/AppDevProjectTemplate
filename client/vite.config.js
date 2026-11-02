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
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5050',
      // Sign-up/sign-in (US-01/US-02) live at the bare paths the scaffold
      // already used (server/app.py's /add_user and /login), not under
      // /api -- proxy them explicitly too, or the dev server swallows
      // these calls instead of forwarding them to Flask.
      '/add_user': 'http://localhost:5050',
      '/login': 'http://localhost:5050',
      '/join_project': 'http://localhost:5050',
      '/create_project': 'http://localhost:5050',
      '/get_user_projects_list': 'http://localhost:5050',
      '/get_project_info': 'http://localhost:5050',
      '/me': 'http://localhost:5050',
      '/logout': 'http://localhost:5050',
    },
  },
});
