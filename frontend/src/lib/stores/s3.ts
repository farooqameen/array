/**
 * Converts an S3 URI to a public HTTPS URL for an S3 object.
 * Appends a page number fragment for PDFs.
 * @param s3Link The S3 URI (e.g., s3://bucket-name/path/to/file.pdf)
 * @param pageNumber The page number to open the PDF to.
 * @returns A public HTTPS URL.
 */
export async function convertS3ToHttps(
  s3Link: string,
  pageNumber: number | null
) {
  if (!s3Link || !s3Link.startsWith("s3://")) return null;

  try {
    const url = new URL(s3Link);
    const key = url.pathname.substring(1);

    const res = await fetch("/routes/generate-signed-url", {
      method: "POST",
      body: JSON.stringify({ key, page: pageNumber }),
      headers: { "Content-Type": "application/json" },
    });

    const data = await res.json();
    return data.url || null;
  } catch (error) {
    console.error("Failed to fetch signed URL:", error);
    return null;
  }
}
