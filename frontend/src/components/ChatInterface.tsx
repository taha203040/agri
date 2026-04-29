import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ImagePlus, Send, Plus, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  ChatMessage,
  ChatThread,
  Citation,
  initialThreads,
  streamResponse,
} from "@/lib/mockData";
import { MessageBubble } from "@/components/MessageBubble";
import { ThinkingIndicator } from "@/components/ThinkingIndicator";
import { CitationsPanel } from "@/components/Citations";

export function ChatInterface() {
  const [threads, setThreads] = useState<ChatThread[]>(initialThreads);
  const [activeId, setActiveId] = useState(initialThreads[0].id);
  const [input, setInput] = useState("");
  const [pendingImage, setPendingImage] = useState<string | null>(null);
  const [thinking, setThinking] = useState(false);
  const [streamingId, setStreamingId] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const active = threads.find((t) => t.id === activeId)!;
  const allCitations: Citation[] = active.messages.flatMap((m) => m.citations ?? []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [active.messages, thinking]);

  const updateActive = (updater: (t: ChatThread) => ChatThread) => {
    setThreads((prev) => prev.map((t) => (t.id === activeId ? updater(t) : t)));
  };

  const handleSend = () => {
    const text = input.trim();
    if (!text && !pendingImage) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text || "What's wrong with this plant?",
      image: pendingImage ?? undefined,
      timestamp: Date.now(),
    };
    const hasImage = !!pendingImage;

    updateActive((t) => ({
      ...t,
      title: t.messages.length === 0 ? text.slice(0, 40) || "Plant diagnosis" : t.title,
      messages: [...t.messages, userMsg],
      updatedAt: Date.now(),
    }));
    setInput("");
    setPendingImage(null);
    setThinking(true);

    setTimeout(() => {
      const assistantId = crypto.randomUUID();
      setStreamingId(assistantId);
      setThinking(false);
      updateActive((t) => ({
        ...t,
        messages: [
          ...t.messages,
          { id: assistantId, role: "assistant", content: "", timestamp: Date.now() },
        ],
      }));

      streamResponse(
        text,
        hasImage,
        (token) => {
          setThreads((prev) =>
            prev.map((t) =>
              t.id !== activeId
                ? t
                : {
                    ...t,
                    messages: t.messages.map((m) =>
                      m.id === assistantId ? { ...m, content: m.content + token } : m,
                    ),
                  },
            ),
          );
        },
        (citations) => {
          setStreamingId(null);
          setThreads((prev) =>
            prev.map((t) =>
              t.id !== activeId
                ? t
                : {
                    ...t,
                    preview: t.messages[t.messages.length - 1]?.content.slice(0, 60) ?? "",
                    messages: t.messages.map((m) =>
                      m.id === assistantId ? { ...m, citations } : m,
                    ),
                  },
            ),
          );
        },
      );
    }, 700);
  };

  const newChat = () => {
    const id = crypto.randomUUID();
    setThreads((prev) => [
      { id, title: "New conversation", preview: "", updatedAt: Date.now(), messages: [] },
      ...prev,
    ]);
    setActiveId(id);
  };

  const onFile = (f: File) => {
    const reader = new FileReader();
    reader.onload = () => setPendingImage(reader.result as string);
    reader.readAsDataURL(f);
  };

  const suggestions = [
    "Diagnose yellow spots on tomato leaves",
    "Best cover crop for clay soil?",
    "How often to fertilize corn?",
  ];

  return (
    <div className="h-[calc(100dvh-4rem)] flex">
      {/* History */}
      <div className="w-64 shrink-0 border-r border-border/60 bg-sidebar/40 flex flex-col">
        <div className="p-4">
          <Button onClick={newChat} className="w-full justify-start gap-2" variant="outline">
            <Plus className="size-4" /> New chat
          </Button>
        </div>
        <div className="px-3 text-[11px] uppercase tracking-wider text-muted-foreground mb-2">
          Recent
        </div>
        <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
          {threads.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveId(t.id)}
              className={cn(
                "w-full text-left px-3 py-2.5 rounded-lg transition-colors text-sm",
                t.id === activeId
                  ? "bg-sidebar-accent text-foreground"
                  : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
              )}
            >
              <div className="font-medium truncate">{t.title}</div>
              <div className="text-[11px] text-muted-foreground truncate mt-0.5">{t.preview || "No messages yet"}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main chat */}
      <div className="flex-1 flex flex-col min-w-0">
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto p-6 space-y-6">
            {active.messages.length === 0 && (
              <div className="pt-12 text-center">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium border border-primary/20 mb-4">
                  <Sparkles className="size-3" /> RAG-powered · 12,400 sources indexed
                </div>
                <h2 className="text-3xl font-semibold tracking-tight glow-text">
                  Ask anything about your crops
                </h2>
                <p className="text-muted-foreground mt-2 mb-8">
                  Upload a photo for instant disease diagnosis, or ask about treatments, soil, irrigation, and more.
                </p>
                <div className="grid sm:grid-cols-3 gap-3">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => setInput(s)}
                      className="text-left p-4 rounded-xl surface border border-border/60 hover:border-primary/40 transition-colors text-sm"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {active.messages.map((m) => (
              <MessageBubble key={m.id} message={m} streaming={m.id === streamingId} />
            ))}

            <AnimatePresence>{thinking && <ThinkingIndicator />}</AnimatePresence>
          </div>
        </div>

        {/* Composer */}
        <div className="border-t border-border/60 bg-background/60 backdrop-blur p-4">
          <div className="max-w-3xl mx-auto">
            {pendingImage && (
              <div className="mb-2 inline-flex items-center gap-2 p-2 pr-3 rounded-lg surface border border-border/60">
                <img src={pendingImage} alt="preview" className="size-12 rounded object-cover" />
                <span className="text-xs text-muted-foreground">Image attached</span>
                <button
                  onClick={() => setPendingImage(null)}
                  className="ml-2 text-muted-foreground hover:text-foreground"
                >
                  <X className="size-4" />
                </button>
              </div>
            )}
            <div className="flex items-end gap-2 surface border border-border/60 rounded-2xl p-2 focus-within:border-primary/40 focus-within:glow-ring transition-all">
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => fileRef.current?.click()}
                className="text-muted-foreground hover:text-primary"
                aria-label="Upload image"
              >
                <ImagePlus className="size-5" />
              </Button>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={1}
                placeholder="Ask about plant health, disease, soil…"
                className="flex-1 bg-transparent outline-none resize-none py-2 text-sm placeholder:text-muted-foreground max-h-32"
              />
              <Button
                onClick={handleSend}
                disabled={(!input.trim() && !pendingImage) || thinking || !!streamingId}
                size="icon"
                className="shrink-0"
              >
                <Send className="size-4" />
              </Button>
            </div>
            <p className="text-[11px] text-muted-foreground text-center mt-2">
              Responses cite peer-reviewed agronomy sources.
            </p>
          </div>
        </div>
      </div>

      {/* Citations panel */}
      <div className="w-80 shrink-0 border-l border-border/60 bg-sidebar/40 hidden lg:flex flex-col">
        <div className="p-4 border-b border-border/60">
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Sources</div>
          <div className="text-sm font-semibold mt-0.5">{allCitations.length} citations</div>
        </div>
        <CitationsPanel citations={allCitations} />
      </div>
    </div>
  );
}
