"use client";

import { useCallback, useRef, useState } from "react";

import { postUploadFile } from "@/lib/api";

const ACCEPT = ".pdf,.txt,application/pdf,text/plain";

function isAllowedFile(file: File): boolean {
  const ext = file.name.toLowerCase().split(".").pop();
  if (ext === "pdf" || ext === "txt") return true;
  if (file.type === "application/pdf" || file.type === "text/plain") return true;
  return false;
}

function Spinner() {
  return (
    <span
      className="inline-block size-4 shrink-0 animate-spin rounded-full border-2 border-white/30 border-t-white"
      aria-hidden
    />
  );
}

export default function FileUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selected, setSelected] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);

  const resetStatus = useCallback(() => {
    setStatus("idle");
    setErrorMessage(null);
    setDocumentId(null);
  }, []);

  const pickFile = useCallback((file: File | null) => {
    resetStatus();
    if (!file) {
      setSelected(null);
      return;
    }
    if (!isAllowedFile(file)) {
      setSelected(null);
      setStatus("error");
      setErrorMessage("Only PDF and TXT files are allowed.");
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    setSelected(file);
  }, [resetStatus]);

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0] ?? null;
      pickFile(file);
    },
    [pickFile],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const file = e.dataTransfer.files?.[0] ?? null;
      pickFile(file);
    },
    [pickFile],
  );

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const upload = useCallback(async () => {
    if (!selected || status === "loading") return;
    setStatus("loading");
    setErrorMessage(null);
    setDocumentId(null);
    try {
      const data = await postUploadFile(selected);
      setStatus("success");
      setDocumentId(data.document_id);
      setSelected(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Upload failed");
    }
  }, [selected, status]);

  return (
    <div className="mx-auto w-full max-w-lg px-4 py-8">
      <div
        className="rounded-2xl border border-zinc-200/90 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900/80"
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          Upload a document
        </h2>
        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-500">
          PDF or TXT — files are indexed for RAG after upload.
        </p>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            onChange={onInputChange}
            className="hidden"
            id="file-upload-input"
            disabled={status === "loading"}
          />
          <label
            htmlFor="file-upload-input"
            className="inline-flex cursor-pointer items-center justify-center rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm font-medium text-zinc-800 transition hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-700"
          >
            Choose file
          </label>
          <button
            type="button"
            onClick={upload}
            disabled={!selected || status === "loading"}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-emerald-600 dark:hover:bg-emerald-500"
          >
            {status === "loading" && <Spinner />}
            {status === "loading" ? "Uploading…" : "Upload"}
          </button>
        </div>

        <p className="mt-3 min-h-[1.25rem] text-xs text-zinc-600 dark:text-zinc-400">
          {selected ? (
            <span>
              Selected: <span className="font-medium text-zinc-800 dark:text-zinc-200">{selected.name}</span>
            </span>
          ) : (
            <span className="text-zinc-400 dark:text-zinc-600">No file selected</span>
          )}
        </p>

        {status === "success" && (
          <p className="mt-4 rounded-xl border border-emerald-200/80 bg-emerald-50 px-3 py-2 text-sm text-emerald-900 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-200">
            File uploaded successfully
            {documentId && (
              <span className="mt-1 block font-mono text-[11px] text-emerald-800/90 dark:text-emerald-300/90">
                document_id: {documentId}
              </span>
            )}
          </p>
        )}

        {status === "error" && errorMessage && (
          <p
            className="mt-4 rounded-xl border border-red-200/80 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200"
            role="alert"
          >
            {errorMessage}
          </p>
        )}
      </div>
    </div>
  );
}
