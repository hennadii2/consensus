import { useEffect } from "react";

type ResultDetailDoiProps = {
  doi?: string;
};
const ResultDetailDoi = ({ doi }: ResultDetailDoiProps) => {
  useEffect(() => {
    // Force Zotero to refresh metadata - When the display is loaded (component did mount), trigger a ZoteroItemUpdated event to instruct Zotero to re-detect metadata on the page.
    // https://www.zotero.org/support/dev/exposing_metadata#force_zotero_to_refresh_metadata
    document.dispatchEvent(
      new Event("ZoteroItemUpdated", {
        bubbles: true,
        cancelable: true,
      })
    );
  }, []);
  return (
    <span style={{ display: "none" }} className="zotero-doi">
      DOI: {doi}
    </span>
  );
};

export default ResultDetailDoi;
