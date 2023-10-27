import { ImageResponse } from "@vercel/og";
import LABELS from "constants/labels.json";
import {
  getSearchWithNativeFetch,
  getSummaryResponseWithNativeFetch,
  getYesNoResultsWithNativeFetch,
  SummaryResponse,
  YesNoResponse,
} from "helpers/api";
import type { NextApiRequest } from "next";

export const config = {
  runtime: "edge",
};

const fontRegular = fetch(
  new URL(
    "../../../../public/fonts/ProductSans-Regular.ttf",
    import.meta.url
  ) as any
).then((res) => res.arrayBuffer());

const fontBold = fetch(
  new URL(
    "../../../../public/fonts/ProductSans-Bold.ttf",
    import.meta.url
  ) as any
).then((res) => res.arrayBuffer());

export default async function handler(req: NextApiRequest) {
  const fontDataRegular = await fontRegular;
  const fontDataBold = await fontBold;
  const { search } = new URL(req.url!);
  const querySearch = decodeURIComponent(search);

  const queryTextBtoa = querySearch.replace("?search=", "");
  const queryText = atob(queryTextBtoa);

  const resSearch = await getSearchWithNativeFetch(queryText);
  const searchId = resSearch.id;

  let resSummaryResponse: SummaryResponse | null = null;
  let resYesNoResponse: YesNoResponse | null = null;
  let isErrorSummary = false;
  let isErrorYesNo = false;

  try {
    resSummaryResponse = await getSummaryResponseWithNativeFetch(searchId);
  } catch (error) {
    isErrorSummary = true;
  }
  try {
    resYesNoResponse = await getYesNoResultsWithNativeFetch(searchId);
  } catch (error) {
    isErrorYesNo = true;
  }

  const isIncompleteAll =
    (resYesNoResponse?.isIncomplete && resSummaryResponse?.isIncomplete) ||
    (!resSearch?.isYesNoQuestion && resSummaryResponse?.isIncomplete) ||
    !resSearch.canSynthesizeSucceed;

  const ogDynamicResultsBackground = await fetch(
    new URL(
      "../../../../public/images/og-dynamic-results-background.png",
      import.meta.url
    ) as any
  ).then((res) => res.arrayBuffer());

  const ogResults = await fetch(
    new URL("../../../../public/images/og-results.png", import.meta.url) as any
  ).then((res) => res.arrayBuffer());

  const render = () => {
    if (isIncompleteAll) {
      return (
        // eslint-disable-next-line jsx-a11y/alt-text
        <img
          width="1200"
          height="630"
          tw="flex absolute"
          src={ogResults as unknown as string}
        />
      );
    }
    if (resSummaryResponse && resYesNoResponse) {
      const { summary, resultsAnalyzedCount: resultsAnalyzedCountSummary } =
        resSummaryResponse;
      const { yesNoAnswerPercents } = resYesNoResponse;
      if (summary && yesNoAnswerPercents) {
        return (
          <>
            {/* eslint-disable-next-line jsx-a11y/alt-text */}
            <img
              width="1200"
              height="630"
              tw="flex absolute"
              src={ogDynamicResultsBackground as unknown as string}
            />
            <div tw="flex w-[1200px] h-[630px] px-[117px] pt-[144px] pb-[61px] flex-col">
              <div tw="flex items-center h-[80px] w-[976px] pl-[24px] pr-[117px]">
                <div
                  style={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  tw="flex text-[28px] text-[#222F2B]"
                >
                  {queryText}
                </div>
              </div>
              <div tw="flex flex-row mt-[37px] h-[308px] rounded-[20.5px] w-full bg-white p-8">
                <div tw="flex flex-col flex-1 pr-[22px] border-r border-r-[#D3EAFD]">
                  <div tw="flex w-full flex-row justify-between items-center h-[42px]">
                    <div tw="flex items-center">
                      <span tw="text-base text-[28px] font-bold text-[#364B44] mr-2">
                        {LABELS["question-summary"].summary}
                      </span>
                      <svg
                        width="29"
                        height="28"
                        viewBox="0 0 29 28"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <g clipPath="url(#clip0_5016_47768)">
                          <path
                            d="M14.9606 2.33203C8.52061 2.33203 3.29395 7.5587 3.29395 13.9987C3.29395 20.4387 8.52061 25.6654 14.9606 25.6654C21.4006 25.6654 26.6273 20.4387 26.6273 13.9987C26.6273 7.5587 21.4006 2.33203 14.9606 2.33203ZM16.1273 19.832H13.7939V12.832H16.1273V19.832ZM16.1273 10.4987H13.7939V8.16537H16.1273V10.4987Z"
                            fill="#4A98F6"
                          />
                        </g>
                        <defs>
                          <clipPath id="clip0_5016_47768">
                            <rect
                              width="28"
                              height="28"
                              fill="white"
                              transform="translate(0.960938)"
                            />
                          </clipPath>
                        </defs>
                      </svg>
                    </div>
                    {resultsAnalyzedCountSummary ? (
                      <span tw="font-normal text-[20px] text-[#889CAA]">
                        {LABELS["question-summary"]["papers-analyzed"].replace(
                          "{count}",
                          resultsAnalyzedCountSummary.toString()
                        )}
                      </span>
                    ) : null}
                  </div>
                  <div
                    style={{
                      overflow: "hidden",
                      display: "-webkit-box",
                      WebkitBoxOrient: "vertical",
                      WebkitLineClamp: 4,
                    }}
                    tw="text-[24px] text-[#222F2B] leading-[42px] mt-4 h-[170px]"
                  >
                    {summary || ""}
                  </div>
                </div>
                <div tw="flex flex-col flex-1 pl-[39px]">
                  <div tw="flex w-full flex-row justify-between items-center h-[42px]">
                    <div tw="flex items-center">
                      <span tw="text-base text-[28px] font-bold text-[#364B44] mr-2">
                        Consensus Meter
                      </span>
                      <svg
                        width="29"
                        height="28"
                        viewBox="0 0 29 28"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <g clipPath="url(#clip0_5016_47768)">
                          <path
                            d="M14.9606 2.33203C8.52061 2.33203 3.29395 7.5587 3.29395 13.9987C3.29395 20.4387 8.52061 25.6654 14.9606 25.6654C21.4006 25.6654 26.6273 20.4387 26.6273 13.9987C26.6273 7.5587 21.4006 2.33203 14.9606 2.33203ZM16.1273 19.832H13.7939V12.832H16.1273V19.832ZM16.1273 10.4987H13.7939V8.16537H16.1273V10.4987Z"
                            fill="#4A98F6"
                          />
                        </g>
                        <defs>
                          <clipPath id="clip0_5016_47768">
                            <rect
                              width="28"
                              height="28"
                              fill="white"
                              transform="translate(0.960938)"
                            />
                          </clipPath>
                        </defs>
                      </svg>
                    </div>
                  </div>
                  <div tw="flex flex-col w-full gap-y-3 mt-[43px] text-sm sm:leading-[1.375rem] text-[#688092]">
                    <div tw="flex items-center w-full">
                      <div tw="w-[175px] flex items-center mb-2 md:mb-0">
                        <svg
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            fillRule="evenodd"
                            clipRule="evenodd"
                            d="M12 0C5.38125 0 0 5.38125 0 12C0 18.6187 5.38125 24 12 24C18.6187 24 24 18.6187 24 12C24 5.38125 18.6187 0 12 0Z"
                            fill="#46A759"
                          />
                          <path
                            fillRule="evenodd"
                            clipRule="evenodd"
                            d="M17.8031 7.95391C18.0937 8.24453 18.0937 8.72266 17.8031 9.01328L10.7719 16.0445C10.6266 16.1898 10.4344 16.2648 10.2422 16.2648C10.05 16.2648 9.85781 16.1898 9.7125 16.0445L6.19687 12.5289C5.90625 12.2383 5.90625 11.7602 6.19687 11.4695C6.4875 11.1789 6.96562 11.1789 7.25625 11.4695L10.2422 14.4555L16.7437 7.95391C17.0344 7.65859 17.5125 7.65859 17.8031 7.95391Z"
                            fill="white"
                          />
                        </svg>
                        <span tw="ml-3 text-[18px]">
                          {LABELS.meter.YES} - {yesNoAnswerPercents.YES || 0}%
                        </span>
                      </div>
                      <div tw="flex h-[15px] flex-1 bg-[#DEE0E3] rounded-[2px]">
                        <div
                          style={{
                            width: `${yesNoAnswerPercents.YES || 0}%`,
                          }}
                          tw="bg-[#46A759] h-full rounded"
                        ></div>
                      </div>
                    </div>
                    <div tw="flex items-center w-full mt-5">
                      <div tw="w-[175px] flex items-center mb-2 md:mb-0">
                        <svg
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0C5.37258 0 0 5.37258 0 12C0 18.6274 5.37258 24 12 24Z"
                            fill="#F89C11"
                          />
                          <path
                            d="M10.1292 6.75138C9.92851 7.0517 9.80378 7.39485 9.76392 7.75141H7.59047C7.63215 7.01971 7.85539 6.30844 8.24174 5.68258C8.67198 4.98562 9.28756 4.42203 10.0197 4.05479C10.7518 3.68754 11.5716 3.53111 12.3875 3.60297C13.2034 3.67484 13.9833 3.97217 14.6399 4.46173C15.2966 4.9513 15.8041 5.61382 16.1059 6.37526C16.4077 7.13669 16.4918 7.96705 16.3488 8.77354C16.2059 9.58003 15.8415 10.3309 15.2963 10.9422C14.7512 11.5535 14.0468 12.0011 13.2619 12.2352L13.0833 12.2884V12.4747V15.7514H10.9167V11.3347C10.9167 11.0474 11.0308 10.7719 11.234 10.5687C11.4371 10.3655 11.7127 10.2514 12 10.2514C12.445 10.2514 12.88 10.1194 13.25 9.87222C13.62 9.62498 13.9084 9.27358 14.0787 8.86245C14.249 8.45131 14.2936 7.99891 14.2068 7.56246C14.1199 7.126 13.9056 6.72509 13.591 6.41042C13.2763 6.09575 12.8754 5.88146 12.4389 5.79464C12.0025 5.70783 11.5501 5.75238 11.1389 5.92268C10.7278 6.09298 10.3764 6.38137 10.1292 6.75138Z"
                            fill="white"
                            stroke="#F89C11"
                            strokeWidth="0.5"
                          />
                          <path
                            d="M13.0833 19.3353C13.0833 19.9336 12.5983 20.4186 12 20.4186C11.4017 20.4186 10.9167 19.9336 10.9167 19.3353C10.9167 18.737 11.4017 18.252 12 18.252C12.5983 18.252 13.0833 18.737 13.0833 19.3353Z"
                            fill="white"
                            stroke="#F89C11"
                            strokeWidth="0.5"
                          />
                        </svg>
                        <span tw="ml-3 text-[18px]">
                          {LABELS.meter.POSSIBLY} -{" "}
                          {yesNoAnswerPercents.POSSIBLY || 0}%
                        </span>
                      </div>
                      <div tw="flex h-[15px] flex-1 bg-[#DEE0E3] rounded-[2px]">
                        <div
                          style={{
                            width: `${yesNoAnswerPercents.POSSIBLY || 0}%`,
                          }}
                          tw="bg-[#FFB800] h-full rounded"
                        ></div>
                      </div>
                    </div>
                    <div tw="flex items-center w-full mt-5">
                      <div tw="w-[175px] flex items-center mb-2 md:mb-0">
                        <svg
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <g clipPath="url(#clip0_1636_1863)">
                            <path
                              d="M12 24.0001C18.6275 24.0001 24.0001 18.6275 24.0001 12C24.0001 5.3726 18.6275 0 12 0C5.3726 0 0 5.3726 0 12C0 18.6275 5.3726 24.0001 12 24.0001Z"
                              fill="#E3504F"
                            />
                            <path
                              d="M17.475 17.475C17.025 17.9249 16.275 17.9249 15.825 17.475L12 13.65L8.17505 17.475C7.72506 17.9249 6.97502 17.9249 6.52504 17.475C6.07506 17.025 6.07506 16.2749 6.52504 15.825L10.35 12L6.52504 8.17499C6.07506 7.72501 6.07506 6.97497 6.52504 6.52499C6.97502 6.075 7.72506 6.075 8.17505 6.52499L12 10.35L15.825 6.52499C16.275 6.075 17.025 6.075 17.475 6.52499C17.925 6.97497 17.925 7.72501 17.475 8.17499L13.65 12L17.475 15.825C17.925 16.2749 17.925 17.0249 17.475 17.475Z"
                              fill="white"
                            />
                          </g>
                          <defs>
                            <clipPath id="clip0_1636_1863">
                              <rect width="24" height="24" fill="white" />
                            </clipPath>
                          </defs>
                        </svg>
                        <span tw="ml-3 text-[18px]">
                          {LABELS.meter.NO} - {yesNoAnswerPercents.NO || 0}%
                        </span>
                      </div>
                      <div tw="flex h-[15px] flex-1 bg-[#DEE0E3] rounded-[2px]">
                        <div
                          style={{
                            width: `${yesNoAnswerPercents.NO || 0}%`,
                          }}
                          tw="bg-[#E3504F] h-full rounded"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      }
      return (
        <>
          {/* eslint-disable-next-line jsx-a11y/alt-text */}
          <img
            width="1200"
            height="630"
            tw="flex absolute"
            src={ogDynamicResultsBackground as unknown as string}
          />
          <div tw="flex w-[1200px] h-[630px] px-[117px] pt-[144px] pb-[61px] flex-col">
            <div tw="flex items-center h-[80px] w-[976px] pl-[24px] pr-[117px]">
              <div
                style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                tw="flex text-[28px] text-[#222F2B]"
              >
                {queryText}
              </div>
            </div>
            <div tw="flex flex-col mt-[37px] h-[308px] rounded-[20.5px] w-full bg-white p-8">
              <div tw="flex w-full flex-row justify-between items-center h-[42px]">
                <div tw="flex items-center">
                  <span tw="text-base text-[28px] font-bold text-[#364B44] mr-2">
                    {LABELS["question-summary"].summary}
                  </span>
                  <svg
                    width="29"
                    height="28"
                    viewBox="0 0 29 28"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <g clipPath="url(#clip0_5016_47768)">
                      <path
                        d="M14.9606 2.33203C8.52061 2.33203 3.29395 7.5587 3.29395 13.9987C3.29395 20.4387 8.52061 25.6654 14.9606 25.6654C21.4006 25.6654 26.6273 20.4387 26.6273 13.9987C26.6273 7.5587 21.4006 2.33203 14.9606 2.33203ZM16.1273 19.832H13.7939V12.832H16.1273V19.832ZM16.1273 10.4987H13.7939V8.16537H16.1273V10.4987Z"
                        fill="#4A98F6"
                      />
                    </g>
                    <defs>
                      <clipPath id="clip0_5016_47768">
                        <rect
                          width="28"
                          height="28"
                          fill="white"
                          transform="translate(0.960938)"
                        />
                      </clipPath>
                    </defs>
                  </svg>
                </div>
                {resultsAnalyzedCountSummary ? (
                  <span tw="font-normal text-[24px] text-[#889CAA]">
                    {LABELS["question-summary"]["papers-analyzed"].replace(
                      "{count}",
                      resultsAnalyzedCountSummary.toString()
                    )}
                  </span>
                ) : null}
              </div>
              <div
                style={{
                  overflow: "hidden",
                  display: "-webkit-box",
                  WebkitBoxOrient: "vertical",
                  WebkitLineClamp: 4,
                }}
                tw="text-[28px] text-[#222F2B] leading-[42px] mt-4 h-[170px]"
              >
                {summary || ""}
              </div>
            </div>
          </div>
        </>
      );
    }
    return (
      // eslint-disable-next-line jsx-a11y/alt-text
      <img
        width="1200"
        height="630"
        tw="flex absolute"
        src={ogResults as unknown as string}
      />
    );
  };
  return new ImageResponse(render(), {
    fonts: [
      {
        name: "ProductSans",
        data: fontDataBold,
        style: "normal",
        weight: 700,
      },
      {
        name: "ProductSans",
        data: fontDataRegular,
        style: "normal",
        weight: 400,
      },
    ],
    width: 1200,
    height: 630,
  });
}
