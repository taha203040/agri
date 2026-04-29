import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Sprout, User } from "lucide-react";
import { ChatMessage } from "@/lib/mockData";
import { CitationBadge } from "./Citations";

export function MessageBubble({ message, streaming }: { message: ChatMessage; streaming?: boolean }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div
        className={`size-8 rounded-lg grid place-items-center shrink-0 border ${
          isUser
            ? "bg-secondary/40 border-secondary/40 text-foreground"
            : "bg-primary/10 border-primary/20 text-primary"
        }`}
      >
        {isUser ? <User className="size-4" /> : <Sprout className="size-4" />}
      </div>

      <div className={`max-w-[78%] flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
        {message.image && (
          <img
            src={message.image}
            alt="uploaded plant"
            className="rounded-xl border border-border/60 max-h-48 object-cover"
          />
        )}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "surface border border-border/60 rounded-tl-sm"
          }`}
        >
          <div className="prose-chat">
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {streaming && (
              <span className="inline-block w-1.5 h-3.5 bg-primary ml-0.5 align-middle animate-pulse" />
            )}
          </div>
        </div>

        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 px-1">
            {message.citations.map((c, i) => (
              <CitationBadge key={c.id} citation={c} index={i} />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
