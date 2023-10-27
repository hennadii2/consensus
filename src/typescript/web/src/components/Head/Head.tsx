import {
  META_IMAGE,
  META_IMAGE_ALT,
  META_TWITTER_SITE,
} from "constants/config";
import NextHead from "next/head";
import React, { ReactNode } from "react";

export interface HeadProps {
  title: string;
  schema?: string;
  description?: string;
  type?: "website" | "article";
  image?: string;
  imageAlt?: string;
  url?: string;
  citation?: {
    title: string;
    date?: string;
    year: number;
    journalTitle: string;
    doi: string;
    publicUrl: string;
    abstractHtmlUrl: string;
    abstact: string;
    authors: string;
    firstPage?: string;
    lastPage?: string;
    volume?: string;
  };
}

function Head({
  title,
  schema,
  description,
  type,
  url,
  image,
  imageAlt,
  citation,
}: HeadProps) {
  // open graph tags
  const tagsToRender: ReactNode[] = [];

  if (title) {
    tagsToRender.push(
      <meta key="title" name="title" property="title" content={title} />
    );
    tagsToRender.push(
      <meta
        key="og:title"
        name="og:title"
        property="og:title"
        content={title}
      />
    );
    tagsToRender.push(
      <meta
        key="twitter:title"
        name="twitter:title"
        property="twitter:title"
        content={title}
      />
    );
  }

  if (description) {
    tagsToRender.push(
      <meta
        key="description"
        name="description"
        property="description"
        content={description}
      />
    );
    tagsToRender.push(
      <meta
        key="og:description"
        name="og:description"
        property="og:description"
        content={description}
      />
    );
    tagsToRender.push(
      <meta
        key="twitter:description"
        name="twitter:description"
        property="twitter:description"
        content={description}
      />
    );
  }

  if (type) {
    tagsToRender.push(
      <meta key="og:type" name="og:type" property="og:type" content={type} />
    );
  }

  if (url) {
    tagsToRender.push(
      <meta key="og:url" name="og:url" property="og:url" content={url} />
    );
  }

  // image
  tagsToRender.push(
    <meta
      key="og:image"
      name="og:image"
      property="og:image"
      content={image || META_IMAGE}
    />
  );
  tagsToRender.push(
    <meta
      key="twitter:image"
      name="twitter:image"
      property="twitter:image"
      content={image || META_IMAGE}
    />
  );

  // image alt
  tagsToRender.push(
    <meta
      key="og:image:alt"
      name="og:image:alt"
      property="og:image:alt"
      content={imageAlt || META_IMAGE_ALT}
    />
  );
  tagsToRender.push(
    <meta
      key="twitter:image:alt"
      name="twitter:image:alt"
      property="twitter:image:alt"
      content={imageAlt || META_IMAGE_ALT}
    />
  );

  // card
  tagsToRender.push(
    <meta
      key="twitter:card"
      name="twitter:card"
      property="twitter:card"
      content="summary_large_image"
    />
  );

  // twiiter site
  tagsToRender.push(
    <meta
      key="twitter:site"
      name="twitter:site"
      property="twitter:site"
      content={META_TWITTER_SITE}
    />
  );

  // highwire press
  if (citation) {
    tagsToRender.push(
      <meta
        key="citation_title"
        name="citation_title"
        property="citation_title"
        content={citation.title}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_date"
        name="citation_date"
        property="citation_date"
        content={citation.date || ""}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_year"
        name="citation_year"
        property="citation_year"
        content={citation.year.toString()}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_journal_title"
        name="citation_journal_title"
        property="citation_journal_title"
        content={citation.journalTitle}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_doi"
        name="citation_doi"
        property="citation_doi"
        content={citation.doi}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_public_url"
        name="citation_public_url"
        property="citation_public_url"
        content={citation.publicUrl}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_abstract_html_url"
        name="citation_abstract_html_url"
        property="citation_abstract_html_url"
        content={citation.abstractHtmlUrl}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_fulltext_html_url"
        name="citation_fulltext_html_url"
        property="citation_fulltext_html_url"
        content={`https://doi.org/${citation.doi}`}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_abstract"
        name="citation_abstract"
        property="citation_abstract"
        content={citation.abstact}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_authors"
        name="citation_authors"
        property="citation_authors"
        content={citation.authors}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_firstpage"
        name="citation_firstpage"
        property="citation_firstpage"
        content={citation.firstPage}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_lastpage"
        name="citation_lastpage"
        property="citation_lastpage"
        content={citation.lastPage}
      />
    );
    tagsToRender.push(
      <meta
        key="citation_volume"
        name="citation_volume"
        property="citation_volume"
        content={citation.volume}
      />
    );
  }

  return (
    <NextHead>
      <title data-testid="title">{title}</title>
      {tagsToRender}
      {schema && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: schema,
          }}
        />
      )}
    </NextHead>
  );
}

export default Head;
