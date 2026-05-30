import createMDX from "@next/mdx";

/**
 * COOP/COEP headers enable cross-origin isolation, which Pyodide can use for
 * SharedArrayBuffer-backed interactive input(). With `output: "export"` these
 * headers are NOT emitted by Next in production (static export cannot set
 * headers) — production hosting sets them via vercel.json (Vercel) or the host's
 * own header config (see README, added in Phase 6). The headers() block below
 * applies during `next dev` so the interactive terminal can be developed locally.
 */
const crossOriginIsolationHeaders = [
  { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
  { key: "Cross-Origin-Embedder-Policy", value: "require-corp" },
];

// GitHub Pages serves this site under https://<user>.github.io/<repo>/, so all
// assets and routes need to be prefixed. Toggle off by setting GITHUB_PAGES=""
// in the environment (e.g. for Vercel or local dev), and on (default for the
// Pages workflow) by leaving it unset/truthy.
const basePath = process.env.GITHUB_PAGES === "false" ? "" : "/learn-to-code-platform";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  reactStrictMode: true,
  pageExtensions: ["ts", "tsx", "js", "jsx", "md", "mdx"],
  basePath,
  assetPrefix: basePath || undefined,
  // Surface the basePath to client code (e.g. the coi-serviceworker <script src>).
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
  images: {
    // next/image optimization is unavailable in static export
    unoptimized: true,
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: crossOriginIsolationHeaders,
      },
    ];
  },
};

const withMDX = createMDX({
  // remark/rehype plugins are added in Phase 3 when lesson MDX is wired up
  options: {},
});

export default withMDX(nextConfig);
