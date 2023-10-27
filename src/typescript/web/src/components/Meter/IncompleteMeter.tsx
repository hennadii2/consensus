import Tag from "components/Tag";
import { EXAMPLE_QUERY_IN_METER } from "constants/config";
import { setSynthesizeOn } from "helpers/setSynthesizeOn";
import useLabels from "hooks/useLabels";
import useSearch from "hooks/useSearch";
import React from "react";

type Props = {
  isIncompleteAll?: boolean;
};

function IncompleteMeter({ isIncompleteAll }: Props) {
  const [meterLabels] = useLabels("meter");
  const { handleSearch } = useSearch();

  return (
    <div className="text-sm flex flex-col gap-y-2 bg-[#F1F4F6] text-[#364B44] rounded-lg p-4 text-center items-center">
      {isIncompleteAll ? (
        <p>
          <strong>{meterLabels["incomplete"]["not-enough"]}</strong>{" "}
          {meterLabels["incomplete"]["try-asking"]}
        </p>
      ) : (
        <p>
          <strong>{meterLabels["incomplete"]["not-enough-predictions"]}</strong>{" "}
          {meterLabels["incomplete"]["needs-at-least-5"]}
        </p>
      )}
      <Tag
        q={EXAMPLE_QUERY_IN_METER}
        onClick={(event) => {
          event.preventDefault();
          setSynthesizeOn();
          handleSearch(EXAMPLE_QUERY_IN_METER);
        }}
      >
        e.g. {EXAMPLE_QUERY_IN_METER}
      </Tag>
    </div>
  );
}

export default IncompleteMeter;
