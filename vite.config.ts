import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// 说明：base 用相对路径 './'，这样构建产物既可以放在域名根目录
// （Cloudflare Pages / Vercel），也可以放在 GitHub Pages 的子路径下，
// 不用改配置就能直接部署。
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 900,
  },
});