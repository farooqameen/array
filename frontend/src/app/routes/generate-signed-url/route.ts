import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { NextRequest, NextResponse } from "next/server";
import { appConfig } from "@/config/appConfig";

const s3 = new S3Client({
  region: appConfig.S3.REGION,
  // Adding the credentials to s3 client
  credentials: {
    accessKeyId: appConfig.S3.ACCESS_KEY,
    secretAccessKey: appConfig.S3.SECRET_KEY,
    sessionToken: appConfig.S3.AWS_SESSION_TOKEN,
  },
});

export async function POST(req: NextRequest) {
  try {
    const { key, page } = await req.json();

    if (!key) {
      return NextResponse.json({ error: "Missing key" }, { status: 400 });
    }

    // Decode the key
    const decodedKey = decodeURIComponent(key);

    // Create the S3 command
    const command = new GetObjectCommand({
      Bucket: appConfig.S3.BUCKET_NAME,
      Key: decodedKey,
      ResponseContentDisposition: "inline",
      ResponseContentType: "application/pdf",
    });
    
    // Generate the signed URL (expires after 5 minutes)
    const signedUrl = await getSignedUrl(s3, command, {
      expiresIn: 60 * 5,
    });

    return NextResponse.json({
      url: page && page > 0 ? `${signedUrl}#page=${page}` : signedUrl,
    });
  } catch (err) {
    console.error("Signed URL error:", err);
    return NextResponse.json(
      { error: "Failed to generate URL" },
      { status: 500 }
    );
  }
}
