import { motion } from "framer-motion";
import { ExternalLink, FileText } from "lucide-react";
import { Citation } from "@/lib/mockData";

export function CitationBadge({ citation, index }: { citation: Citation; index: number }) {
  return (
    <a
      href={citation.url ?? "#"}
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors"
    >
      <span className="font-mono">[{index + 1}]</span>
      <span className="truncate max-w-[160px]">{citation.title}</span>
    </a>
  );
}

export function CitationsPanel({ citations }: { citations: Citation[] }) {
  if (!citations.length) {
    return (
      <div className="flex-1 grid place-items-center text-center p-6 text-sm text-muted-foreground">
        <div>
          <FileText className="size-8 mx-auto mb-3 opacity-40" />
          Sources cited by the assistant will appear here.
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {citations.map((c, i) => (
        <motion.a
          key={c.id}
          href={c.url ?? "#"}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="block group p-4 rounded-xl surface border border-border/60 hover:border-primary/40 transition-all"
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="size-5 grid place-items-center rounded-md bg-primary/10 text-primary text-[10px] font-mono font-bold">
              {i + 1}
            </span>
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">{c.source}</span>
            <ExternalLink className="ml-auto size-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="font-medium text-sm leading-snug mb-1.5 text-foreground">{c.title}</div>
          <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">{c.excerpt}</p>
        </motion.a>
      ))}
    </div>
  );
}
