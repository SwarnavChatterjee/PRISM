import { useState, useMemo, useEffect, useRef } from "react";
import type { Analysis, Finding, Page } from "./types";
import {
  analyzeConfiguration,
  trainMapping,
  exportAnalysisJson,
  SCHEMA_OPTIONS,
} from "./api";
import {
  SAMPLE_CISCO_CONFIG,
  SAMPLE_JUNIPER_CONFIG,
  createSampleFile,
} from "./sampleData";
import {
  ShieldCheck, AlertTriangle, FileCode2, Sparkles,
  ChevronDown, ChevronRight, Loader2, Check, Copy,
  Download, Server, Upload, RefreshCw, X, Activity,
  Layers, Terminal, ArrowRight, BarChart3,
} from "lucide-react";

/* ============================================================
   Top Navigation
   ============================================================ */
type NavItem = { id: Page; label: string; icon: React.ReactNode };

const NAV_ITEMS: NavItem[] = [
  { id: "overview",  label: "Overview",        icon: <BarChart3 size={14} /> },
  { id: "analysis",  label: "Configurations",  icon: <FileCode2 size={14} /> },
  { id: "results",   label: "Compliance",       icon: <ShieldCheck size={14} /> },
  { id: "findings",  label: "Findings",         icon: <AlertTriangle size={14} /> },
  { id: "training",  label: "Training",         icon: <Sparkles size={14} /> },
  { id: "devices",   label: "Devices",          icon: <Server size={14} /> },
];

function TopNav({
  page,
  setPage,
  score,
  activeFile,
  busy,
  failedCount,
}: {
  page: Page;
  setPage: (p: Page) => void;
  score: number;
  activeFile?: string;
  busy: boolean;
  failedCount: number;
}) {
  return (
    <nav className="topnav">
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 8,
          background: "linear-gradient(135deg, #6366f1, #4f46e5)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 0 0 1px rgba(99,102,241,0.4), 0 2px 8px rgba(99,102,241,0.3)",
        }}>
          <ShieldCheck size={15} color="#fff" />
        </div>
        <span style={{ fontWeight: 700, fontSize: 14, letterSpacing: "-0.02em", color: "var(--text-primary)" }}>
          PRISM
        </span>
        <span style={{
          fontSize: 10, fontWeight: 600, padding: "1px 6px",
          background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: 4, color: "var(--text-brand)", letterSpacing: "0.06em",
        }}>
          v1.0
        </span>
      </div>

      {/* Divider */}
      <div style={{ width: 1, height: 20, background: "var(--border-default)", flexShrink: 0 }} />

      {/* Nav tabs */}
      <div style={{ display: "flex", alignItems: "center", gap: 2, overflow: "auto" }} className="no-scrollbar">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`nav-tab ${page === item.id ? "active" : ""}`}
            onClick={() => setPage(item.id)}
          >
            {item.icon}
            {item.label}
            {item.id === "findings" && failedCount > 0 && (
              <span style={{
                minWidth: 16, height: 16, borderRadius: 99, padding: "0 4px",
                background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.25)",
                color: "var(--red-400)", fontSize: 10, fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                {failedCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Right side: active file chip + score */}
      {activeFile && (
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          {busy && <Loader2 size={13} className="animate-spin" style={{ color: "var(--brand-400)" }} />}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "4px 10px", borderRadius: 99,
            background: "var(--bg-hover)", border: "1px solid var(--border-default)",
            fontSize: 11, color: "var(--text-secondary)", maxWidth: 200,
          }}>
            <Terminal size={11} style={{ flexShrink: 0, color: "var(--brand-400)" }} />
            <span className="truncate" title={activeFile}>{activeFile}</span>
          </div>
          <div style={{
            display: "flex", alignItems: "center", gap: 5,
            padding: "4px 10px", borderRadius: 99,
            background: score >= 80 ? "rgba(34,197,94,0.1)" : score >= 50 ? "rgba(251,191,36,0.1)" : "rgba(239,68,68,0.1)",
            border: `1px solid ${score >= 80 ? "rgba(34,197,94,0.2)" : score >= 50 ? "rgba(251,191,36,0.2)" : "rgba(239,68,68,0.2)"}`,
            fontSize: 11, fontWeight: 700,
            color: score >= 80 ? "var(--green-400)" : score >= 50 ? "var(--amber-400)" : "var(--red-400)",
          }}>
            <ShieldCheck size={11} />
            {score}%
          </div>
        </div>
      )}
    </nav>
  );
}

/* ============================================================
   Score Ring
   ============================================================ */
function ScoreRing({ score, size = 120 }: { score: number; size?: number }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "#4ade80" : score >= 50 ? "#fbbf24" : "#f87171";

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8} />
        <circle cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.16,1,0.3,1)" }}
        />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        gap: 0,
      }}>
        <span style={{ fontSize: size * 0.21, fontWeight: 800, color, lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: size * 0.09, color: "var(--text-tertiary)", fontWeight: 600, letterSpacing: "0.05em" }}>SCORE</span>
      </div>
    </div>
  );
}

/* ============================================================
   Stat Card
   ============================================================ */
