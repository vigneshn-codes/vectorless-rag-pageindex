import { FileText } from "lucide-react";
import Badge from "@/components/ui/Badge";
import { SourceChunk } from "@/lib/api";

interface SourceCardProps {
  source: SourceChunk;
  index: number;
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const ext = source.filename.split(".").pop()?.toLowerCase() ?? "";

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm">
      <div className="mb-1.5 flex items-center gap-2">
        <FileText className="h-3.5 w-3.5 shrink-0 text-blue-600" />
        <span className="font-medium text-gray-800 truncate max-w-[200px]" title={source.filename}>
          {source.filename}
        </span>
        <Badge variant="info" className="ml-auto shrink-0">
          {ext.toUpperCase()}
        </Badge>
        {source.page_number != null && (
          <Badge variant="default" className="shrink-0">
            p.{source.page_number}
          </Badge>
        )}
      </div>
      <p className="line-clamp-3 text-xs text-gray-600 leading-relaxed">
        {source.snippet}
      </p>
      <div className="mt-1.5 flex items-center justify-between">
        <span className="text-xs text-gray-400">Source {index + 1}</span>
        <span className="text-xs text-gray-400">
          Score: {source.score.toFixed(4)}
        </span>
      </div>
    </div>
  );
}
