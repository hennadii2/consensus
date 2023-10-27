import { useAppSelector } from "hooks/useStore";
import { useState } from "react";

const initial = {
  url: "",
  title: "",
  text: "",
  subText: "",
  shareText: "",
  isDetail: false,
};

/**
 * @hook useShare
 * @description Hooks for share.
 * @api openShare = will be true if native share doesn't support
 * @api handleShare = function for share
 * @api handleCloseShare = function for set openShare is false
 * @api shareData = state metadata share
 * @api setShareData = function for set metadata share
 * @example
 * const { handleShare, openShare, handleCloseShare, shareData, setShareData } = useShare();
 */
const useShare = () => {
  const [openShare, setOpenShare] = useState(false);
  const [shareData, setShareData] = useState(initial);
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const handleShare = ({ title, url }: { title: string; url: string }) => {
    if (isMobile && navigator.share) {
      navigator.share({ title, url });
    } else {
      setOpenShare(true);
    }
  };

  const handleCloseShare = () => {
    setOpenShare(false);
    setTimeout(() => {
      setShareData(initial);
    }, 500);
  };

  return {
    handleShare,
    handleCloseShare,
    openShare,
    shareData,
    setShareData,
  };
};

export default useShare;