function StatCard({
  label, value, sub, tone = "default", icon,
}: {
  label: string; value: string | number; sub?: string;
  tone?: "green" | "red" | "amber" | "blue" | "purple" | "default";
  icon?: React.ReactNode;
}) {
  const tones = {
    green:   { icon: "rgba(34,197,94,0.1)",  iconBorder: "rgba(34,197,94,0.2)",  iconColor: "#4ade80",  val: "#4ade80" },
    red:     { icon: "rgba(239,68,68,0.1)",   iconBorder: "rgba(239,68,68,0.2)",   iconColor: "#f87171",  val: "#f87171" },
    amber:   { icon: "rgba(251,191,36,0.1)",  iconBorder: "rgba(251,191,36,0.2)",  iconColor: "#fbbf24",  val: "#fbbf24" },
    blue:    { icon: "rgba(96,165,250,0.1)",  iconBorder: "rgba(96,165,250,0.2)",  iconColor: "#60a5fa",  val: "#60a5fa" },
    purple:  { icon: "rgba(192,132,252,0.1)", iconBorder: "rgba(192,132,252,0.2)", iconColor: "#c084fc",  val: "#c084fc" },
    default: { icon: "rgba(255,255,255,0.05)", iconBorder: "var(--border-default)", iconColor: "var(--text-secondary)", val: "var(--text-primary)" },
  };
  const t = tones[tone];

  return (
    <div className="stat-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-tertiary)", letterSpacing: "0.04em", textTransform: "uppercase" }}>
          {label}
        </span>
        {icon && (
          <div style={{
            width: 30, height: 30, borderRadius: 8,
            background: t.icon, border: `1px solid ${t.iconBorder}`,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: t.iconColor,
          }}>
            {icon}
          </div>
        )}
      </div>
      <div>
        <div style={{ fontSize: 28, fontWeight: 800, color: t.val, lineHeight: 1 }}>{value}</div>
        {sub && <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 4 }}>{sub}</div>}
      </div>
    </div>
  );
}

/* ============================================================
   Upload Zone
   ============================================================ */
function UploadZone({
  file, onFile, onLoadSample,
}: {
  file: File | null;
  onFile: (f: File | null) => void;
  onLoadSample: (t?: "cisco" | "juniper") => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  return (
    <div
      className={`upload-zone ${dragging ? "drag-over" : ""} ${file ? "has-file" : ""}`}
      style={{ padding: "2rem", textAlign: "center" }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".cfg,.conf,.txt,.log"
        style={{ display: "none" }}
        onChange={(e) => onFile(e.target.files?.[0] ?? null)}
      />

      {file ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "rgba(34,197,94,0.12)", border: "1px solid rgba(34,197,94,0.25)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Check size={20} style={{ color: "#4ade80" }} />
          </div>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{file.name}</p>
            <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 2 }}>
              {(file.size / 1024).toFixed(1)} KB · Click to change
            </p>
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }} className="animate-float">
            <Upload size={20} style={{ color: "var(--brand-400)" }} />
          </div>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
              Drop your config file here
            </p>
            <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 4 }}>
              .cfg · .conf · .txt · .log · or{" "}
              <span style={{ color: "var(--brand-400)", textDecoration: "underline" }}>browse</span>
            </p>
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 4 }} onClick={(e) => e.stopPropagation()}>
            <button
              className="btn btn-ghost"
              style={{ fontSize: 11, padding: "4px 10px" }}
              onClick={() => onLoadSample("cisco")}
            >
              <Terminal size={11} /> Load Cisco Sample
            </button>
            <button
              className="btn btn-ghost"
              style={{ fontSize: 11, padding: "4px 10px" }}
              onClick={() => onLoadSample("juniper")}
            >
              <Terminal size={11} /> Load Juniper Sample
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Finding Accordion Item
   ============================================================ */
