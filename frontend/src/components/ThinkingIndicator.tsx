import { motion } from "framer-motion";
import { Sprout } from "lucide-react";

export function ThinkingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <div className="size-8 rounded-lg bg-primary/10 border border-primary/20 grid place-items-center text-primary shrink-0">
        <Sprout className="size-4" />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface border border-border/60 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2"
      >
        <span className="text-xs text-muted-foreground mr-1">Thinking</span>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="size-1.5 rounded-full bg-primary thinking-dot"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </motion.div>
    </div>
  );
}

export function MessageSkeleton() {
  return (
    <div className="space-y-2 max-w-[85%]">
      <div className="h-3 w-3/4 rounded shimmer" />
      <div className="h-3 w-full rounded shimmer" />
      <div className="h-3 w-1/2 rounded shimmer" />
    </div>
  );
}
