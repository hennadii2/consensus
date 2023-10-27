import { IDetailItem } from "components/DetailContent/DetailContent";

const WEBSITE_URL = process.env.NEXT_PUBLIC_WEBSITE_URL;

export function claimDetailSchema(item?: IDetailItem | null) {
  const graph: any = [];
  const types = ["ScholarlyArticle", "Article"];

  if (!item) {
    return JSON.stringify({
      "@context": "http://schema.org",
      "@graph": graph,
    });
  }

  const slug = encodeURIComponent(item.claim!.url_slug);
  const url = `${WEBSITE_URL}/details/${slug}/${item.claim!.id}`;

  types.forEach((type) => {
    graph.push({
      "@type": type,
      name: item.paper.title,
      headline: item.paper.title,
      mainEntityOfPage: `/details/${slug}/${item.claim!.id}`,
      mainEntity: {
        "@type": "Thing",
        name: `https://doi.org/${item.paper.doi}`,
      },
      about: {
        "@type": "DigitalDocument",
        url: item.paper.provider_url,
      },
      description: item.paper.abstract,
      author: item.paper.authors.map((author) => ({
        "@type": "Person",
        name: author,
      })),
      publication: item.paper.journal.title,
      isPartOf: item.paper.journal.title,
      publisher: {
        "@type": "Organization",
        name: item.paper.journal.title,
      },
      copyrightYear: item.paper.year,
      datePublished: item.paper.publish_date,
      abstract: item.paper.abstract,
      identifier: item.paper.doi ? `https://doi.org/${item.paper.doi}` : "",
      url: url,
      sameAs: `https://doi.org/${item.paper.doi}`,
      alternateName: item.paper.abstract_takeaway,
      disambiguatingDescription: item.paper.abstract_takeaway,
    });
  });

  return JSON.stringify({
    "@context": "http://schema.org",
    "@graph": graph,
  });
}

export function paperDetailSchema(item?: IDetailItem | null) {
  const graph: any = [];
  const types = ["ScholarlyArticle", "Article"];

  if (!item) {
    return JSON.stringify({
      "@context": "http://schema.org",
      "@graph": graph,
    });
  }

  const slug = encodeURIComponent(item.paper!.url_slug!);
  const url = `${WEBSITE_URL}/papers/${slug}/${item.paper.id}`;

  types.forEach((type) => {
    graph.push({
      "@type": type,
      name: item.paper.title,
      headline: item.paper.title,
      mainEntityOfPage: `/papers/${slug}/${item.paper.id}`,
      mainEntity: {
        "@type": "Thing",
        name: `https://doi.org/${item.paper.doi}`,
      },
      about: {
        "@type": "DigitalDocument",
        url: item.paper.provider_url,
      },
      description: item.paper.abstract,
      author: item.paper.authors.map((author) => ({
        "@type": "Person",
        name: author,
      })),
      publication: item.paper.journal.title,
      isPartOf: item.paper.journal.title,
      publisher: {
        "@type": "Organization",
        name: item.paper.journal.title,
      },
      copyrightYear: item.paper.year,
      datePublished: item.paper.publish_date,
      abstract: item.paper.abstract,
      identifier: item.paper.doi ? `https://doi.org/${item.paper.doi}` : "",
      url: url,
      sameAs: `https://doi.org/${item.paper.doi}`,
      alternateName: item.paper.abstract_takeaway,
      disambiguatingDescription: item.paper.abstract_takeaway,
    });
  });

  return JSON.stringify({
    "@context": "http://schema.org",
    "@graph": graph,
  });
}