function FindingItem({ finding, defaultOpen = false }: { finding: Finding; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const isFail = finding.status === "fail";
  const isCritical = isFail && finding.severity === "critical";
  const statusClass = isCritical ? "critical" : isFail ? "fail" : "pass";

  const severityColor = {
    critical: "#fca5a5",
    high:     "#fdba74",
    medium:   "#fcd34d",
    low:      "#94a3b8",
    informational: "#60a5fa",
  }[finding.severity] ?? "var(--text-secondary)";

  const copyRemediation = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(finding.remediation_command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`finding-item ${statusClass}`}>
      <div className="finding-header" onClick={() => setOpen(!open)}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1, minWidth: 0 }}>
          <div style={{ flexShrink: 0 }}>
            {isFail ? (
              <AlertTriangle size={14} style={{ color: isCritical ? "#f87171" : "#fb923c" }} />
            ) : (
              <Check size={14} style={{ color: "#4ade80" }} />
            )}
          </div>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }} className="truncate">
            {finding.control_name}
          </span>
          <span style={{ fontSize: 10, color: "var(--text-tertiary)", fontFamily: "var(--font-mono)", flexShrink: 0 }}>
            {finding.control_id}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          <span className={`badge badge-${finding.severity}`} style={{ fontSize: 10 }}>
            {finding.severity}
          </span>
          <span className={`badge badge-${finding.status === "pass" ? "pass" : "fail"}`} style={{ fontSize: 10 }}>
            {finding.status}
          </span>
          {open ? <ChevronDown size={13} style={{ color: "var(--text-tertiary)" }} /> : <ChevronRight size={13} style={{ color: "var(--text-tertiary)" }} />}
        </div>
      </div>

      {open && (
        <div className="finding-body">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <p className="label" style={{ marginBottom: 4 }}>Observed Config Line</p>
              <pre style={{
                background: "var(--bg-base)", border: "1px solid var(--border-subtle)",
                borderRadius: 8, padding: "8px 10px", fontSize: 11, fontFamily: "var(--font-mono)",
                color: "#93c5fd", overflowX: "auto",
              }}>
                <span style={{ opacity: 0.4, marginRight: 8 }}>L{finding.source_line}</span>
                {finding.raw_config_line || "—"}
              </pre>
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                <p className="label">Remediation Command</p>
                <button
                  className="btn btn-ghost"
                  style={{ fontSize: 10, padding: "2px 6px", gap: 3 }}
                  onClick={copyRemediation}
                >
                  {copied ? <><Check size={10} style={{ color: "#4ade80" }} /> Copied</> : <><Copy size={10} /> Copy</>}
                </button>
              </div>
              <pre style={{
                background: "var(--bg-base)", border: "1px solid var(--border-subtle)",
                borderRadius: 8, padding: "8px 10px", fontSize: 11, fontFamily: "var(--font-mono)",
                color: "#86efac", overflowX: "auto",
              }}>
                {finding.remediation_command || "No remediation required"}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Empty State
   ============================================================ */
function EmptyState({
  icon, title, desc, action, onAction,
}: {
  icon: React.ReactNode; title: string; desc: string;
  action?: string; onAction?: () => void;
}) {
  return (
    <div className="empty-state">
      <div style={{
        width: 56, height: 56, borderRadius: 16,
        background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.15)",
        display: "flex", alignItems: "center", justifyContent: "center",
        color: "var(--brand-400)", marginBottom: 4,
      }}>
        {icon}
      </div>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)" }}>{title}</h3>
      <p style={{ fontSize: 12, color: "var(--text-tertiary)", maxWidth: 340 }}>{desc}</p>
      {action && onAction && (
        <button className="btn btn-secondary" style={{ marginTop: 4 }} onClick={onAction}>
          {action} <ArrowRight size={12} />
        </button>
      )}
    </div>
  );
}

/* ============================================================
   Section Header
   ============================================================ */
function SectionHeader({
  eyebrow, title, desc, action,
}: {
  eyebrow?: string; title: string; desc?: string; action?: React.ReactNode;
}) {
  return (
    <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 16, marginBottom: "1.5rem" }}>
      <div>
        {eyebrow && <p className="label" style={{ marginBottom: 4 }}>{eyebrow}</p>}
        <h1 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.03em", color: "var(--text-primary)" }}>{title}</h1>
        {desc && <p style={{ fontSize: 12, color: "var(--text-tertiary)", marginTop: 4, maxWidth: 560 }}>{desc}</p>}
      </div>
      {action && <div style={{ flexShrink: 0 }}>{action}</div>}
    </div>
  );
}

/* ============================================================
   Main App
   ============================================================ */
