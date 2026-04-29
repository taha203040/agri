import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Image as ImageIcon, ShieldAlert, Leaf, AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { sampleDiagnosis, DiagnosisResult } from "@/lib/mockData";
import { CitationBadge } from "@/components/Citations";
import { cn } from "@/lib/utils";

const severityMap = {
  mild: { label: "Mild", color: "text-success", bg: "bg-success/10 border-success/30", icon: Leaf },
  moderate: { label: "Moderate", color: "text-warning", bg: "bg-warning/10 border-warning/30", icon: ShieldAlert },
  severe: { label: "Severe", color: "text-danger", bg: "bg-danger/10 border-danger/30", icon: AlertTriangle },
};

export function DiseaseDiagnosis() {
  const [image, setImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [progress, setProgress] = useState(0);

  const onUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      setImage(reader.result as string);
      setResult(null);
      runAnalysis();
    };
    reader.readAsDataURL(file);
  };

  const runAnalysis = () => {
    setAnalyzing(true);
    setProgress(0);
    let p = 0;
    const t = setInterval(() => {
      p += Math.random() * 18;
      if (p >= 100) {
        p = 100;
        clearInterval(t);
        setTimeout(() => {
          setAnalyzing(false);
          setResult(sampleDiagnosis);
        }, 250);
      }
      setProgress(Math.min(p, 100));
    }, 180);
  };

  const reset = () => {
    setImage(null);
    setResult(null);
    setAnalyzing(false);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upload zone / image */}
        <div className="surface border border-border/60 rounded-2xl p-6 flex flex-col">
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-4">Plant Sample</div>

          {!image ? (
            <label
              className="flex-1 min-h-[360px] border-2 border-dashed border-border rounded-xl grid place-items-center text-center cursor-pointer hover:border-primary/40 hover:bg-primary/5 transition-colors"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const f = e.dataTransfer.files[0];
                if (f) onUpload(f);
              }}
            >
              <input
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
              />
              <div>
                <div className="size-14 rounded-xl bg-primary/10 grid place-items-center mx-auto mb-4 text-primary">
                  <Upload className="size-6" />
                </div>
                <div className="font-medium mb-1">Drop a leaf photo here</div>
                <div className="text-sm text-muted-foreground">or click to browse · JPG, PNG up to 10MB</div>
              </div>
            </label>
          ) : (
            <div className="relative flex-1 rounded-xl overflow-hidden border border-border/60">
              <img src={image} alt="plant" className="w-full h-full object-cover min-h-[360px]" />
              {analyzing && (
                <div className="absolute inset-0 bg-background/70 backdrop-blur-sm grid place-items-center">
                  <div className="text-center w-2/3">
                    <div className="text-sm font-medium mb-3 text-primary glow-text">Analyzing image…</div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-primary to-secondary"
                        animate={{ width: `${progress}%` }}
                      />
                    </div>
                    <div className="text-[11px] text-muted-foreground mt-2 tabular-nums">{Math.round(progress)}%</div>
                  </div>
                </div>
              )}
              <Button
                size="sm"
                variant="secondary"
                onClick={reset}
                className="absolute top-3 right-3 gap-1.5"
              >
                <RotateCcw className="size-3.5" /> New
              </Button>
            </div>
          )}
        </div>

        {/* Result */}
        <div className="flex flex-col gap-4">
          <AnimatePresence mode="wait">
            {!result && !analyzing && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="surface border border-border/60 rounded-2xl p-8 flex-1 grid place-items-center text-center text-muted-foreground"
              >
                <div>
                  <ImageIcon className="size-10 mx-auto mb-3 opacity-40" />
                  <p>Upload a photo to get an instant disease diagnosis with treatment recommendations.</p>
                </div>
              </motion.div>
            )}

            {analyzing && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="surface border border-border/60 rounded-2xl p-6 space-y-4"
              >
                <div className="h-5 w-1/3 rounded shimmer" />
                <div className="h-3 w-3/4 rounded shimmer" />
                <div className="h-3 w-full rounded shimmer" />
                <div className="h-3 w-2/3 rounded shimmer" />
                <div className="h-24 w-full rounded shimmer" />
              </motion.div>
            )}

            {result && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <DiagnosisCard result={result} />
                <TreatmentCard result={result} />
                <SourcesCard result={result} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function DiagnosisCard({ result }: { result: DiagnosisResult }) {
  const sev = severityMap[result.severity];
  const SevIcon = sev.icon;
  const pct = Math.round(result.confidence * 100);
  return (
    <div className="surface border border-border/60 rounded-2xl p-6">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-1">Diagnosis</div>
          <h3 className="text-2xl font-semibold tracking-tight">{result.disease}</h3>
          <p className="text-sm text-muted-foreground italic">{result.scientificName}</p>
        </div>
        <span className={cn("inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm font-medium", sev.bg, sev.color)}>
          <SevIcon className="size-3.5" /> {sev.label}
        </span>
      </div>

      <p className="text-sm text-muted-foreground leading-relaxed mb-5">{result.description}</p>

      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs text-muted-foreground">Model confidence</span>
          <span className="text-sm font-semibold tabular-nums text-primary glow-text">{pct}%</span>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-primary to-secondary"
          />
        </div>
      </div>
    </div>
  );
}

function TreatmentCard({ result }: { result: DiagnosisResult }) {
  return (
    <div className="surface border border-border/60 rounded-2xl p-6">
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-3">Recommended treatment</div>
      <ul className="space-y-2.5">
        {result.treatments.map((t, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="flex gap-3 text-sm"
          >
            <span className="size-5 shrink-0 rounded-md bg-primary/10 text-primary text-[11px] font-mono font-bold grid place-items-center">
              {i + 1}
            </span>
            <span className="leading-relaxed">{t}</span>
          </motion.li>
        ))}
      </ul>
    </div>
  );
}

function SourcesCard({ result }: { result: DiagnosisResult }) {
  return (
    <div className="surface border border-border/60 rounded-2xl p-6">
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-3">Sources</div>
      <div className="flex flex-wrap gap-2">
        {result.citations.map((c, i) => (
          <CitationBadge key={c.id} citation={c} index={i} />
        ))}
      </div>
    </div>
  );
}
