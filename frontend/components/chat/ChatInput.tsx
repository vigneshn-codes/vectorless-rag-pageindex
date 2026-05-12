"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import Spinner from "@/components/ui/Spinner";

interface ChatInputProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export default function ChatInput({
  onSubmit,
  isLoading,
  disabled = false,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;
    onSubmit(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
  }, [input]);

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      <div className="mx-auto flex max-w-3xl items-end gap-3">
        <div className="flex-1 rounded-xl border border-gray-300 bg-gray-50 px-4 py-2.5 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents… (Enter to send)"
            className="block w-full resize-none bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none"
            rows={1}
            disabled={isLoading || disabled}
          />
        </div>
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading || disabled}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Send message"
        >
          {isLoading ? (
            <Spinner size="sm" className="border-white border-t-blue-200" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>
      <p className="mt-1.5 text-center text-xs text-gray-400">
        Shift+Enter for new line
      </p>
    </div>
  );
}
