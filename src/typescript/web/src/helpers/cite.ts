export interface ICiteParams {
  authors?: string[];
  author: string;
  title: string;
  journal: string;
  year: number;
  doi?: string;
  volume?: string;
  pages?: string;
  issue?: string;
}

export interface ICite {
  mla: string;
  apa: string;
  chicago: string;
  bibtex: string;
  harvard: string;
}

interface IExtractCitationPage {
  firstPage: string;
  lastPage: string;
}

function formatCitationNameApa(names: string[]): string {
  let citationName = "";

  for (let i = 0; i < names.length; i++) {
    const name = names[i].split(" ");
    let firstName = name[0]?.[0] ? `${name[0][0]}.` : "";
    let lastName = "";

    if (name.length > 1) {
      lastName = name[name.length - 1];
    }

    if (i === 0) {
      citationName += lastName + ", " + firstName;
    } else if (i === names.length - 1) {
      citationName += ", & " + lastName + ", " + firstName;
    } else {
      citationName += ", " + lastName + ", " + firstName;
    }
  }

  return citationName;
}

function formatCitationNameChicago(names: string[]): string {
  let citationName = "";

  for (let i = 0; i < names.length; i++) {
    if (i === 0) {
      citationName += names[i];
    } else if (i === names.length - 1) {
      citationName += " and " + names[i];
    } else {
      citationName += ", " + names[i];
    }
  }

  return citationName;
}

function formatCitationNameBibtex(names: string[]): string {
  let citationName = "";

  for (let i = 0; i < names.length; i++) {
    if (i === 0) {
      citationName += names[i];
    } else {
      citationName += " and " + names[i];
    }
  }

  return citationName;
}

export function getCite(params: ICiteParams): ICite {
  const splitName = params.author.split(" ");
  const firstInitial = splitName[0][0];
  const lastName = splitName[splitName.length - 1];
  const splitTitle = params.title.split(" ");
  const firstWordTitle = splitTitle[0];
  const doi = params.doi || "";
  const doiUrl = doi ? `https://doi.org/${doi}` : "";
  const doiLink = doiUrl
    ? ` <a style='color: rgb(8 83 148 / 1);' href='${doiUrl}' target='_blank'>${doiUrl}</a>.`
    : "";

  const apaAuthorName = params?.authors
    ? formatCitationNameApa(params.authors)
    : `${lastName}, ${firstInitial}.`;
  const chicagoAuthorName = params?.authors
    ? formatCitationNameChicago(params.authors)
    : params.author;
  const bibtexAuthorName = params?.authors
    ? formatCitationNameBibtex(params.authors)
    : params.author;

  const mla = `${params.author} et al. "${params.title}." <em>${
    params.journal
  }</em>${
    params.volume
      ? `, ${params.volume}${params.issue ? `.${params.issue}` : ""}`
      : ""
  } (${params.year})${params.pages ? `: ${params.pages}` : ""}.${doiLink}`;

  const apa = `${apaAuthorName} (${params.year}). ${params.title}. <em>${
    params.journal
  }</em>${
    params.volume
      ? `, ${params.volume}${params.issue ? `(${params.issue})` : ""}`
      : ""
  }${params.pages ? `, ${params.pages}` : ""}.${doiLink}`;

  const chicago = `${chicagoAuthorName}. "${params.title}." <em>${
    params.journal
  }</em>${
    params.volume
      ? `, ${params.volume}${params.issue ? `, no. ${params.issue}` : ""}`
      : ""
  } (${params.year})${params.pages ? `: ${params.pages}` : ""}.${doiLink}`;

  const harvard = `${apaAuthorName}, ${params.year}. ${params.title}. <em>${
    params.journal
  }</em>${
    params.volume
      ? `, ${params.volume}${params.issue ? `(${params.issue})` : ""}`
      : ""
  }${params.pages ? `, pp. ${params.pages}` : ""}.${doiLink}`;

  const bibtex = `@article{${lastName}${
    params.year
  }${firstWordTitle},<br/>title={${
    params.title
  }},<br/>author={${bibtexAuthorName}},${
    params.journal ? `<br/>journal={${params.journal}},` : ""
  }<br/>year={${params.year}},${
    params.volume ? `<br/>volume={${params.volume}},` : ""
  }${params.issue ? `<br/>number={${params.issue}},` : ""}${
    params.pages ? `<br/>pages={${params.pages}},` : ""
  }<br/>doi={${doi}}<br/>}`;

  return {
    mla,
    apa,
    chicago,
    bibtex,
    harvard,
  };
}

/**
 * @function extractCitationPage
 * @description To get the firstPage and lastPage from the pages, the format should include a "-". For example, "10-12p".
 * @example
 * extractCitationPage("10-12p")
 */
export function extractCitationPage(pages?: string): IExtractCitationPage {
  let firstPage = "";
  let lastPage = "";
  if (pages?.includes("-")) {
    const splitPages = pages.split("-");
    if (splitPages.length > 1) {
      firstPage = splitPages[0].replace(/\D/g, "");
      lastPage = splitPages[1].replace(/\D/g, "");
    }
  }
  return {
    firstPage,
    lastPage,
  };
}
