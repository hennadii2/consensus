import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import React, { useRef, useState } from "react";

function AuthMessage() {
  const [expand, setExpand] = useState(false);
  const [pageLabels] = useLabels("screens.sign-in");
  const ref = useRef<HTMLDivElement>(null);

  return (
    <div
      onClick={() => setExpand(!expand)}
      data-testid="auth-message"
      className="cl-card cursor-pointer bg-white p-5 border border-[#D3EAFD] rounded-xl max-w-[25rem] m-auto mb-6"
    >
      <div className="flex justify-between items-center">
        <div className="flex">
          <img alt="question" src="/icons/question.svg" />
          <h4 className="font-bold text-base ml-2">
            {pageLabels["message-title"]}
          </h4>
        </div>
        {expand ? (
          <Icon size={18} name="minus" />
        ) : (
          <Icon size={18} name="plus" />
        )}
      </div>
      <div
        style={{
          height: expand
            ? ref.current?.clientHeight
              ? ref.current?.clientHeight + 4
              : "auto"
            : 0,
          transition: ".2s",
          overflow: "hidden",
        }}
      >
        <div className="text-sm" ref={ref}>
          <ul className="list-disc text-[#688092] mt-2 pl-5">
            <li>{pageLabels["message-1"]}</li>
            <li>{pageLabels["message-2"]}</li>
          </ul>
          <h4 className="font-bold text-base mt-4">
            {pageLabels["message-title-2"]}
          </h4>
          <p className="text-[#688092] mt-1">{pageLabels["message-desc"]}</p>
        </div>
      </div>
    </div>
  );
}

export default AuthMessage;
