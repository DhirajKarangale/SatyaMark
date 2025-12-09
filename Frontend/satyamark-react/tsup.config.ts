import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  external: ["react"],
  target: "es2019",
  loader: {
    ".png": "copy"
  },
  publicDir: "icons-mark"
});
