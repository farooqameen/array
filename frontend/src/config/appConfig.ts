const isProd =
  process.env.NODE_ENV === "production" ||
  process.env.NODE_ENV === "development";

export const appConfig = {
  API_BASE_URL:
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    (isProd ? "https://dev.jade.array.world/api" : "http://localhost:8000"),

  OPENSEARCH: {
    URL: process.env.NEXT_PUBLIC_OPENSEARCH_URL!,
    USER: process.env.NEXT_PUBLIC_OPENSEARCH_USER!,
    PASS: process.env.NEXT_PUBLIC_OPENSEARCH_PASS!,
    USE_SSL: process.env.NEXT_PUBLIC_OPENSEARCH_USE_SSL === "true",
    VERIFY_CERTS: process.env.NEXT_PUBLIC_OPENSEARCH_VERIFY_CERTS === "true",
  },

  S3: {
    BUCKET_NAME: process.env.NEXT_PUBLIC_S3_BUCKET_NAME!,
    REGION: process.env.NEXT_PUBLIC_APP_AWS_REGION!,
    ACCESS_KEY: process.env.AWS_ACCESS_KEY_ID!, // only for server-side use
    SECRET_KEY: process.env.AWS_SECRET_ACCESS_KEY!, // only for server-side use
    AWS_SESSION_TOKEN: process.env.AWS_SESSION_TOKEN!,
  },

  MAX_FILES: 10,
  MAX_TOTAL_SIZE_MB: 10,
  MAX_TOTAL_SIZE_BYTES: 10 * 1024 * 1024,
};
