import { User, Bot } from "lucide-react";
import SourceCard from "@/components/chat/SourceCard";
import { SourceChunk } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  model?: string;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-blue-600" : "bg-gray-200"
        }`}
      >
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Bot className="h-4 w-4 text-gray-600" />
        )}
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
            isUser
              ? "rounded-tr-sm bg-blue-600 text-white"
              : "rounded-tl-sm bg-white text-gray-800 border border-gray-200"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <p className="mb-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Sources ({message.sources.length})
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              {message.sources.map((source, i) => (
                <SourceCard key={`${source.document_id}-${i}`} source={source} index={i} />
              ))}
            </div>
            {message.model && message.model !== "none" && (
              <p className="mt-1.5 text-right text-xs text-gray-400">
                via {message.model}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