export default function App() {
  const [page, setPage] = useState<Page>("overview");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedVendor, setSelectedVendor] = useState("");

  async function handleAnalyze(fileToAnalyze?: File, vendorToUse?: string) {
    const file = fileToAnalyze || selectedFile;
    const vendor = vendorToUse !== undefined ? vendorToUse : selectedVendor;
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const data = await analyzeConfiguration(file, vendor);
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setBusy(false);
    }
  }

  function loadSample(type: "cisco" | "juniper" = "cisco") {
    if (type === "cisco") {
      const s = createSampleFile("Core-Switch-01.cfg", SAMPLE_CISCO_CONFIG);
      setSelectedFile(s); setSelectedVendor("cisco"); handleAnalyze(s, "cisco");
    } else {
      const s = createSampleFile("Edge-Router-01.conf", SAMPLE_JUNIPER_CONFIG);
      setSelectedFile(s); setSelectedVendor("juniper"); handleAnalyze(s, "juniper");
    }
  }

  async function handleTrain(rawLine: string, schemaPath: string, mappedValue: string) {
    if (!analysis) return;
    setBusy(true); setError("");
    try {
      const updated = await trainMapping({
        filename: analysis.filename, raw_config: analysis.raw_config,
        vendor: analysis.vendor, raw_line: rawLine,
        schema_path: schemaPath, mapped_value: mappedValue,
      });
      setAnalysis(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Training failed");
    } finally { setBusy(false); }
  }

  const score = useMemo(() => {
    if (!analysis || !analysis.compliance.total_controls) return 0;
    return Math.round((analysis.compliance.passed / analysis.compliance.total_controls) * 100);
  }, [analysis]);

  const failedCount = analysis?.compliance.failed ?? 0;

  useEffect(() => { loadSample("cisco"); }, []);

  return (
    <div className="page-root bg-mesh" style={{ background: "var(--bg-base)" }}>
      <TopNav page={page} setPage={setPage} score={score} activeFile={analysis?.filename} busy={busy} failedCount={failedCount} />

      {/* Error banner */}
      {error && (
        <div style={{
          position: "fixed", top: 52, left: 0, right: 0, zIndex: 40,
          padding: "10px 24px",
          background: "rgba(239,68,68,0.1)", borderBottom: "1px solid rgba(239,68,68,0.2)",
          display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#fca5a5" }}>
            <AlertTriangle size={14} style={{ flexShrink: 0 }} />
            {error}
          </div>
          <button className="btn btn-ghost" style={{ padding: "2px 6px" }} onClick={() => setError("")}>
            <X size={13} />
          </button>
        </div>
      )}

      <div className="page-content" style={{ paddingTop: error ? "3.5rem" : "2rem" }}>
        {page === "overview"  && <OverviewPage analysis={analysis} score={score} onNavigate={setPage} onAnalyze={handleAnalyze} onLoadSample={loadSample} busy={busy} selectedFile={selectedFile} setSelectedFile={setSelectedFile} selectedVendor={selectedVendor} setSelectedVendor={setSelectedVendor} />}
        {page === "analysis"  && <ConfigPage analysis={analysis} onAnalyze={handleAnalyze} onLoadSample={loadSample} busy={busy} selectedFile={selectedFile} setSelectedFile={setSelectedFile} selectedVendor={selectedVendor} setSelectedVendor={setSelectedVendor} />}
        {page === "results"   && <CompliancePage analysis={analysis} onNavigate={setPage} />}
        {page === "findings"  && <FindingsPage analysis={analysis} onNavigate={setPage} />}
        {page === "training"  && <TrainingPage analysis={analysis} onTrain={handleTrain} busy={busy} onNavigate={setPage} />}
        {page === "devices"   && <DevicesPage analysis={analysis} onNavigate={setPage} />}
        {page === "policies"  && <PoliciesPage analysis={analysis} onNavigate={setPage} />}
        {page === "reports"   && <ReportsPage analysis={analysis} onNavigate={setPage} />}
        {page === "settings"  && <SettingsPage />}
      </div>
    </div>
  );
}

/* ============================================================
   Page 1: Overview
   ============================================================ */
function OverviewPage({
  analysis, score, onNavigate, onAnalyze, onLoadSample,
  busy, selectedFile, setSelectedFile, selectedVendor, setSelectedVendor,
}: {
  analysis: Analysis | null; score: number;
  onNavigate: (p: Page) => void;
  onAnalyze: (f?: File, v?: string) => void;
  onLoadSample: (t?: "cisco" | "juniper") => void;
  busy: boolean;
  selectedFile: File | null; setSelectedFile: (f: File | null) => void;
  selectedVendor: string; setSelectedVendor: (v: string) => void;
}) {
  const [showUpload, setShowUpload] = useState(!analysis);
  const compliance = analysis?.compliance;
  const device = analysis?.device_config;
  const mappedCount = Object.keys(device?.provenance ?? {}).length;
  const unmappedCount = device?.unmapped_lines.length ?? 0;
  const critFindings = compliance?.findings.filter(f => f.status === "fail") ?? [];

  return (
    <div className="animate-fade-up">
      {/* Header row */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, marginBottom: "1.75rem" }}>
        <div>
          <p className="label" style={{ marginBottom: 4 }}>Network Security</p>
          <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.035em", color: "var(--text-primary)" }}>
            Compliance Dashboard
          </h1>
          <p style={{ fontSize: 12, color: "var(--text-tertiary)", marginTop: 4 }}>
            {analysis ? `Active: ${analysis.filename} · ${analysis.vendor.toUpperCase()} · Confidence ${Math.round(analysis.detection_confidence * 100)}%` : "No configuration loaded yet"}
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
          <button className="btn btn-secondary" onClick={() => setShowUpload(!showUpload)}>
            <Upload size={13} /> {showUpload ? "Hide Upload" : "Upload Config"}
          </button>
          <button className="btn btn-ghost" onClick={() => onLoadSample("cisco")} disabled={busy}>
            <RefreshCw size={13} className={busy ? "animate-spin" : ""} /> Reload Sample
          </button>
        </div>
      </div>

      {/* Upload panel */}
      {showUpload && (
        <div className="card animate-fade-up" style={{ marginBottom: "1.5rem", padding: "1.5rem", display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, borderBottom: "1px solid var(--border-subtle)", paddingBottom: 12 }}>
            <Upload size={15} style={{ color: "var(--brand-400)" }} />
            <span style={{ fontSize: 13, fontWeight: 600 }}>Upload Device Configuration</span>
          </div>
          <UploadZone file={selectedFile} onFile={setSelectedFile} onLoadSample={onLoadSample} />
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>Vendor:</span>
              <select className="input" style={{ width: 160 }} value={selectedVendor} onChange={e => setSelectedVendor(e.target.value)}>
                <option value="">Auto-detect</option>
                <option value="cisco">Cisco IOS</option>
                <option value="juniper">Juniper JunOS</option>
                <option value="unknown">Generic CLI</option>
              </select>
            </div>
            <button
              className="btn btn-primary"
              disabled={!selectedFile || busy}
              onClick={() => { onAnalyze(); setShowUpload(false); }}
            >
              {busy ? <><Loader2 size={13} className="animate-spin" /> Analyzing…</> : <>Analyze Configuration <ArrowRight size={13} /></>}
            </button>
          </div>
        </div>
      )}

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: "1.5rem" }}>
        <div className="stat-card" style={{ gridColumn: "1", display: "flex", alignItems: "center", gap: 20 }}>
          <ScoreRing score={score} size={90} />
          <div>
            <p className="label" style={{ marginBottom: 6 }}>Compliance Score</p>
            <p style={{ fontSize: 12, color: "var(--text-tertiary)" }}>
              {compliance?.passed ?? 0} of {compliance?.total_controls ?? 0} controls passed
            </p>
          </div>
        </div>
        <StatCard label="Critical Issues" value={compliance?.critical_count ?? 0}
          sub={compliance?.critical_count ? "Immediate action required" : "No critical findings"}
          tone={compliance?.critical_count ? "red" : "green"} icon={<AlertTriangle size={14} />} />
        <StatCard label="Mapped Fields" value={mappedCount}
          sub="Provenance tracked" tone="blue" icon={<Layers size={14} />} />
        <StatCard label="Training Queue" value={unmappedCount}
          sub={unmappedCount > 0 ? "Lines awaiting review" : "All lines canonicalized"}
          tone={unmappedCount > 0 ? "amber" : "green"} icon={<Sparkles size={14} />} />
      </div>

      {/* Progress bars for control breakdown */}
      {compliance && compliance.total_controls > 0 && (
        <div className="card" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>Control Breakdown</span>
            <button
              className="btn btn-ghost" style={{ fontSize: 11 }}
              onClick={() => onNavigate("results")}
            >
              View All <ArrowRight size={11} />
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              { label: "Passed", count: compliance.passed, color: "#4ade80" },
              { label: "Failed", count: compliance.failed, color: "#f87171" },
              { label: "Critical", count: compliance.critical_count, color: "#f87171", bright: true },
            ].map(({ label, count, color, bright }) => (
              <div key={label} style={{ display: "grid", gridTemplateColumns: "80px 1fr 40px", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>{label}</span>
                <div className="progress-bar">
                  <div className="progress-bar-fill" style={{
                    width: `${(count / compliance.total_controls) * 100}%`,
                    background: bright ? `linear-gradient(90deg, ${color}, #ff5555)` : color,
                  }} />
                </div>
                <span style={{ fontSize: 11, fontWeight: 700, color, textAlign: "right" }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent findings */}
      {critFindings.length > 0 && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
              Recent Findings
            </span>
            <button className="btn btn-ghost" style={{ fontSize: 11 }} onClick={() => onNavigate("findings")}>
              View All <ArrowRight size={11} />
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {critFindings.slice(0, 4).map(f => <FindingItem key={f.control_id} finding={f} defaultOpen={f.severity === "critical"} />)}
          </div>
        </div>
      )}

      {!analysis && !busy && (
        <div className="card">
          <EmptyState
            icon={<ShieldCheck size={22} />}
            title="No Configuration Loaded"
            desc="Upload a device configuration file or load a sample to run a compliance analysis."
            action="Load Cisco Sample"
            onAction={() => { onLoadSample("cisco"); setShowUpload(false); }}
          />
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Page 2: Config Analysis
   ============================================================ */
function ConfigPage({
  analysis, onAnalyze, onLoadSample, busy,
  selectedFile, setSelectedFile, selectedVendor, setSelectedVendor,
}: {
  analysis: Analysis | null;
  onAnalyze: (f?: File, v?: string) => void;
  onLoadSample: (t?: "cisco" | "juniper") => void;
  busy: boolean;
  selectedFile: File | null; setSelectedFile: (f: File | null) => void;
  selectedVendor: string; setSelectedVendor: (v: string) => void;
}) {
  const [copiedRaw, setCopiedRaw] = useState(false);
  const [copiedBase, setCopiedBase] = useState(false);

  return (
    <div className="animate-fade-up">
      <SectionHeader
        eyebrow="Pipeline"
        title="Configuration Analysis"
        desc="Ingest device exports, view raw syntax, and inspect the normalized security baseline."
      />

      <div className="card" style={{ padding: "1.5rem", marginBottom: "1.5rem", display: "flex", flexDirection: "column", gap: 16 }}>
        <UploadZone file={selectedFile} onFile={setSelectedFile} onLoadSample={onLoadSample} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>Vendor:</span>
            <select className="input" style={{ width: 160 }} value={selectedVendor} onChange={e => setSelectedVendor(e.target.value)}>
              <option value="">Auto-detect</option>
              <option value="cisco">Cisco IOS</option>
              <option value="juniper">Juniper JunOS</option>
              <option value="unknown">Generic CLI</option>
            </select>
          </div>
          <button className="btn btn-primary" disabled={!selectedFile || busy} onClick={() => onAnalyze()}>
            {busy ? <><Loader2 size={13} className="animate-spin" /> Running Parser…</> : <>Analyze Config <ArrowRight size={13} /></>}
          </button>
        </div>
      </div>

      {analysis && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {/* Raw config */}
          <div className="card" style={{ overflow: "hidden" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <FileCode2 size={14} style={{ color: "var(--brand-400)" }} />
                <span style={{ fontSize: 12, fontWeight: 600 }}>Raw Configuration</span>
                <span style={{ fontSize: 10, color: "var(--text-tertiary)", fontFamily: "var(--font-mono)" }}>
                  {analysis.raw_config.split("\n").length} lines
                </span>
              </div>
              <button className="btn btn-ghost" style={{ fontSize: 10, padding: "3px 8px" }} onClick={() => {
                navigator.clipboard.writeText(analysis.raw_config);
                setCopiedRaw(true); setTimeout(() => setCopiedRaw(false), 2000);
              }}>
                {copiedRaw ? <><Check size={10} style={{ color: "#4ade80" }} /> Copied</> : <><Copy size={10} /> Copy</>}
              </button>
            </div>
            <pre className="code-block" style={{ borderRadius: 0, border: "none", maxHeight: 480, margin: 0 }}>
              {analysis.raw_config}
            </pre>
          </div>

          {/* Normalized baseline */}
          <div className="card" style={{ overflow: "hidden" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Layers size={14} style={{ color: "#4ade80" }} />
                <span style={{ fontSize: 12, fontWeight: 600 }}>Normalized Baseline</span>
                <span style={{ fontSize: 10, color: "var(--text-tertiary)", fontFamily: "var(--font-mono)" }}>
                  {Object.keys(analysis.device_config.provenance).length} fields
                </span>
              </div>
              <button className="btn btn-ghost" style={{ fontSize: 10, padding: "3px 8px" }} onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(analysis.device_config.baseline, null, 2));
                setCopiedBase(true); setTimeout(() => setCopiedBase(false), 2000);
              }}>
                {copiedBase ? <><Check size={10} style={{ color: "#4ade80" }} /> Copied</> : <><Copy size={10} /> Copy JSON</>}
              </button>
            </div>
            <pre className="code-block green" style={{ borderRadius: 0, border: "none", maxHeight: 480, margin: 0 }}>
              {JSON.stringify(analysis.device_config.baseline, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Page 3: Compliance
   ============================================================ */
function CompliancePage({ analysis, onNavigate }: { analysis: Analysis | null; onNavigate: (p: Page) => void }) {
  const [statusFilter, setStatusFilter] = useState<"all" | "pass" | "fail">("all");
  const [sevFilter, setSevFilter] = useState("all");

  if (!analysis) {
    return (
      <div className="animate-fade-up">
        <SectionHeader eyebrow="Evaluation" title="CIS Benchmark Compliance" />
        <div className="card">
          <EmptyState icon={<ShieldCheck size={22} />} title="No Compliance Data"
            desc="Analyze a device configuration to run deterministic benchmark checks."
            action="Go to Analysis" onAction={() => onNavigate("analysis")} />
        </div>
      </div>
    );
  }

  const { compliance } = analysis;
  const displayed = compliance.findings.filter(f => {
    if (statusFilter !== "all" && f.status !== statusFilter) return false;
    if (sevFilter !== "all" && f.severity.toLowerCase() !== sevFilter) return false;
    return true;
  });

  return (
    <div className="animate-fade-up">
      <SectionHeader
        eyebrow="Evaluation Report"
        title="CIS Benchmark Compliance"
        desc="Formal audit against CIS security controls. Click any finding to inspect observed lines and remediation."
        action={
          <button className="btn btn-secondary" onClick={() => exportAnalysisJson(compliance, `${analysis.filename}-compliance.json`)}>
            <Download size={13} /> Export Report
          </button>
        }
      />

      {/* Filter bar */}
      <div className="card" style={{ padding: "10px 14px", marginBottom: "1rem", display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ fontSize: 11, color: "var(--text-tertiary)", marginRight: 4 }}>Status:</span>
          {(["all", "fail", "pass"] as const).map(s => (
            <button key={s} className={`nav-tab ${statusFilter === s ? "active" : ""}`} style={{ padding: "4px 10px", fontSize: 11 }} onClick={() => setStatusFilter(s)}>
              {s === "all" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
        <div style={{ width: 1, height: 16, background: "var(--border-subtle)" }} />
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ fontSize: 11, color: "var(--text-tertiary)", marginRight: 4 }}>Severity:</span>
          {["all", "critical", "high", "medium", "low"].map(s => (
            <button key={s} className={`nav-tab ${sevFilter === s ? "active" : ""}`} style={{ padding: "4px 10px", fontSize: 11, textTransform: "capitalize" }} onClick={() => setSevFilter(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {displayed.map(f => <FindingItem key={f.control_id} finding={f} defaultOpen={f.severity === "critical" && f.status === "fail"} />)}
        {displayed.length === 0 && (
          <div className="card" style={{ padding: "2.5rem", textAlign: "center", color: "var(--text-tertiary)", fontSize: 12 }}>
            No findings match the selected filters.
          </div>
        )}
      </div>
    </div>
  );
}

/* ============================================================
   Page 4: Findings (Risk Register)
   ============================================================ */
function FindingsPage({ analysis, onNavigate }: { analysis: Analysis | null; onNavigate: (p: Page) => void }) {
  if (!analysis) {
    return (
      <div className="animate-fade-up">
        <SectionHeader eyebrow="Risk Register" title="Security Findings" />
        <div className="card">
          <EmptyState icon={<AlertTriangle size={22} />} title="No Active Findings"
            desc="Analyze a device configuration to populate the risk register."
            action="Go to Analysis" onAction={() => onNavigate("analysis")} />
        </div>
      </div>
    );
  }

  const tiers = ["critical", "high", "medium", "low"] as const;
  const tierColors = { critical: "#f87171", high: "#fb923c", medium: "#fbbf24", low: "#94a3b8" };

  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Risk Register" title="Prioritized Findings"
        desc="Failing controls grouped by severity with observable configuration evidence." />

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {tiers.map(sev => {
          const items = analysis.compliance.findings.filter(f => f.status === "fail" && f.severity.toLowerCase() === sev);
          return (
            <div key={sev} className="card" style={{ overflow: "hidden" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)", background: "var(--bg-raised)" }}>
                <span style={{ width: 8, height: 8, borderRadius: 99, background: tierColors[sev], flexShrink: 0, boxShadow: `0 0 6px ${tierColors[sev]}60` }} />
                <span style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: tierColors[sev] }}>{sev}</span>
                <span style={{ fontSize: 12, color: "var(--text-tertiary)" }}>— {items.length} finding{items.length !== 1 ? "s" : ""}</span>
              </div>
              <div style={{ padding: items.length > 0 ? "12px" : 0, display: "flex", flexDirection: "column", gap: 6 }}>
                {items.length > 0 ? items.map(f => <FindingItem key={f.control_id} finding={f} defaultOpen={sev === "critical"} />) : (
                  <p style={{ padding: "16px 16px", fontSize: 11, color: "var(--text-muted)", textAlign: "center" }}>
                    No {sev} severity findings detected.
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ============================================================
   Page 5: Training
   ============================================================ */
function TrainingPage({
  analysis, onTrain, busy, onNavigate,
}: {
  analysis: Analysis | null;
  onTrain: (line: string, path: string, value: string) => void;
  busy: boolean;
  onNavigate: (p: Page) => void;
}) {
  if (!analysis) {
    return (
      <div className="animate-fade-up">
        <SectionHeader eyebrow="Human-in-the-Loop" title="Training Queue" />
        <div className="card">
          <EmptyState icon={<Sparkles size={22} />} title="No Active Configuration"
            desc="Upload and analyze a configuration file to inspect and train unmapped syntax."
            action="Go to Analysis" onAction={() => onNavigate("analysis")} />
        </div>
      </div>
    );
  }

  const unmapped = analysis.device_config.unmapped_lines;

  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Human-in-the-Loop" title="Training Queue"
        desc="Confirm what PRISM could not map automatically. Confirmed mappings are stored permanently." />

      {unmapped.length === 0 ? (
        <div className="card">
          <EmptyState icon={<Check size={22} />} title="Training Queue Clear"
            desc="Every configuration line was successfully canonicalized into the security baseline."
            action="View Compliance" onAction={() => onNavigate("results")} />
        </div>
      ) : (
        <div>
          <div style={{
            display: "flex", alignItems: "center", gap: 8, padding: "10px 14px",
            background: "rgba(251,191,36,0.06)", border: "1px solid rgba(251,191,36,0.15)",
            borderRadius: "var(--radius-lg)", marginBottom: "1rem", fontSize: 12, color: "#fcd34d",
          }}>
            <Sparkles size={14} />
            {unmapped.length} unmapped line{unmapped.length !== 1 ? "s" : ""} awaiting classification.
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {unmapped.map(item => (
              <TrainingCard key={item.line_no} lineNo={item.line_no} raw={item.raw} busy={busy} onTrain={onTrain} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TrainingCard({ lineNo, raw, busy, onTrain }: {
  lineNo: number; raw: string; busy: boolean;
  onTrain: (line: string, path: string, value: string) => void;
}) {
  const [schemaPath, setSchemaPath] = useState<string>(SCHEMA_OPTIONS[0]);
  const [mappedValue, setMappedValue] = useState("");

  return (
    <div className="card" style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{
          fontSize: 10, fontWeight: 700, padding: "2px 8px",
          background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: 4, color: "var(--brand-400)", fontFamily: "var(--font-mono)",
        }}>
          LINE {lineNo}
        </span>
        <span style={{ fontSize: 10, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
          Unmapped
        </span>
      </div>
      <pre className="code-block" style={{ margin: 0, padding: "10px 12px" }}>{raw}</pre>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: 10, alignItems: "flex-end" }}>
        <div>
          <p className="label" style={{ marginBottom: 4 }}>Canonical Baseline Field</p>
          <select className="input" value={schemaPath} onChange={e => setSchemaPath(e.target.value)}>
            {SCHEMA_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
        <div>
          <p className="label" style={{ marginBottom: 4 }}>Value (defaults to true)</p>
          <input type="text" className="input" placeholder="e.g. 2, false, true"
            value={mappedValue} onChange={e => setMappedValue(e.target.value)} />
        </div>
        <button className="btn btn-primary" disabled={busy} onClick={() => onTrain(raw, schemaPath, mappedValue)}>
          {busy ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />}
          Confirm
        </button>
      </div>
    </div>
  );
}

/* ============================================================
   Page 6: Devices
   ============================================================ */
function DevicesPage({ analysis, onNavigate }: { analysis: Analysis | null; onNavigate: (p: Page) => void }) {
  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Inventory" title="Device Inventory"
        desc="Catalog of analyzed network hardware with compliance state." />
      {analysis ? (
        <div className="card" style={{ overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 18px", borderBottom: "1px solid var(--border-subtle)", background: "var(--bg-raised)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Server size={16} style={{ color: "var(--brand-400)" }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>{analysis.filename}</span>
            </div>
            <span className={`badge ${analysis.compliance.passed === analysis.compliance.total_controls ? "badge-pass" : "badge-warn"}`}>
              {analysis.compliance.passed === analysis.compliance.total_controls ? "Compliant" : "Issues Detected"}
            </span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 0 }}>
            {[
              { label: "Platform", value: analysis.vendor.toUpperCase(), color: "var(--text-primary)" },
              { label: "Detection Confidence", value: `${Math.round(analysis.detection_confidence * 100)}%`, color: "#4ade80" },
              { label: "Controls Passed", value: `${analysis.compliance.passed} / ${analysis.compliance.total_controls}`, color: "var(--text-primary)" },
            ].map(({ label, value, color }, i) => (
              <div key={i} style={{ padding: "1.25rem 1.5rem", borderRight: i < 2 ? "1px solid var(--border-subtle)" : "none" }}>
                <p className="label" style={{ marginBottom: 6 }}>{label}</p>
                <p style={{ fontSize: 18, fontWeight: 700, color, fontFamily: "var(--font-mono)" }}>{value}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card">
          <EmptyState icon={<Server size={22} />} title="No Devices Analyzed"
            desc="Multi-device inventory is built as configurations are analyzed."
            action="Analyze First Device" onAction={() => onNavigate("analysis")} />
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Stub pages
   ============================================================ */
function PoliciesPage({ analysis, onNavigate }: { analysis: Analysis | null; onNavigate: (p: Page) => void }) {
  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Governance" title="CIS Benchmark Policies"
        desc="Framework rules executed by the Tier 1 deterministic engine." />
      <div className="card" style={{ padding: "1.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <ShieldCheck size={16} style={{ color: "var(--brand-400)" }} />
          <span style={{ fontSize: 14, fontWeight: 600 }}>Active Policy Set: CIS Benchmark v2.0</span>
        </div>
        <p style={{ fontSize: 12, color: "var(--text-tertiary)", lineHeight: 1.7, maxWidth: 560, marginBottom: 16 }}>
          Rules cover SSH configuration, Telnet prohibition, HTTP management hardening, AAA authentication, minimum password complexity, and syslog transport enforcement.
        </p>
        <button className="btn btn-secondary" onClick={() => onNavigate(analysis ? "results" : "analysis")}>
          {analysis ? "View Policy Results" : "Upload Configuration"} <ArrowRight size={12} />
        </button>
      </div>
    </div>
  );
}

function ReportsPage({ analysis, onNavigate }: { analysis: Analysis | null; onNavigate: (p: Page) => void }) {
  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Audit Trail" title="Recent Scans" />
      <div className="card">
        <EmptyState icon={<Activity size={22} />}
          title={analysis ? "Current Scan Active" : "No Scan History"}
          desc={analysis ? `Active scan for ${analysis.filename}. All audit logs stored locally.` : "Run a configuration scan to record an audit milestone."}
          action={analysis ? "Inspect Compliance" : "Upload Config"}
          onAction={() => onNavigate(analysis ? "results" : "analysis")} />
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="animate-fade-up">
      <SectionHeader eyebrow="Preferences" title="Workspace Settings"
        desc="PRISM API configuration, engine endpoints, and local workspace options." />
      <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: 20, maxWidth: 560 }}>
        <div>
          <p style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>FastAPI Backend Endpoint</p>
          <input type="text" className="input" readOnly value={import.meta.env.VITE_API_URL || "http://localhost:8000 (Vite Proxy: /api)"} style={{ fontFamily: "var(--font-mono)" }} />
          <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 4 }}>API communications route locally with full CORS support.</p>
        </div>
        <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 16 }}>
          <p style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Deterministic Engine</p>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#4ade80" }}>
            <span style={{ width: 8, height: 8, borderRadius: 99, background: "#4ade80", boxShadow: "0 0 6px #4ade80" }} />
            Tier 1 Pattern Matching Engine Active
          </div>
          <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 4 }}>Exact YAML regex mapping with zero hallucinatory outputs.</p>
        </div>
      </div>
    </div>
  );
}
