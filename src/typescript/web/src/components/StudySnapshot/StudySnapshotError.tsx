import useLabels from "hooks/useLabels";
import React from "react";

interface StudySnapshotErrorProps {}

function StudySnapshotError({}: StudySnapshotErrorProps) {
  const [pageLabels] = useLabels("study-snapshot");

  return (
    <div
      data-testid="study-snapshot-error"
      className="flex flex-wrap justify-center rounded-[16px] bg-[#F1F4F6]"
    >
      <img className="w-5 mr-2" alt="Alert" src="/icons/alert.svg" />
      <span className="text-base text-black">{pageLabels["error-msg"]}</span>
    </div>
  );
}

export default StudySnapshotError;
