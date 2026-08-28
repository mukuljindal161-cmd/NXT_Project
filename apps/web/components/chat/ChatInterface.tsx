"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  Conversation,
  Message,
  Citation,
  api
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { SourceCard } from "./SourceCard";
import { SuggestedQuestions } from "./SuggestedQuestions";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import {
  Send,
  Plus,
  Trash2,
  GraduationCap,
  Sparkles,
  Bot,
  User,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  Search,
  ArrowLeft,
  ShieldCheck,
  LogOut,
  RefreshCw,
  Menu,
  X
} from "lucide-react";

interface ChatInterfaceProps {
  initialConversationId?: string;
}

export function ChatInterface({ initialConversationId }: ChatInterfaceProps) {
  const router = useRouter();
  const { user, logout } = useAuth();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState<string | undefined>(initialConversationId);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [searchFilter, setSearchFilter] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [streamingCitations, setStreamingCitations] = useState<Citation[]>([]);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (currentConvId) {
      loadMessages(currentConvId);
    } else {
      setMessages([]);
    }
  }, [currentConvId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, statusMessage]);

  const loadConversations = async () => {
    try {
      const list = await api.listConversations();
      setConversations(list);
    } catch {}
  };

  const loadMessages = async (convId: string) => {
    try {
      const conv = await api.getConversation(convId);
      setMessages(conv.messages || []);
    } catch {}
  };

  const handleNewChat = async () => {
    try {
      const newConv = await api.createConversation("New Conversation");
      setConversations([newConv, ...conversations]);
      setCurrentConvId(newConv.id);
      setSidebarOpen(false);
      router.push(`/chat/${newConv.id}`);
    } catch {}
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (currentConvId === id) {
        const nextId = remaining.length > 0 ? remaining[0].id : undefined;
        setCurrentConvId(nextId);
        if (nextId) router.push(`/chat/${nextId}`);
        else router.push("/chat");
      }
    } catch {}
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isStreaming) return;

    setInputQuery("");
    let convId = currentConvId;

    if (!convId) {
      try {
        const newConv = await api.createConversation(query.slice(0, 30));
        setConversations([newConv, ...conversations]);
        convId = newConv.id;
        setCurrentConvId(convId);
        window.history.pushState({}, "", `/chat/${convId}`);
      } catch {
        return;
      }
    }

    const tempUserMsg: Message = {
      id: "temp-user-" + Date.now(),
      conversation_id: convId,
      role: "user",
      content: query,
      status: "COMPLETED",
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsStreaming(true);
    setStreamingText("");
    setStreamingCitations([]);
    setStatusMessage("Searching official college documents...");

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
      const streamUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/conversations/${convId}/messages/stream?content=${encodeURIComponent(query)}`;
      
      const response = await fetch(streamUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok || !response.body) {
        throw new Error("Failed to stream answer");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";
      let capturedCitations: Citation[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/^event:\s*(.+)$/m);
          const dataMatch = block.match(/^data:\s*(.+)$/m);

          const eventType = eventMatch ? eventMatch[1].trim() : "";
          const data = dataMatch ? JSON.parse(dataMatch[1].trim()) : {};

          if (eventType === "retrieval.started") {
            setStatusMessage("Querying pgvector for relevant knowledge...");
          } else if (eventType === "retrieval.completed") {
            if (data.chunks && data.chunks.length > 0) {
              capturedCitations = data.chunks.map((c: any, idx: number) => ({
                document_id: c.document_id,
                document_name: c.document_name,
                chunk_id: c.chunk_id,
                page_number: c.page,
                similarity_score: c.similarity,
                citation_order: idx + 1,
              }));
              setStreamingCitations(capturedCitations);
            }
            setStatusMessage("Validating evidence & grounding response...");
          } else if (eventType === "generation.started") {
            setStatusMessage(null);
          } else if (eventType === "generation.delta") {
            accumulatedText += data.text || "";
            setStreamingText(accumulatedText);
          } else if (eventType === "generation.completed") {
            accumulatedText = data.answer || accumulatedText;
            setStreamingText(accumulatedText);
          } else if (eventType === "citations.completed") {
            if (data.citations) {
              setStreamingCitations(data.citations);
            }
          }
        }
      }

      const assistantMsg: Message = {
        id: "msg-" + Date.now(),
        conversation_id: convId,
        role: "assistant",
        content: accumulatedText,
        status: "COMPLETED",
        created_at: new Date().toISOString(),
        citations: capturedCitations,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setStreamingText("");
      setStreamingCitations([]);
      setStatusMessage(null);
      loadConversations();
    } catch (err) {
      try {
        const reply = await api.sendMessage(convId, query);
        setMessages((prev) => [...prev, reply]);
      } catch (e: any) {
        const errorMsg: Message = {
          id: "error-" + Date.now(),
          conversation_id: convId,
          role: "assistant",
          content: "Sorry, an error occurred while generating the grounded response. Please try again.",
          status: "FAILED",
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } finally {
      setIsStreaming(false);
      setStreamingText("");
      setStatusMessage(null);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedback = async (messageId: string, rating: "positive" | "negative") => {
    try {
      await api.submitFeedback(messageId, rating);
    } catch {}
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-950 overflow-hidden transition-colors relative">
      {/* Mobile Backdrop Overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-slate-900/60 backdrop-blur-xs md:hidden"
        />
      )}

      {/* Sidebar (Desktop persistent, Mobile slide-over drawer) */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 sm:w-80 border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 flex flex-col shrink-0 transition-transform duration-300 ease-in-out md:static md:translate-x-0 ${
          sidebarOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm shrink-0">
              <GraduationCap className="h-4 w-4" />
            </div>
            <span className="font-bold text-sm text-slate-900 dark:text-white tracking-tight">College Assistant</span>
          </Link>
          <div className="flex items-center gap-1">
            <ThemeToggle />
            <button
              onClick={handleNewChat}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white transition-colors"
              title="New Chat"
            >
              <Plus className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSidebarOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="p-3">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200 dark:placeholder:text-slate-600"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          {filteredConversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-400 dark:text-slate-600">No conversations found</div>
          ) : (
            filteredConversations.map((c) => {
              const isSelected = c.id === currentConvId;
              return (
                <div
                  key={c.id}
                  onClick={() => {
                    setCurrentConvId(c.id);
                    setSidebarOpen(false);
                    router.push(`/chat/${c.id}`);
                  }}
                  className={`group flex items-center justify-between rounded-xl px-3 py-2.5 text-xs font-medium cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-blue-50 text-blue-900 font-semibold dark:bg-blue-950/50 dark:text-blue-200"
                      : "text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <span className="truncate pr-2">{c.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 dark:text-slate-500 dark:hover:text-rose-400 p-1 transition-opacity"
                    title="Delete Conversation"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* User Footer */}
        <div className="p-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/50">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="h-7 w-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300 shrink-0">
              {user?.full_name ? user.full_name[0].toUpperCase() : "U"}
            </div>
            <div className="flex flex-col truncate">
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                {user?.full_name || user?.email || "Student"}
              </span>
              <span className="text-[10px] text-slate-400 dark:text-slate-500 capitalize">{user?.role || "student"}</span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {user?.role === "admin" && (
              <button
                onClick={() => router.push("/admin")}
                className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
                title="Admin Console"
              >
                <ShieldCheck className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              </button>
            )}
            <button
              onClick={() => logout()}
              className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-950/30 transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full bg-white dark:bg-slate-950 relative transition-colors overflow-hidden">
        {/* Mobile Header Bar */}
        <div className="flex md:hidden items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
              aria-label="Open sidebar"
            >
              <Menu className="h-5 w-5" />
            </button>
            <span className="font-bold text-sm text-slate-900 dark:text-white">
              {conversations.find((c) => c.id === currentConvId)?.title || "College Assistant"}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
          {messages.length === 0 && !isStreaming ? (
            <SuggestedQuestions onSelect={(q) => handleSendMessage(q)} />
          ) : (
            messages.map((msg) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id}
                  className={`flex gap-2 sm:gap-3.5 max-w-3xl mx-auto ${
                    isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  {!isUser && (
                    <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                      <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                    </div>
                  )}

                  <div className={`flex flex-col max-w-[90%] sm:max-w-[85%] ${isUser ? "items-end" : "items-start"}`}>
                    <div
                      className={`rounded-2xl px-3.5 py-2.5 sm:px-4 sm:py-3 text-xs sm:text-sm leading-relaxed ${
                        isUser
                          ? "bg-blue-600 text-white shadow-sm"
                          : "bg-slate-50 text-slate-900 border border-slate-200/80 shadow-2xs dark:bg-slate-900 dark:text-slate-100 dark:border-slate-800"
                      }`}
                    >
                      {isUser ? (
                        <p>{msg.content}</p>
                      ) : (
                        <div className="prose prose-xs sm:prose-sm max-w-none text-slate-900 dark:text-slate-100 prose-headings:font-bold prose-headings:text-slate-900 dark:prose-headings:text-slate-100 prose-a:text-blue-600 dark:prose-a:text-blue-400">
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                      )}
                    </div>

                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div className="w-full">
                        <SourceCard citations={msg.citations} />
                      </div>
                    )}

                    {!isUser && (
                      <div className="mt-1 flex items-center gap-2 text-slate-400 dark:text-slate-500 text-xs">
                        <button
                          onClick={() => handleCopy(msg.content, msg.id)}
                          className="hover:text-slate-600 dark:hover:text-slate-300 p-1 flex items-center gap-1 transition-colors"
                          title="Copy Answer"
                        >
                          {copiedId === msg.id ? (
                            <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, "positive")}
                          className="hover:text-emerald-600 dark:hover:text-emerald-400 p-1 transition-colors"
                          title="Helpful Answer"
                        >
                          <ThumbsUp className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, "negative")}
                          className="hover:text-rose-600 dark:hover:text-rose-400 p-1 transition-colors"
                          title="Not Helpful"
                        >
                          <ThumbsDown className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-xl bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300 flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs">
                      {user?.full_name ? user.full_name[0].toUpperCase() : "U"}
                    </div>
                  )}
                </div>
              );
            })
          )}

          {/* Streaming Bubble */}
          {isStreaming && (
            <div className="flex gap-2 sm:gap-3.5 max-w-3xl mx-auto justify-start">
              <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5 animate-pulse">
                <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              </div>
              <div className="flex flex-col max-w-[90%] sm:max-w-[85%] items-start">
                {statusMessage && (
                  <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-blue-50 dark:bg-blue-950/60 px-3 py-1 text-xs font-medium text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-900">
                    <RefreshCw className="h-3 w-3 animate-spin" />
                    <span>{statusMessage}</span>
                  </div>
                )}
                {streamingText && (
                  <div className="rounded-2xl px-3.5 py-2.5 sm:px-4 sm:py-3 text-xs sm:text-sm bg-slate-50 text-slate-900 border border-slate-200/80 shadow-2xs dark:bg-slate-900 dark:text-slate-100 dark:border-slate-800">
                    <div className="prose prose-xs sm:prose-sm max-w-none text-slate-900 dark:text-slate-100">
                      <ReactMarkdown>{streamingText}</ReactMarkdown>
                    </div>
                  </div>
                )}
                {streamingCitations.length > 0 && (
                  <div className="w-full">
                    <SourceCard citations={streamingCitations} />
                  </div>
                )}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-2 sm:p-4 border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 transition-colors shrink-0">
          <div className="max-w-3xl mx-auto flex items-center gap-1.5 sm:gap-2 bg-slate-50 dark:bg-slate-950 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-1.5 sm:p-2 shadow-sm focus-within:border-blue-600 focus-within:bg-white dark:focus-within:bg-slate-950 focus-within:ring-2 focus-within:ring-blue-600/20 transition-all">
            <input
              type="text"
              placeholder="Ask a question about fees, courses, exams, library..."
              value={inputQuery}
              disabled={isStreaming}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              className="flex-1 bg-transparent px-2.5 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputQuery.trim() || isStreaming}
              className="h-8 w-8 sm:h-10 sm:w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-40 transition-all shrink-0"
              aria-label="Send message"
            >
              <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
            </button>
          </div>
          <p className="mt-1.5 sm:mt-2 text-center text-[10px] sm:text-[11px] text-slate-400 dark:text-slate-500">
            Answers are strictly grounded in official college records with page citations.
          </p>
        </div>
      </main>
    </div>
  );
}
