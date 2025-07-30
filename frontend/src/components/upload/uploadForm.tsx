// src/components/upload/UploadForm.tsx
"use client";

import React, { useState, useCallback, useRef } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { UploadResponse, ErrorResponse } from "@/types";
import { Loader2, UploadCloud, FileText, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { appConfig } from "@/config/appConfig";

const { API_BASE_URL, MAX_FILES, MAX_TOTAL_SIZE_MB, MAX_TOTAL_SIZE_BYTES } =
  appConfig;

export default function UploadForm() {
  const [indexName, setIndexName] = useState<string>("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndAddFiles = useCallback(
    (files: FileList | File[]) => {
      const newFiles: File[] = [];
      let currentTotalSize = selectedFiles.reduce(
        (sum, file) => sum + file.size,
        0
      );

      for (const file of Array.from(files)) {
        if (file.type !== "application/pdf") {
          toast.error(`"${file.name}" is not a PDF.`, {
            description: "Invalid File Type",
          });
          continue;
        }

        if (selectedFiles.length + newFiles.length >= MAX_FILES) {
          toast.error(
            `Cannot add "${file.name}". Maximum of ${MAX_FILES} files allowed.`,
            {
              description: "Too Many Files",
            }
          );
          break;
        }

        if (currentTotalSize + file.size > MAX_TOTAL_SIZE_BYTES) {
          toast.error(`"${file.name}" exceeds total size limit.`, {
            description: `Total size cannot exceed ${MAX_TOTAL_SIZE_MB}MB.`,
          });
          continue;
        }

        newFiles.push(file);
        currentTotalSize += file.size;
      }

      if (newFiles.length > 0) {
        setSelectedFiles((prev) => [...prev, ...newFiles]);
      }
    },
    [selectedFiles]
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      validateAndAddFiles(event.target.files);
      event.target.value = ""; // Allow re-selecting the same file
    }
  };

  const handleRemoveFile = (fileName: string) => {
    setSelectedFiles((prev) => prev.filter((file) => file.name !== fileName));
  };

  const handleDragOver = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragOver(true);
    },
    []
  );

  const handleDragLeave = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragOver(false);
    },
    []
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragOver(false);

      if (event.dataTransfer.files?.length) {
        validateAndAddFiles(event.dataTransfer.files);
        event.dataTransfer.clearData();
      }
    },
    [validateAndAddFiles]
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!indexName.trim()) {
      toast.error("Please provide a name for the index.", {
        description: "Index Name Missing",
      });
      return;
    }

    if (selectedFiles.length === 0) {
      toast.error("Please select at least one PDF file to upload.", {
        description: "No Files Selected",
      });
      return;
    }

    setIsUploading(true);
    const toastId = toast.loading("Starting upload...", {
      description: `Uploading ${selectedFiles.length} file(s).`,
    });

    const formData = new FormData();
    formData.append("index_name", indexName.trim());
    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(`${API_BASE_URL}/search/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(
          errorData.detail ||
            errorData.reason ||
            `HTTP error! status: ${response.status}`
        );
      }

      const successData: UploadResponse = await response.json();

      if (successData.status && successData.results) {
        let successfulUploads = 0;
        let failedUploads = 0;

        successData.results.forEach((fileResult) => {
          if (fileResult.status === "success") {
            successfulUploads++;
            toast.success(`"${fileResult.filename}" indexed successfully.`, {
              description: `Indexed ${fileResult.indexed_chunks || 0} chunks.`,
            });
          } else {
            failedUploads++;
            toast.error(`Failed to index "${fileResult.filename}".`, {
              description: fileResult.reason || "Unknown error.",
              duration: 7000,
            });
          }
        });

        if (failedUploads > 0) {
          toast.dismiss(toastId);
          toast.warning(`${failedUploads} file(s) failed to upload.`, {
            description: "See individual messages for details.",
          });
        }
        if (successfulUploads > 0) {
          toast.dismiss(toastId);
          toast.success(
            `Upload complete: ${successfulUploads} file(s) indexed.`,
            {
              description: `Knowledge base "${indexName}" is ready.`,
            }
          );
        }
      } else {
        toast.success(`Files indexed into "${indexName}".`, {
          id: toastId,
          description: `Successfully indexed ${
            successData.indexed_chunks || 0
          } chunks.`,
        });
      }

      setIndexName("");
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error: any) {
      console.error("Upload Error:", error);
      toast.error(error.message || "An unknown error occurred.", {
        id: toastId,
        description: "Upload Failed",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const totalSelectedSize = selectedFiles.reduce(
    (sum, file) => sum + file.size,
    0
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center text-2xl">
          <UploadCloud className="mr-3 h-7 w-7 text-primary" />
          Create Knowledge Base
        </CardTitle>
        <CardDescription>
          Upload one or more PDF documents to create a new searchable knowledge
          base.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid gap-3">
            <Label htmlFor="indexName">Knowledge Base Name</Label>
            <Input
              id="indexName"
              type="text"
              placeholder="e.g., policy-manual-v2"
              value={indexName}
              onChange={(e) => setIndexName(e.target.value)}
              disabled={isUploading}
              required
            />
          </div>

          <div className="grid gap-3">
            <Label htmlFor="pdfFiles">PDF Documents</Label>
            <div
              className={cn(
                "flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-200 ease-in-out",
                isDragOver
                  ? "border-primary bg-primary/10"
                  : "border-border hover:border-primary/50"
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud className="h-10 w-10 text-muted-foreground mb-3" />
              <p className="text-muted-foreground text-sm mb-2">
                Drag & drop files here, or{" "}
                <span className="font-semibold text-primary">
                  click to browse
                </span>
              </p>
              <p className="text-xs text-muted-foreground">
                Max {MAX_FILES} files, total size up to {MAX_TOTAL_SIZE_MB}MB.
              </p>
              <Input
                id="pdfFiles"
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileChange}
                disabled={isUploading}
                className="hidden"
                ref={fileInputRef}
              />
            </div>
          </div>

          {selectedFiles.length > 0 && (
            <div className="space-y-3">
              <Label>
                Selected Files ({selectedFiles.length}/{MAX_FILES})
              </Label>
              <div
                className="max-h-48 overflow-y-auto pr-2 space-y-2"
                style={{ scrollbarWidth: "thin" }}
              >
                {selectedFiles.map((file) => (
                  <div
                    key={file.name}
                    className="flex items-center justify-between bg-muted p-2 rounded-md text-sm"
                  >
                    <div className="flex items-center overflow-hidden gap-2">
                      <FileText className="h-4 w-4 text-primary flex-shrink-0" />
                      <span className="truncate" title={file.name}>
                        {file.name}
                      </span>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        ({(file.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRemoveFile(file.name)}
                      disabled={isUploading}
                      className="h-6 w-6 text-muted-foreground hover:text-destructive"
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                <div
                  className="bg-primary h-2.5 rounded-full"
                  style={{
                    width: `${
                      (totalSelectedSize / MAX_TOTAL_SIZE_BYTES) * 100
                    }%`,
                  }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground text-right">
                Total: {(totalSelectedSize / (1024 * 1024)).toFixed(2)}MB /{" "}
                {MAX_TOTAL_SIZE_MB}MB
              </p>
            </div>
          )}

          <Button
            type="submit"
            size="lg"
            className="w-full text-base"
            disabled={
              isUploading || selectedFiles.length === 0 || !indexName.trim()
            }
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <UploadCloud className="mr-2 h-5 w-5" />
                Upload & Create
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
