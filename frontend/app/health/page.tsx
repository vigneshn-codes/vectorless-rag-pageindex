"use client";

import { useState, useEffect, useCallback } from "react";
import {
  CheckCircle,
  XCircle,
  RefreshCw,
  Database,
  FileText,
  Layers,
  Clock,
  Wifi,
  WifiOff,
} from "lucide-react";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/api";

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getHealth();
      setHealth(result);
      setIsOffline(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to reach API";
      setError(msg);
      setIsOffline(true);
      setHealth(null);
    } finally {
      setIsLoading(false);
      setLastChecked(new Date().toISOString());
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  const isOnline = !isOffline && health != null;
  const isHealthy = isOnline && health.status === "ok";

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-gray-800">Health</h1>
            <p className="text-xs text-gray-500 mt-0.5">
              API and database status
            </p>
          </div>
          <button
            onClick={checkHealth}
            disabled={isLoading}
            className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm transition hover:bg-gray-50 disabled:opacity-50"
          >
            {isLoading ? <Spinner size="sm" /> : <RefreshCw className="h-4 w-4" />}
            Refresh
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* API Status Card */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {isLoading ? (
                  <Spinner size="md" />
                ) : isOnline ? (
                  <Wifi className="h-6 w-6 text-green-500" />
                ) : (
                  <WifiOff className="h-6 w-6 text-red-500" />
                )}
                <div>
                  <p className="font-semibold text-gray-800">API Server</p>
                  <p className="text-xs text-gray-500">
                    {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                  </p>
                </div>
              </div>
              {!isLoading && (
                <Badge variant={isOnline ? (isHealthy ? "success" : "warning") : "error"}>
                  {isOnline ? (isHealthy ? "Online" : "Degraded") : "Offline"}
                </Badge>
              )}
            </div>
          </div>

          {/* DB Status Card */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {isLoading ? (
                  <Spinner size="md" />
                ) : health?.db_connected ? (
                  <CheckCircle className="h-6 w-6 text-green-500" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-500" />
                )}
                <div>
                  <p className="font-semibold text-gray-800">PostgreSQL Database</p>
                  <p className="text-xs text-gray-500">Full-text search via tsvector</p>
                </div>
              </div>
              {!isLoading && (
                <Badge variant={health?.db_connected ? "success" : "error"}>
                  {health?.db_connected ? "Connected" : "Disconnected"}
                </Badge>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-blue-100 p-2.5">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">
                    {isLoading ? (
                      <span className="inline-block h-7 w-12 animate-pulse rounded bg-gray-200" />
                    ) : (
                      (health?.document_count ?? "—").toLocaleString()
                    )}
                  </p>
                  <p className="text-xs text-gray-500">Total Documents</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-purple-100 p-2.5">
                  <Layers className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">
                    {isLoading ? (
                      <span className="inline-block h-7 w-16 animate-pulse rounded bg-gray-200" />
                    ) : (
                      (health?.chunk_count ?? "—").toLocaleString()
                    )}
                  </p>
                  <p className="text-xs text-gray-500">Total Chunks</p>
                </div>
              </div>
            </div>
          </div>

          {/* Last Checked */}
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>
                Last checked:{" "}
                {lastChecked ? (
                  <span className="font-medium text-gray-700">
                    {formatTimestamp(lastChecked)}
                  </span>
                ) : (
                  "Never"
                )}
              </span>
            </div>
            {health?.timestamp && (
              <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
                <Database className="h-3.5 w-3.5" />
                <span>
                  Server time: {formatTimestamp(health.timestamp)}
                </span>
              </div>
            )}
          </div>

          {/* Architecture info */}
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">
              How it works
            </h3>
            <ul className="space-y-1 text-xs text-blue-700">
              <li>Documents are parsed and split into text chunks</li>
              <li>Chunks are indexed with PostgreSQL tsvector (no embeddings)</li>
              <li>Queries use plainto_tsquery + ts_rank for retrieval</li>
              <li>Top 10 chunks are re-ranked by OpenAI to top 5</li>
              <li>GPT-4o-mini generates the final answer with source citations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
