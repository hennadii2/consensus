const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const WORDPRESS_BLOG_URL = process.env.WORDPRESS_BLOG_URL;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  experimental: {
    scrollRestoration: true,
  },
  distDir: "build",
  trailingSlash: true,
  transpilePackages: ["export-to-csv"],
  async redirects() {
    return [
      {
        source: "/home",
        destination: "/",
        permanent: true,
      },
      {
        source: "/links/",
        destination: "/home/links/",
        permanent: true,
      },
      {
        source: "/about-us/",
        destination: "/home/about-us/",
        permanent: true,
      },
      {
        source: "/contact-us/",
        destination: "/home/contact-us/",
        permanent: true,
      },
      {
        source: "/privacy-policy/",
        destination: "/home/privacy-policy/",
        permanent: true,
      },
      {
        source: "/blog/:slug*",
        destination: "/home/blog/:slug*",
        permanent: true,
      },
      {
        source: "/wp-content/:slug*",
        destination: "/home/wp-content/:slug*",
        permanent: true,
      },
      {
        source: "/wp-includes/:slug*",
        destination: "/home/wp-includes/:slug*",
        permanent: true,
      },
      {
        source: "/wp-json/:slug*",
        destination: "/home/wp-json/:slug*",
        permanent: true,
      },
    ];
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/",
          destination: `${WORDPRESS_BLOG_URL}`,
        },
        {
          source: "/#",
          destination: `${WORDPRESS_BLOG_URL}/#`,
        },
        // Match on paths that include a "." extension in the path to avoid
        // adding a breaking slash at the end.
        // Example: /home/sitemap_index.xml, /home/wp-admin.php?...
        {
          source: "/home/:slug(.*\\.\\w{1,})*",
          destination: `${WORDPRESS_BLOG_URL}/:slug*`,
        },
        {
          source: "/home/:slug*/",
          destination: `${WORDPRESS_BLOG_URL}/:slug*/`,
        },
        {
          source: "/search/",
          destination: "/",
        },
      ],
      afterFiles: [
        {
          source: "/sitemaps/:path*",
          destination: "/sitemap.xml",
        },
      ],
    };
  },
};

module.exports = withBundleAnalyzer(nextConfig);
