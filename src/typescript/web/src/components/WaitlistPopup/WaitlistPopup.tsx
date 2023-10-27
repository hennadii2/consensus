import { useUser } from "@clerk/nextjs";
import Icon from "components/Icon";
import Logo from "components/Logo";
import Modal from "components/Modal";
import { TWITTER } from "constants/config";
import path from "constants/path";
import useLabels from "hooks/useLabels";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";

// Time to wait after page load before showing the waitlist popup
const WAITING_IN_MILISECOND = 10000;
const SHOW_WAITLIST_POPUP = "SHOW_WAITLIST_POPUP";

declare global {
  interface Window {
    // Adds a quick type to satisfy the type checker.
    Cypress: any;
  }
}

type WaitlistPopupProps = {};

/**
 * @component WaitlistPopup
 * @description Component waitlist popup
 * @example
 * return (
 *   <WaitlistPopup />
 * )
 */
function WaitlistPopup({}: WaitlistPopupProps) {
  const { isLoaded, user } = useUser();
  const [labels] = useLabels("waitlist");
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const onClose = () => {
    setOpen(false);
  };

  useEffect(() => {
    const alreadyOpen = localStorage.getItem(SHOW_WAITLIST_POPUP);
    const isTest = window.Cypress;

    if (!isTest && isLoaded && !user && alreadyOpen !== "true") {
      const timeout = setTimeout(() => {
        setOpen(true);
        localStorage.setItem(SHOW_WAITLIST_POPUP, "true");
      }, WAITING_IN_MILISECOND);

      return () => {
        clearTimeout(timeout);
      };
    }
  }, [isLoaded, user]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    router.push(path.SIGN_UP);
  };

  return (
    <Modal size="xl" open={open} onClose={onClose}>
      <div className="text-center flex flex-col items-center py-8 relative">
        <button
          onClick={() => onClose()}
          className="absolute text-[#085394] top-0 right-0  outline-none"
        >
          <Icon name="x" />
        </button>
        <Logo size="large" />
        <p className="text-[#4B5854] text-xl font-bold mt-4 mb-8">
          {labels["subtitle"]}
        </p>
        {success ? (
          <>
            <p
              className="text-2xl text-[#364B44]"
              dangerouslySetInnerHTML={{
                __html: labels["success"].replace("{TWITTER}", TWITTER),
              }}
            ></p>
          </>
        ) : (
          <>
            <p
              className="text-2xl text-[#364B44]"
              dangerouslySetInnerHTML={{
                __html: labels["description-sign-up"],
              }}
            ></p>

            <form onSubmit={handleSubmit} className="mt-8 max-w-sm">
              {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
              <button
                type="submit"
                disabled={false}
                className="w-full disabled:opacity-60 font-bold px-4 py-3.5 rounded-full  bg-[#0A6DC2] text-white mt-5"
              >
                {labels["sign-up"]}
              </button>
              <div
                style={{
                  background:
                    "linear-gradient(270deg, rgba(222, 224, 227, 0) -6.68%, #DEE0E3 47.77%, rgba(222, 224, 227, 0) 100%)",
                }}
                className="w-full mt-10 h-[1px]"
              ></div>

              <div className="mt-10">
                <p className="text-[#4B5854]">
                  {labels["already-have-account"]}{" "}
                  <Link passHref href={path.SIGN_IN} legacyBehavior>
                    <a className="text-[#085394]">{labels["login"]}</a>
                  </Link>
                </p>
              </div>
            </form>
          </>
        )}
      </div>
    </Modal>
  );
}

export default WaitlistPopup;
