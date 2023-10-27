import { useState } from "react";

const initial = {
  mla: "",
  apa: "",
  chicago: "",
  bibtex: "",
  harvard: "",
};

/**
 * @hook useCite
 * @description Hooks for cite.
 * @api openCite = will be true if native cite doesn't support
 * @api handleCite = function for cite
 * @api handleCloseCite = function for set openCite is false
 * @api citeData = state metadata cite
 * @api setCiteData = function for set metadata cite
 * @example
 * const { handleCite, openCite, handleCloseCite, citeData, setCiteData } = useCite();
 */
const useCite = () => {
  const [openCite, setOpenCite] = useState(false);
  const [citeData, setCiteData] = useState(initial);

  const handleCite = () => {
    setOpenCite(true);
  };

  const handleCloseCite = () => {
    setOpenCite(false);
    setTimeout(() => {
      setCiteData(initial);
    }, 500);
  };

  return {
    handleCite,
    handleCloseCite,
    openCite,
    citeData,
    setCiteData,
  };
};

export default useCite;
