"use client";

import { useState, useEffect, useCallback } from "react";
import UploadDropzone from "@/components/documents/UploadDropzone";
import DocumentTable from "@/components/documents/DocumentTable";
import { listDocuments } from "@/lib/api";
import type { Document } from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setFetchError(null);
    try {
      const result = await listDocuments();
      setDocuments(result.documents);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load documents";
      setFetchError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <h1 className="text-lg font-semibold text-gray-800">Documents</h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Upload and manage your knowledge base
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-4xl space-y-6">
          {fetchError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              Error loading documents: {fetchError}
            </div>
          )}

          <UploadDropzone onUploaded={fetchDocuments} />

          <DocumentTable
            documents={documents}
            isLoading={isLoading}
            onRefresh={fetchDocuments}
            onDeleted={fetchDocuments}
          />
        </div>
      </div>
    </div>
  );
}
