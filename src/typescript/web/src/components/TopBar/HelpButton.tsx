import { Popover, Transition } from "@headlessui/react";
import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import React, { Fragment, useState } from "react";

interface HelpButtonProps {
  isSignedIn?: boolean;
}

function HelpButton({ isSignedIn }: HelpButtonProps) {
  const [helpLabels] = useLabels("tooltips.help");
  const [hover, setHover] = useState<null | number>(null);

  const items = [
    {
      icon: "magnifier",
      title: helpLabels["how-search"],
      desc: helpLabels["how-search-desc"],
      url: "https://consensus.app/home/blog/maximize-your-consensus-experience-with-these-best-practices/",
    },
    {
      icon: "artificial-intelligence",
      title: helpLabels["how-works"],
      desc: helpLabels["how-works-desc"],
      url: "https://consensus.app/home/blog/welcome-to-consensus/",
    },
    {
      icon: "mobile-app",
      title: helpLabels["add-to-home"],
      desc: helpLabels["add-to-home-desc"],
      url: "https://consensus.app/home/blog/how-to-add-to-home/",
    },
    {
      icon: "faq",
      isVisit: true,
      title: helpLabels["visit"],
      url: "https://consensus.app/home/blog/category/help-center/",
    },
  ];

  return (
    <Popover>
      {({ close }: any) => (
        <>
          <Popover.Button
            data-testid="help-button"
            className="bg-[#0A6DC2] w-10 h-10 rounded-full flex items-center justify-center"
          >
            <img alt="help" src="/icons/help.svg" className="w-6 h-6" />
          </Popover.Button>

          <Transition
            as={Fragment}
            enter="transition ease-out duration-200"
            enterFrom="opacity-0 translate-y-1"
            enterTo="opacity-100 translate-y-0"
            leave="transition ease-in duration-150"
            leaveFrom="opacity-100 translate-y-0"
            leaveTo="opacity-0 translate-y-1"
          >
            <Popover.Panel
              className={`absolute right-3 z-10 help-button ${
                isSignedIn ? "top-12" : "top-12"
              }`}
            >
              <div data-testid="help-content" className="pt-4 pb-2 text-sm">
                <div
                  className={`bg-[white] absolute h-3 w-3 -top-1 rotate-45 ${
                    isSignedIn ? "right-[54px]" : "right-[116px]"
                  }`}
                ></div>

                <div className="flex justify-between  px-6">
                  <h4 className="font-semibold mb-3 text-base">
                    {helpLabels["title"]}
                  </h4>
                </div>
                <div>
                  {items.map((item, index) => (
                    <div key={index}>
                      {item.isVisit && (
                        <div className="my-2 h-[0.5px] bg-[#EAF0F8] w-full"></div>
                      )}
                      <a href={item.url}>
                        <div
                          onMouseEnter={() => setHover(index)}
                          onMouseLeave={() => setHover(null)}
                          className="flex relative items-center py-2 hover:bg-[#F8F9FC] cursor-pointer px-6"
                        >
                          <div className="bg-[#E8F3FD] w-[48px] h-[48px] rounded-md mr-3 flex items-center justify-center">
                            <img
                              alt={item.icon}
                              src={`/icons/${item.icon}.svg`}
                            />
                          </div>
                          <div>
                            <p className="font-medium text-sm">{item.title}</p>
                            <p className="text-[#688092] text-sm">
                              {item.desc}
                            </p>
                          </div>
                          <div
                            className="absolute right-6"
                            style={{ opacity: index === hover ? 1 : 0 }}
                          >
                            <Icon name="arrow-right" />
                          </div>
                        </div>
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </Popover.Panel>
          </Transition>
        </>
      )}
    </Popover>
  );
}

export default HelpButton;
