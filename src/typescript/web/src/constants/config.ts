export const PER_PAGE = 10;

// env
export const WEB_URL = process.env.NEXT_PUBLIC_WEBSITE_URL;
export const IS_PRODUCTION_ENV = process.env.DEPLOYMENT_ENV === "production";
export const MIXPANEL_PROXY_API_HOST = "https://track.consensus.app";

// urls
export const TWITTER = "https://twitter.com/ConsensusNLP";
export const SUPPORT_EMAIL = "support@consensus.app";
export const SALES_EMAIL = "sales@consensus.app";
export const STUDENT_EMAIL = "student@consensus.app";
export const INSTAGRAM = "https://www.instagram.com/consensusnlp/";
export const LINKEDIN = "https://www.linkedin.com/company/consensus-nlp/";
export const CRUNCHBASE =
  "https://www.crunchbase.com/organization/consensus-c075";
export const WAITLIST_URL = "/#form";
export const LEARN_SEARCH_URL =
  "https://consensus.app/home/blog/maximize-your-consensus-experience-with-these-best-practices/";
export const WEB_URL_BLOG = WEB_URL + "/home/blog/";
export const WEB_URL_CONSENSUS_METER = WEB_URL + "/home/blog/consensus-meter";
export const SUMMARY_TOOL_TIP =
  "https://consensus.app/home/blog/introducing-gpt-4-powered-scientific-summaries/";
export const CAREERS_URL = "https://angel.co/l/2ychKe";
export const SLACK =
  "https://join.slack.com/t/consensus-users/shared_invite/zt-1tg3477h1-bpwm_wSAvfcX6O8dd1b5Iw";
export const TRY_SEARCH_URL =
  WEB_URL +
  "/results/?q=Does remote patient monitoring improve outcomes?&synthesize=on";
export const HIERARCHY_OF_EVIDENCE_URL =
  "https://en.wikipedia.org/wiki/Hierarchy_of_evidence";

// keys
export const GLEAP_API_KEY = process.env.NEXT_PUBLIC_GLEAP_API_KEY;
export const MIXPANEL_API_KEY = process.env.NEXT_PUBLIC_MIXPANEL_API_KEY;
export const INTERCOM_APP_ID = process.env.NEXT_PUBLIC_INTERCOM_APP_ID;
export const INTERCOM_API_BASE = process.env.NEXT_PUBLIC_INTERCOM_API_BASE;
export const INTERCOM_API_IDENTITY_VERIFICATION_SECRET =
  process.env.NEXT_PUBLIC_INTERCOM_API_IDENTITY_VERIFICATION_SECRET;

// meta
export const META_IMAGE = WEB_URL + "/images/consensus-card.png";
export const META_IMAGE_ALT = "An image of the Consensus logo";
export const META_TWITTER_SITE = "@ConsensusNLP";
export const META_SEARCH_IMAGE = WEB_URL + "/images/og-search.png";
export const META_RESULTS_IMAGE = WEB_URL + "/images/og-results.png";
export const META_RESULTS_DYNAMIC_IMAGE = "/api/og_results";
export const META_DETAILS_IMAGE = WEB_URL + "/images/og-details.png";
export const META_PRICING_IMAGE = WEB_URL + "/images/og-pricing.png";

export const MAX_MOBILE_WIDTH = 800;
export const SEARCH_ITEM = "search";
export const MAX_VISIBLE_AUTHORS = 3;
export const MAX_CREDIT_NUM = 20;
export const MAX_CREDIT_LIMIT_DAYS = 30;
export const CLERK_META_KEY_STRIPE_CUSTOMER_ID = "stripeCustomerId";
export const CLERK_META_KEY_CREDIT_USE_NUM = "credit_use_num";
export const CLERK_META_KEY_CREATED_DATE = "created_date";
export const CLERK_META_KEY_USED_SYNTHESIZED_QUERIES =
  "used_synthesized_queries";
export const CLERK_META_KEY_USED_STUDY_PAPER_IDS = "used_study_paper_ids";

// Stripe Meta Data
export const STRIPE_PRICE_METADATA_TYPE_PREMIUM = "premium";
export const STRIPE_PRICE_METADATA_TYPE_LIFETIME = "lifetime";
export const STRIPE_PRICE_METADATA_TYPE_EARLY_BIRD = "early bird";

export const ALLOWED_ORG_DOMAINS_AND_FULL_ORG_NAME: { [key: string]: string } =
  {
    "consensus.app": "Consensus App",
  };

// Student Discount
export const STUDENT_EMAIL_DOMAINS = ["edu", "ac"];
export const STUDENT_DISCOUNT_1_YEAR = "wjkc1OXY";
export const STUDENT_DISCOUNT_2_YEAR = "1GINMYoW";
export const STUDENT_DISCOUNT_3_YEAR = "VwIlgtN0";
export const STUDENT_DISCOUNT_4_YEAR = "gjKtbhze";
export const STUDENT_DISCOUNT_1_YEAR_PERCENT = 40;
export const STUDENT_DISCOUNT_2_YEAR_PERCENT = 40;
export const STUDENT_DISCOUNT_3_YEAR_PERCENT = 40;
export const STUDENT_DISCOUNT_4_YEAR_PERCENT = 40;

// Mailchimp
export const MAILCHIMP_TAG = "Product_Activation";

// Bookmark
export const BOOKMARK_LISTNAME_FAVORITE = "My favorites";
export const BOOKMARK_LISTNAME_MAX_LENGTH = 100;
export const BOOKMARK_MAX_CUSTOM_LIST_NUM = 1;
export const BOOKMARK_MAX_ITEM_NUM = 10;

export const PRIVACY_PAGE_URL = "https://consensus.app/home/privacy-policy/";
export const TERMS_PAGE_URL =
  "https://consensus.app/home/blog/terms-of-service/";
export const EXAMPLE_QUERY_IN_METER =
  "Does beta alanine improve exercise performance?";
