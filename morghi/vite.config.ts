import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tsNameof from 'vite-plugin-ts-nameof';

export default defineConfig({ plugins: [tsNameof(), vue()] });