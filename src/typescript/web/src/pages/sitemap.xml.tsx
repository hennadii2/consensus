import { withServerSideAuth } from "@clerk/nextjs/ssr";
import { getIp, getSitemap } from "helpers/api";
import type { GetServerSidePropsContext } from "next";

/**
 * @page Sitemap Page
 * @description Page to display all sitemaps (root and sub pages), where the
 * sitemap XML is loaded dynamically from the backend.
 */
const Sitemap = () => {
  // Empty. getServerSideProps writes XML directly to the browser.
};

export const getServerSideProps = withServerSideAuth(
  async (context: GetServerSidePropsContext) => {
    try {
      const authToken = await (context.req as any).auth.getToken();
      const ipAddress = await getIp(context.req);
      // Get the sitemap from the backend and send XML to the browser.
      const sitemap = await getSitemap(context.res?.req?.url as string, {
        authToken,
        ipAddress,
        headers: context.req.headers,
      });
      context.res.setHeader("Content-Type", "application/xml");
      context.res.write(`<?xml version="1.0" encoding="UTF-8"?>${sitemap}`);
      context.res.end();
      return { props: {} };
    } catch (e) {
      // Error to 404 page if sitemap was not found
      return { notFound: true };
    }
  }
);

export default Sitemap;
