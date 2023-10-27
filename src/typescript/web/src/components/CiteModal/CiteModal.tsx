import { Tab } from "@headlessui/react";
import classNames from "classnames";
import Modal from "components/Modal";
import copyText from "helpers/copyText";
import useLabels from "hooks/useLabels";
import React, { useMemo, useRef, useState } from "react";

// Number of ms for how long it takes to display the confirmation message after click copy.
const COPY_TIMEOUT_MILLISECONDS = 3000;

enum Copy {
  EMPTY = "EMPTY",
  LINK = "LINK",
  TEXT = "TEXT",
  LINK_TEXT = "LINK_TEXT",
}

type CiteModalProps = {
  open?: boolean;
  title: string;
  apa: string;
  mla: string;
  chicago: string;
  harvard: string;
  bibtex: string;
  onClose: (value: boolean) => void;
};

/**
 * @component CiteModal
 * @description Component for share modal
 * @example
 * return (
 *   <CiteModal
 *    open={true}
 *    onClick={fn}
 *    title="Share"
 *    shareText=""
 *    text="Hello"
 *   />
 * )
 */
function CiteModal({
  onClose,
  open,
  title,
  apa,
  bibtex,
  chicago,
  mla,
  harvard,
}: CiteModalProps) {
  const [shareLabels] = useLabels("share");

  const [isCopied, setIsCopied] = useState<Copy>(Copy.EMPTY);

  const refContent = useRef<HTMLDivElement>(null);

  const tabs = useMemo(
    () => [
      {
        key: "apa",
        title: "APA",
        content: apa,
      },
      {
        key: "mla",
        title: "MLA",
        content: mla,
      },
      {
        key: "chicago",
        title: "Chicago",
        content: chicago,
      },
      {
        key: "harvard",
        title: "Harvard",
        content: harvard,
      },
      {
        key: "bibtex",
        title: "BibTeX",
        content: bibtex,
      },
    ],
    [apa, mla, bibtex, chicago, harvard]
  );

  const handleClickCopyText = () => {
    const text = refContent.current?.textContent;
    if (text) {
      setIsCopied(Copy.TEXT);
      copyText(text);

      setTimeout(() => {
        setIsCopied(Copy.EMPTY);
      }, COPY_TIMEOUT_MILLISECONDS);
    }
  };

  return (
    <>
      <Modal open={open} onClose={onClose} size="lg" padding={false}>
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat"
          data-testid="cite-modal"
        >
          <div>
            <h3 className="text-2xl text-center font-semibold text-black max-w-sm mx-auto">
              {title}
            </h3>
          </div>
          <div className="mt-9">
            <Tab.Group>
              <Tab.List className="flex space-x-1 bg-transparent border-b border-white">
                {tabs.map((tab) => (
                  <Tab
                    key={tab.key}
                    className={({ selected }) =>
                      classNames(
                        "w-full py-2.5 leading-5",
                        "ring-transparent ring-opacity-60 focus:outline-none focus:ring-2",
                        selected
                          ? "text-black font-bold border-b-4 border-b-[#57AC91]"
                          : "text-[#707070]"
                      )
                    }
                  >
                    {tab.title}
                  </Tab>
                ))}
              </Tab.List>
              <Tab.Panels className="mt-5">
                {tabs.map((tab) => (
                  <Tab.Panel
                    key={tab.key}
                    className="text-lg py-2 px-4 rounded-md bg-white min-h-[260px] sm:overflow-y-auto"
                  >
                    <div
                      ref={refContent}
                      className="text-[#303A40] text-base"
                      dangerouslySetInnerHTML={{ __html: tab.content }}
                    />
                  </Tab.Panel>
                ))}
              </Tab.Panels>
            </Tab.Group>
          </div>

          <div className="mt-6">
            <button
              onClick={handleClickCopyText}
              className="flex w-full justify-center bg-[#D3EAFD] text-[#085394] h-11 rounded-full items-center cursor-pointer"
            >
              <img
                alt="share-copy-text"
                src="/icons/share-copy-text.svg"
                className="mr-3 h-5"
              />
              {shareLabels["copy-text"]}
            </button>
          </div>
        </div>
      </Modal>
      <div
        style={{ top: 20, right: isCopied !== Copy.EMPTY ? 20 : -500 }}
        className="fixed duration-200 bg-green-600 px-6 py-2 rounded-md text-white z-[1000]"
      >
        {shareLabels[isCopied]} {shareLabels["copy-message"]}
      </div>
    </>
  );
}

export default CiteModal;
