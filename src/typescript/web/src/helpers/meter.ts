import { YesNoAnswerPercents } from "./api";

export interface MeterSummary {
  answer: "YES" | "NO" | "POSSIBLY" | "MIXED" | "MIXED_YES" | "MIXED_NO";
  percent: number;
}

export function meterSummary(params?: YesNoAnswerPercents): MeterSummary {
  const percent: YesNoAnswerPercents = params || { YES: 0, NO: 0, POSSIBLY: 0 };
  let summary: MeterSummary = {
    answer: "YES",
    percent: percent.YES,
  };

  const items: MeterSummary[] = [];
  Object.keys(percent).forEach((item) => {
    const key = item as keyof YesNoAnswerPercents;
    const value = percent[key];
    if (summary.percent < value) {
      summary.answer = key;
      summary.percent = value;
    }
    items.push({ answer: key, percent: value });
  });

  // duplicate percent
  const filter = items.filter((item) => item.percent === summary.percent);

  const possibly = filter.find((item) => item.answer === "POSSIBLY");
  if (possibly && filter.length === 2) {
    const item = filter.find((item) => item.answer !== "POSSIBLY");
    return {
      answer:
        item?.answer === "YES"
          ? "MIXED_YES"
          : item?.answer === "NO"
          ? "MIXED_NO"
          : "MIXED",
      percent: item?.percent || 0,
    };
  }

  if (filter.length >= 2) {
    return {
      answer: "MIXED",
      percent: summary.percent,
    };
  }

  return summary;
}
