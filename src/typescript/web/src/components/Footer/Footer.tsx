import Logo from "components/Logo";
import {
  CRUNCHBASE,
  INSTAGRAM,
  LINKEDIN,
  SLACK,
  TWITTER,
  WEB_URL,
} from "constants/config";
import { show as showIntercom } from "helpers/services/intercom";
import Link from "next/link";
import React from "react";

type FooterProps = {};

/**
 * @component Footer
 * @description Footer component.
 * @example
 * return (
 *   <Footer />
 * )
 */
const Footer = ({}: FooterProps) => {
  const company = [
    [
      {
        label: "Home",
        href: "/#",
        onClick: () => (window.location.href = "/#"),
      },
      {
        label: "About Us",
        href: WEB_URL + "/home/about-us/",
      },
      {
        label: "Contact",
        href: WEB_URL + "/home/contact-us/",
      },
      {
        label: "News",
        href: WEB_URL + "/home/blog/category/news/",
      },
    ],
    [
      {
        label: "Blog",
        href: WEB_URL + "/home/blog/",
      },
      {
        label: "Privacy Policy",
        href: WEB_URL + "/home/privacy-policy/",
      },
      ...[
        {
          label: "Pricing",
          href: WEB_URL + "/pricing/",
        },
      ],
      {
        label: "Sitemap",
        href: WEB_URL + "/sitemap.xml",
      },
    ],
  ];

  const product = [
    {
      label: "Beta Product",
      href: "/search",
    },
    {
      label: "Best Practices",
      href:
        WEB_URL +
        "/home/blog/maximize-your-consensus-experience-with-these-best-practices/",
    },
    {
      label: "Support",
      onClick: () => {
        showIntercom();
      },
    },
  ];

  return (
    <footer id="footer" className="bg-[#EFFCF8] rounded-t-2xl">
      <div className="container">
        <div className="md:grid gap-4 grid-cols-8  py-10 md:py-20 text-sm">
          <div className="col-span-3">
            <div className="hidden md:block">
              <Logo size="medium" />
            </div>
            <div className="md:hidden justify-center flex">
              <div className="bg-white p-2 mb-8 rounded-lg">
                <Logo size="small" />
              </div>
            </div>
          </div>
          <div className="col-span-3">
            <div className="grid grid-cols-1 md:grid-cols-3">
              <div className="text-[#808080] font-medium text-center md:text-left mb-5 text-lg md:text-sm">
                Company
              </div>
              {company.map((c, i) => (
                <div key={i} className="flex justify-evenly md:block">
                  {c.map((item) => (
                    <div
                      className="mb-3 md:mb-2 text-[#085394]"
                      key={item.label}
                    >
                      {item.onClick ? (
                        <a
                          className="cursor-pointer"
                          href={item.href}
                          onClick={item.onClick}
                        >
                          {item.label}
                        </a>
                      ) : (
                        <Link passHref href={item.href} legacyBehavior>
                          <a className="whitespace-nowrap">{item.label}</a>
                        </Link>
                      )}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 col-span-2 mt-6 md:mt-0">
            <div></div>
            <div className="text-[#808080] font-medium text-center md:text-left mb-5 text-lg md:text-sm">
              Product
            </div>
            <div className="flex justify-evenly md:block">
              {product.map((item) => (
                <div className="mb-3 md:mb-2 text-[#085394]" key={item.label}>
                  {item.onClick ? (
                    <a className="cursor-pointer" onClick={item.onClick}>
                      {item.label}
                    </a>
                  ) : (
                    <Link passHref href={item.href} legacyBehavior>
                      <a className="whitespace-nowrap">{item.label}</a>
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="col-span-8  mb-8 md:mb-0 flex items-center md:justify-end  justify-center text-[#085394]">
            <div className="mt-8 md:-mt-12 flex gap-4">
              <a
                className="-mb-1"
                rel="noreferrer"
                target="_blank"
                href={TWITTER}
              >
                <img alt="Twitter" src="/icons/twitter.svg" />
              </a>
              <a rel="noreferrer" target="_blank" href={LINKEDIN}>
                <img alt="Linkedin" src="/icons/linkedin.svg" />
              </a>
              <a rel="noreferrer" target="_blank" href={INSTAGRAM}>
                <img alt="Instagram" src="/icons/instagram.svg" />
              </a>
              <a rel="noreferrer" target="_blank" href={CRUNCHBASE}>
                <img alt="Crunchbase" src="/icons/crunchbase.svg" />
              </a>
              <a rel="noreferrer" target="_blank" href={SLACK}>
                <img
                  alt="Slack"
                  className="w-6 h-6 text-[#085394]"
                  src="/icons/slack.svg"
                />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
