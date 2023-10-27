import { IS_PRODUCTION_ENV } from "constants/config";
import type { GetServerSidePropsContext } from "next";

/**
 * @page RobotsDotTxt Page
 * @description Page to display a dynamically generated robots.txt file.
 */
const RobotsDotTxt = () => {
  // Empty. getServerSideProps writes txt directly to the browser.
};

export const getServerSideProps = async (
  context: GetServerSidePropsContext
) => {
  context.res.setHeader("Content-Type", "text/plain");
  if (IS_PRODUCTION_ENV) {
    context.res.write(
      `User-agent: *
Allow: /home/wp-content/uploads/
Disallow: /home/wp-content/plugins/
Disallow: /home/wp-admin/
Disallow: /home/readme.html
Crawl-delay: 1

User-agent: Yandex
Disallow: /

Sitemap: https://consensus.app/sitemap.xml`
    );
  } else {
    // Prevent crawling non-production site
    context.res.write(
      `User-agent: *
Disallow: /`
    );
  }
  context.res.end();
  return { props: {} };
};

export default RobotsDotTxt;
