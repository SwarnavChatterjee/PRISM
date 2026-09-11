export type Page =
  | "overview"
  | "devices"
  | "analysis"
  | "training"
  | "results"
  | "findings"
  | "policies"
  | "reports"
  | "settings";

export type FindingStatus = "pass" | "fail" | "warn" | "info";
export type FindingSeverity = "critical" | "high" | "medium" | "low" | "informational";

export interface Finding {
  control_id: string;
  control_name: string;
  status: string;
  severity: string;
  source_line: number;
  raw_config_line: string;
  remediation_command: string;
  rationale?: string;
  references?: { source?: string; url?: string }[];
}

export interface UnmappedLine {
  line_no: number;
  raw: string;
  status: string;
}

export interface DeviceConfig {
  baseline: Record<string, unknown>;
  unmapped_lines: UnmappedLine[];
  provenance: Record<string, unknown>;
}

export interface ComplianceSummary {
  total_controls: number;
  passed: number;
  failed: number;
  critical_count: number;
  findings: Finding[];
}

export interface Analysis {
  filename: string;
  vendor: string;
  detection_confidence: number;
  raw_config: string;
  device_config: DeviceConfig;
  compliance: ComplianceSummary;
}

export type Tone = "blue" | "green" | "amber" | "red" | "muted";
