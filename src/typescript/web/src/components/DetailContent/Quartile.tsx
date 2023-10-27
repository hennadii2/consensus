import Tooltip from "components/Tooltip";
import { show as showIntercom } from "helpers/services/intercom";
import useLabels from "hooks/useLabels";

type QuartileProps = {
  quartile: number | null;
};

function Quartile({ quartile }: QuartileProps) {
  if (quartile !== null && ![1, 2, 3, 4].includes(quartile)) {
    throw new Error(
      "Invalid quartile value. Expected a number between 1 and 4."
    );
  }
  const colorMap = [
    "", // Index starts at 1
    "bg-green-500",
    "bg-yellow-450",
    "bg-yellow-450",
    "bg-red-550",
  ];

  const [quartileLabels] = useLabels("quartile");

  return (
    <Tooltip
      interactive
      maxWidth={334}
      tooltipContent={
        <div>
          <p className="text-gray-700 text-lg">
            {quartileLabels["title"]} -{" "}
            <span className="font-bold">
              {quartile ? `Q${quartile}` : "UNKNOWN"}
            </span>
          </p>
          <div className="flex flex-row gap-x-1 my-2">
            {[4, 3, 2, 1].map((q) => (
              <div
                key={q}
                role="img"
                aria-label={`Quartile ${q} bubble`}
                className={`w-5 h-2 rounded-full ${
                  quartile && quartile <= q ? colorMap[quartile] : "bg-gray-250"
                } `}
              />
            ))}
          </div>
          {!quartile ? (
            <p className="text-base mb-2 italic">
              {quartileLabels["we-could-not-map"]}{" "}
              <a
                onClick={() => showIntercom()}
                className="text-[#0A6DC2] cursor-pointer font-semibold"
              >
                here
              </a>
              .
            </p>
          ) : null}
          <p className="text-base">
            <a
              className="text-[#0A6DC2] font-semibold"
              target="_blank"
              rel="noreferrer"
              href="https://www.scimagojr.com/journalrank.php"
            >
              {quartileLabels["scimago-journal-rank"]}
            </a>{" "}
            {quartileLabels["description"]}
          </p>
        </div>
      }
    >
      <div className="flex flex-row items-center text-xs gap-x-2">
        <p className="text-gray-400">{quartileLabels["title"]}</p>
        <div className="flex flex-row gap-x-1">
          {quartile === null ? (
            <span className="font-bold text-gray-400">UNKNOWN</span>
          ) : (
            <>
              {[4, 3, 2, 1].map((q) => (
                <div
                  key={q}
                  role="img"
                  aria-label={`Quartile ${q} bubble`}
                  className={`w-5 h-2 rounded-full ${
                    quartile <= q ? colorMap[quartile] : "bg-gray-250"
                  } `}
                />
              ))}
            </>
          )}
        </div>
      </div>
    </Tooltip>
  );
}

export default Quartile;
