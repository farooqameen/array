// types/index.ts

export interface SuccessfulUploadResult {
  status: "success";
  filename: string;
  indexed_chunks?: number;
}

export interface FailedUploadResult {
  status: "error";
  filename: string;
  reason?: string;
}

export interface UploadResponse {
  status: "success" | "partial_success";
  results?: (SuccessfulUploadResult | FailedUploadResult)[];
  indexed_chunks?: number; // Fallback for single file responses
}

export interface ErrorResponse {
  detail?: string;
  reason?: string;
}