import { UserButton as ClerkButton } from "@clerk/nextjs";
import path from "constants/path";
import { getReversedSubscriptionUsageData } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { useCallback, useEffect } from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

function UserButton() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const [creditTooltipLabel] = useLabels("ai-credits-tooltip");
  const hasSubscription = useAppSelector((state) =>
    Boolean(
      state.subscription.subscription.user ||
        state.subscription.subscription.org
    )
  );
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );

  const handleClickUpgradePremium = useCallback(async () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  }, [dispatch]);

  const injectSubscriptionButton = () => {
    const elements = document.getElementsByClassName(
      "cl-userButtonPopoverActions"
    );
    const actionsNode = elements[0];
    if (actionsNode) {
      const subscriptionNode = document.createElement("button");
      subscriptionNode.className =
        "cursor-pointer px-9 py-3 flex items-center hover:bg-gray-100 cl-userButtonPopoverActionButton__manageSubscription";
      subscriptionNode.onclick = () => {
        router.push(path.SUBSCRIPTION);
      };
      subscriptionNode.innerHTML = `
      <img width="20px" src="/icons/noun-payment.svg" />
      <span style="color: #000000A6; margin-left: 29px; font-size: 1.0005rem;text-align:left;">Manage subscription</span>
      `;

      const signOutNode = document.getElementsByClassName(
        "cl-userButtonPopoverActionButton__signOut"
      )[0];
      actionsNode.insertBefore(subscriptionNode, signOutNode);
    }
  };

  const injectCreditTag = () => {
    const elements = document.getElementsByClassName(
      "cl-userButtonPopoverActionButton__manageSubscription"
    );
    const actionsNode = elements[0];
    if (actionsNode) {
      const creditNode = createCreditTagNode();
      actionsNode.append(creditNode);
    }
  };

  const createCreditTooltipNode = () => {
    const tooltipNode = document.createElement("div");

    if (window.innerWidth < 400) {
      tooltipNode.className =
        "cl-userButtonCreditTooltip absolute right-[-30px] w-[300px] min-h-[200px] text-left bg-white p-[20px] hidden";
    } else {
      tooltipNode.className =
        "cl-userButtonCreditTooltip absolute right-0 w-[334px] min-h-[200px] text-left bg-white p-[20px] hidden";
    }

    tooltipNode.style.cssText =
      "cursor: auto; top: 100%; border-radius: 12px; box-shadow: 0px 12px 26px 0px rgba(189, 201, 219, 0.32);";
    tooltipNode.innerHTML = `
      <div class="flex items-center justify-start">
        <img
          class="w-[24px] h-[24px] mr-[6px]"
          alt="Sparkler"
          src="/icons/sparkler.svg"
        />
        <span class="text-lg text-[#364B44] font-bold">${creditTooltipLabel["title"]}</span>
      </div>

      <div class="mt-[12px] text-base text-[#364b44]">
        ${creditTooltipLabel["description"]}
      </div>

      <div class="flex flex-wrap items-center mt-[16px]">
        <img
          class="w-[16px] h-[16px] mr-[6px]"
          alt="coin"
          src="/icons/coin-blue.svg"
        />
        <span class="mr-1 text-base text-[#364B44] font-bold">${creditTooltipLabel["ai-credits-left"]} - </span>
        <span 
          class="text-base font-bold" 
          style="
            background: linear-gradient(76deg, #009FF5 -84.16%, #2BAE90 141.47%); 
            background-clip: text; 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
          ">${reversedSubscriptionUsageData.creditLeft}</span>
      </div>

      <div class="text-sm text-[#688092] mt-[4px]">
        <span class="mr-1">${creditTooltipLabel["renews-on"]}</span>
        <span class="font-bold">${reversedSubscriptionUsageData.refreshDate}</span>
      </div>

      <div class="flex flex-wrap items-center justify-between mt-[16px]">
        <span class="text-[#364b44] text-base">${creditTooltipLabel["need-unlimited?"]}</span>
        <button type="button" class="cl-userButtonCreditTooltip-upgradeButton transition bg-[#0A6DC2] text-white text-center justify-center inline-flex items-center text-sm rounded-full pt-2.5 pb-2.5 pl-7 pr-7 bg-opacity-80 hover:bg-opacity-100">
          ${creditTooltipLabel["upgrade"]}
        </button>
      </div>
    `;
    return tooltipNode;
  };

  const createCreditTagNode = () => {
    const creditNode = document.createElement("div");
    creditNode.className =
      "cl-userButtonCreditTag rounded-full flex justify-center items-center gap-[4px] h-[30px] bg-[#F1F4F6] px-[8px] ml-auto relative";
    creditNode.innerHTML = `
      <img
        class="w-[16px] h-[16px]"
        alt="coin"
        src="/icons/coin-blue.svg"
      />
      <span 
        class="font-bold text-base" 
        style="
          background: linear-gradient(76deg, #009FF5 -84.16%, #2BAE90 141.47%); 
          background-clip: text; 
          -webkit-background-clip: text; 
          -webkit-text-fill-color: transparent;
        ">
        ${reversedSubscriptionUsageData.creditLeft}
      </span>
    `;
    const creditTooltipNode = createCreditTooltipNode();
    creditNode.append(creditTooltipNode);

    const upgradeButtonElements = creditTooltipNode.getElementsByClassName(
      "cl-userButtonCreditTooltip-upgradeButton"
    );
    if (upgradeButtonElements && upgradeButtonElements.length > 0) {
      upgradeButtonElements[0].addEventListener("click", function (e) {
        creditTooltipNode.classList.add("hidden");
        handleClickUpgradePremium();
      });
    }

    document.addEventListener("click", function (e) {
      if (
        creditTooltipNode &&
        creditTooltipNode.classList.contains("hidden") == false
      ) {
        creditTooltipNode.classList.add("hidden");
      }
    });

    creditTooltipNode.onclick = function (event) {
      event.preventDefault();
      event.stopPropagation();
    };

    creditNode.onclick = function (event) {
      event.preventDefault();
      event.stopPropagation();

      if (isMobile && creditTooltipNode) {
        creditTooltipNode.classList.remove("hidden");
      }
    };

    creditNode.onmouseover = function (event) {
      if (!isMobile && creditTooltipNode) {
        creditTooltipNode.classList.remove("hidden");
      }
    };

    creditNode.onmouseout = function (event) {
      if (!isMobile) {
        creditTooltipNode.classList.add("hidden");
      }
    };
    return creditNode;
  };

  const createPremiunNode = (size: "medium" | "small" = "medium") => {
    const width = size === "medium" ? 18 : 16;
    const premiumNode = document.createElement("div");
    premiumNode.style.position = "absolute";
    premiumNode.style.height = `${width}px`;
    premiumNode.style.width = `${width}px`;
    premiumNode.style.display = "flex";
    premiumNode.style.justifyContent = "center";
    premiumNode.style.alignItems = "center";
    premiumNode.style.background = "white";
    premiumNode.style.borderRadius = "10px";
    premiumNode.style.right = size === "small" ? "-4px" : "-3px";
    premiumNode.style.top = "0px";
    premiumNode.style.zIndex = "2";

    premiumNode.innerHTML = `
      <img width="${width - 6}px" src="/icons/premium.svg" />
      `;
    return premiumNode;
  };

  useEffect(() => {
    if (hasSubscription) {
      const userButtonNode = document.getElementById("user-button");

      if (userButtonNode) {
        const premiumNode = createPremiunNode("small");
        userButtonNode.appendChild(premiumNode);
      }
    }
  }, [hasSubscription]);

  const injectPremiumUser = () => {
    const elements = document.getElementsByClassName(
      "cl-userPreviewAvatarContainer"
    );

    const avatarNode = elements[0];

    if (avatarNode) {
      const premiumNode = createPremiunNode();
      avatarNode.appendChild(premiumNode);
    }
  };

  const handleClick = async () => {
    injectSubscriptionButton();

    if (hasSubscription) {
      injectPremiumUser();
    } else {
      injectCreditTag();
    }
  };

  return (
    <button
      data-testid="user-button"
      type="button"
      id="user-button"
      className="flex items-center ml-3 relative"
      onClick={handleClick}
    >
      <ClerkButton
        userProfileUrl={path.ACCOUNT}
        signInUrl={path.SIGN_IN}
        afterSignOutUrl={path.SIGN_IN}
        userProfileMode="navigation"
        appearance={{
          elements: {
            avatarBox: {
              height: 40,
              width: 40,
            },
          },
        }}
      />
    </button>
  );
}

export default UserButton;
