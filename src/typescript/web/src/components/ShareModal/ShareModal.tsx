import Icon from "components/Icon";
import Modal from "components/Modal";
import { META_TWITTER_SITE } from "constants/config";
import copyText from "helpers/copyText";
import useLabels from "hooks/useLabels";
import React, { useState } from "react";

// Number of ms for how long it takes to display the confirmation message after click copy.
const COPY_TIMEOUT_MILLISECONDS = 3000;

// Share URL
const TWITTER_SHARE_URL = "https://twitter.com/intent/tweet";
export enum ButtonShare {
  TWITTER = "Twitter",
  COPY_TEXT = "Copy text",
  LINK_TEXT = "Link + Text",
  COPY_LINK = "Copy link",
}

enum Copy {
  EMPTY = "EMPTY",
  LINK = "LINK",
  TEXT = "TEXT",
  LINK_TEXT = "LINK_TEXT",
}

type ShareModalProps = {
  open?: boolean;
  title: string;
  text: string;
  url?: string;
  subText?: string;
  shareText: string;
  onClose: (value: boolean) => void;
  onClickButton?: (type: ButtonShare) => void;
  isDetail?: boolean;
  summaryText?: string;
};

/**
 * @component ShareModal
 * @description Component for share modal
 * @example
 * return (
 *   <ShareModal
 *    open={true}
 *    onClick={fn}
 *    title="Share"
 *    shareText=""
 *    text="Hello"
 *   />
 * )
 */
function ShareModal({
  onClose,
  open,
  title,
  url,
  text,
  subText,
  shareText,
  onClickButton,
  isDetail,
  summaryText,
}: ShareModalProps) {
  const [shareLabels] = useLabels("share");

  const [isCopied, setIsCopied] = useState<Copy>(Copy.EMPTY);
  const [includeQueryLink, setIncludeQueryLink] = useState(false);
  const [includeSummaryLink, setIncludeSummaryLink] = useState(false);

  const handleClickCopyLink = () => {
    setIsCopied(Copy.LINK);
    const link = url || window.location.href;
    copyText(link);
    onClickButton?.(ButtonShare.COPY_LINK);

    setTimeout(() => {
      setIsCopied(Copy.EMPTY);
    }, COPY_TIMEOUT_MILLISECONDS);
  };

  const handleClickCopyText = () => {
    setIsCopied(Copy.TEXT);
    copyText(text);
    onClickButton?.(ButtonShare.COPY_TEXT);

    setTimeout(() => {
      setIsCopied(Copy.EMPTY);
    }, COPY_TIMEOUT_MILLISECONDS);
  };

  const handleClickCopyLinkText = () => {
    setIsCopied(Copy.LINK_TEXT);
    const link = url || window.location.href;
    let textToCopy = "";
    if (includeQueryLink) {
      textToCopy = `${isDetail ? `"${text}"` : text}
${link}`;
    }
    if (includeSummaryLink && !isDetail) {
      textToCopy = `${summaryText}
${link}`;
    }
    if (includeQueryLink && includeSummaryLink && !isDetail) {
      textToCopy = `${isDetail ? `"${text}"` : text}
${summaryText}
${link}`;
    }
    copyText(textToCopy);
    onClickButton?.(ButtonShare.LINK_TEXT);

    setTimeout(() => {
      setIsCopied(Copy.EMPTY);
    }, COPY_TIMEOUT_MILLISECONDS);
  };

  const handleClickTwitter = () => {
    const link = url || window.location.href;
    onClose(true);
    onClickButton?.(ButtonShare.TWITTER);
    window.open(
      `${TWITTER_SHARE_URL}?text=${encodeURIComponent(
        shareText
          .replace("Consensus", META_TWITTER_SITE)
          .replace("{text}", text)
          .replace("{url}", link)
      )}`
    );
  };

  return (
    <>
      <Modal open={open} onClose={onClose} size="lg" padding={false}>
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat"
          data-testid="share-modal"
        >
          <div>
            <h3 className="text-2xl text-center font-semibold text-black max-w-sm mx-auto">
              {title}
            </h3>
          </div>
          <div className="mt-9">
            <div className="text-lg py-2 px-4 rounded-md bg-white">
              <div className="flex">
                {isDetail ? null : (
                  <Icon
                    size={20}
                    className="mr-2 mt-1 text-[#085394]"
                    name="search"
                  />
                )}
                <p
                  className="text-[#303A40]"
                  dangerouslySetInnerHTML={{ __html: text }}
                ></p>
              </div>
              {subText && (
                <p className="text-xs text-gray-400 mt-2 ">{subText}</p>
              )}
            </div>
          </div>

          <div className="mt-6">
            {!isDetail ? (
              <button
                onClick={
                  includeQueryLink || includeSummaryLink
                    ? handleClickCopyLinkText
                    : handleClickCopyLink
                }
                className="flex w-full justify-center bg-primary text-white py-3 rounded-full items-center cursor-pointer mt-6"
              >
                <Icon size={20} className="mr-2" name="link-2" />
                {shareLabels["copy-link"]}
              </button>
            ) : (
              <button
                onClick={
                  includeQueryLink
                    ? handleClickCopyLinkText
                    : handleClickCopyText
                }
                className="flex w-full justify-center bg-[#D3EAFD] text-[#085394] py-3 rounded-full items-center cursor-pointer"
              >
                <img
                  alt="share-copy-text"
                  src="/icons/share-copy-text.svg"
                  className="mr-3 h-5"
                />
                {shareLabels["copy-text"]}
              </button>
            )}
            <div className="flex items-center mt-3">
              <input
                checked={includeQueryLink}
                onChange={(e) => setIncludeQueryLink(e.target.checked)}
                id="include"
                type="checkbox"
                className="h-6"
              />
              <label htmlFor="include" className="ml-2 text-black">
                {!isDetail
                  ? shareLabels["include-query-link"]
                  : shareLabels["include-link"]}
              </label>
            </div>

            {!isDetail && summaryText ? (
              <div className="flex items-center mt-3">
                <input
                  checked={includeSummaryLink}
                  onChange={(e) => setIncludeSummaryLink(e.target.checked)}
                  id="include-summary"
                  type="checkbox"
                  className="h-6"
                />
                <label htmlFor="include-summary" className="ml-2 text-black">
                  {shareLabels["include-summary-link"]}
                </label>
              </div>
            ) : null}

            <div className="mt-5 flex items-center">
              <div className="border-t border-gray-200 flex-1"></div>
              <div className="w-10 text-center text-[#688092]">
                {shareLabels["or"]}
              </div>
              <div className="border-t border-gray-200 flex-1"></div>
            </div>

            {isDetail ? (
              <button
                onClick={handleClickCopyLink}
                className="flex w-full justify-center bg-primary text-white py-3 rounded-full items-center cursor-pointer mt-6"
              >
                <Icon size={20} className="mr-2" name="link-2" />
                {shareLabels["copy-link"]}
              </button>
            ) : null}
            <button
              onClick={handleClickTwitter}
              data-testid="twitter-share"
              className="flex w-full justify-center bg-[#2AA3EF] text-white py-3 rounded-full items-center cursor-pointer mt-4"
            >
              <Icon size={20} className="mr-2" name="twitter" />
              {shareLabels["share-on-twitter"]}
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

export default ShareModal;
