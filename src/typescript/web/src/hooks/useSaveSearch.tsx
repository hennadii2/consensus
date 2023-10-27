import { useAppSelector } from "hooks/useStore";
import { useState } from "react";

/**
 * @hook useSaveSearch
 * @description Hooks for savesearch.
 * @example
 * const { openSaveSearchPopup, handleSaveSearch, handleCloseSaveSearch } = useSaveSearch();
 */
const useSaveSearch = () => {
  const [openSaveSearchPopup, setOpenSaveSearchPopup] = useState(false);
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const handleSaveSearch = () => {
    setOpenSaveSearchPopup(true);
  };

  const handleCloseSaveSearch = () => {
    setOpenSaveSearchPopup(false);
  };

  return {
    openSaveSearchPopup,
    handleSaveSearch,
    handleCloseSaveSearch,
  };
};

export default useSaveSearch;
