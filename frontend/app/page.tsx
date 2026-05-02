"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import ChatMessage, { Message } from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import Spinner from "@/components/ui/Spinner";
import { queryDocuments } from "@/lib/api";
import { MessageSquare } from "lucide-react";

const MAX_MESSAGES = 10; // 5 Q&A pairs = 10 messages

function generateId(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSubmit = async (question: string) => {
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: question,
    };

    setMessages((prev) => {
      const next = [...prev, userMessage];
      return next.slice(-MAX_MESSAGES);
    });
    setIsLoading(true);

    try {
      const result = await queryDocuments(question);

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: result.answer,
        sources: result.sources,
        model: result.model,
      };

      setMessages((prev) => {
        const next = [...prev, assistantMessage];
        return next.slice(-MAX_MESSAGES);
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to get answer";

      const errorMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${msg}`,
      };
      setMessages((prev) => {
        const next = [...prev, errorMessage];
        return next.slice(-MAX_MESSAGES);
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <h1 className="text-lg font-semibold text-gray-800">Chat</h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Ask questions about your uploaded documents
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-3xl space-y-6">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
              <div className="rounded-full bg-blue-100 p-6">
                <MessageSquare className="h-12 w-12 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-700">
                  Ask anything about your documents
                </h2>
                <p className="mt-1 text-sm text-gray-500">
                  Upload documents on the Documents page, then ask questions here.
                </p>
              </div>
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {[
                  "What is the main topic of the uploaded documents?",
                  "Summarize the key findings.",
                  "What are the most important dates mentioned?",
                  "List any recommendations or conclusions.",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSubmit(suggestion)}
                    className="rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-left text-sm text-gray-600 shadow-sm transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {isLoading && (
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200">
                <Spinner size="sm" />
              </div>
              <div className="rounded-2xl rounded-tl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Spinner size="sm" />
                  Searching documents and generating answer...
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
    </div>
  );
}
