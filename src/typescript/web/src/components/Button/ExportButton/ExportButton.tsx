import { useMutation } from "@tanstack/react-query";
import Button from "components/Button";
import { IconLoader } from "components/Icon";
import { FeatureFlag } from "enums/feature-flag";
import { download, generateCsv, mkConfig } from "export-to-csv";
import { getPapersList, ISearchItem } from "helpers/api";
import { paperDetailPagePath } from "helpers/pageUrl";
import useIsFeatureEnabled from "hooks/useIsFeatureEnabled";
import React, { useMemo } from "react";

type ExportButtonProps = {
  items: ISearchItem[];
  query: string;
};

type CsvData = {
  Title: string;
  Takeaway: string;
  Authors: string;
  Year: number;
  Citations: number;
  Abstract: string;
  "Study Type": string;
  Journal: string;
  "Journal SJR Quartile": string;
  DOI: string;
  "Consensus Link": string;
};

const FILENAME_MAX_LENGTH_CHARS = 300;

function escapeQuotesForCSV(input: string): string {
  return input.replace(/"/g, '""');
}

/**
 * @component ExportButton
 * @description Export a CSV file of search results
 * @example
 * return (
 *   <ExportButton/>
 * )
 */
const ExportButton = ({ items, query }: ExportButtonProps) => {
  const headers = [
    "Title",
    "Takeaway",
    "Authors",
    "Year",
    "Citations",
    "Abstract",
    "Study Type",
    "Journal",
    "Journal SJR Quartile",
    "DOI",
    "Consensus Link",
  ];
  const features = {
    enablePaperSearch: useIsFeatureEnabled(FeatureFlag.PAPER_SEARCH),
  };

  const getPapersListMutation = useMutation((ids: string[]) =>
    getPapersList(ids, {
      includeAbstract: true,
      includeJournal: true,
      enablePaperSearch: features.enablePaperSearch,
    })
  );

  const handleClick = async () => {
    try {
      const ids = items.map((item) => item.paper_id);
      const papersListData = await getPapersListMutation.mutateAsync(ids);

      const fullData = items.map((item): CsvData => {
        const itemDetails =
          papersListData.paperDetailsListByPaperId[item.paper_id];
        const quartile =
          itemDetails?.journal.scimago_quartile != null
            ? itemDetails?.journal.scimago_quartile.toString()
            : "";

        return {
          Title: escapeQuotesForCSV(itemDetails.title),
          Takeaway: escapeQuotesForCSV(itemDetails.abstract_takeaway),
          Authors: escapeQuotesForCSV(itemDetails.authors?.join(", ") || ""),
          Year: itemDetails.year,
          Citations: itemDetails?.citation_count || 0,
          Abstract: escapeQuotesForCSV(itemDetails?.abstract) || "",
          "Study Type": itemDetails.badges.study_type || "",
          Journal: itemDetails.journal.title,
          "Journal SJR Quartile": quartile,
          DOI: escapeQuotesForCSV(itemDetails.doi || ""),
          "Consensus Link":
            window.location.origin +
            paperDetailPagePath(
              itemDetails.url_slug || "details",
              item.paper_id
            ),
        };
      });

      const csvConfig = mkConfig({
        columnHeaders: headers,
        filename: filename,
        quoteStrings: true,
      });
      const csv = generateCsv(csvConfig)(fullData);
      download(csvConfig)(csv);
    } catch (error) {
      console.error(error);
    }
  };

  const filename = useMemo(() => {
    const sanitizedQuery = query
      .replace(/[?*:|"]/g, "")
      .substring(0, FILENAME_MAX_LENGTH_CHARS);
    const date = new Date().toLocaleDateString(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

    return `${sanitizedQuery} - ${date}`;
  }, [query]);

  return getPapersListMutation.isLoading ? (
    <div className="inline-flex items-center w-[36px] mr-3">
      <IconLoader color="black" />
    </div>
  ) : (
    <Button className="inline-flex items-center" onClick={handleClick}>
      <img alt="export" src="/icons/export.svg" className="w-5 h-5 mr-2" />
      Export csv
    </Button>
  );
};

export default ExportButton;
