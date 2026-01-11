import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni()],
  resolve: {
    alias: {
      "wot-design-uni/style/index.scss": path.resolve(__dirname, "src/styles/wot-design-uni.scss"),
    },
  },
});
