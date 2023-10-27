export type ParseSubTextProps = {
  journal?: string;
  citation_count?: number;
  primary_author?: string;
  year?: number;
};

export default function parseSubText(item?: ParseSubTextProps) {
  const extras = [];

  if (item?.journal) {
    extras.push(`Published in ${item.journal}`);
  }

  if (typeof item?.citation_count === "number") {
    extras.push(`Citations: ${item.citation_count}`);
  }

  if (item?.primary_author) {
    extras.push(`${item.primary_author}`);
  }

  if (item?.year) {
    extras.push(item.year);
  }

  return extras.join(" | ");
}
