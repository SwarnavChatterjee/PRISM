import type { Analysis } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "";

export const SCHEMA_OPTIONS = [
  "baseline.remote_access.ssh_version",
  "baseline.remote_access.telnet_enabled",
  "baseline.remote_access.http_management_enabled",
  "baseline.authentication.aaa_enabled",
  "baseline.authentication.min_password_length",
  "baseline.logging.syslog_configured",
] as const;

export async function analyzeConfiguration(file: File, vendor = ""): Promise<Analysis> {
  const form = new FormData();
  form.append("file", file);
  if (vendor) {
    form.append("vendor", vendor);
  }

  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: form,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? `Analysis failed with status ${response.status}`);
  }

  return data as Analysis;
}

export interface TrainParams {
  filename: string;
  raw_config: string;
  vendor: string;
  raw_line: string;
  schema_path: string;
  mapped_value: string;
}

export async function trainMapping(params: TrainParams): Promise<Analysis> {
  const { filename, raw_config, vendor, raw_line, schema_path, mapped_value } = params;

  let parsedValue: unknown = mapped_value;
  if (mapped_value === "" || mapped_value.toLowerCase() === "true") {
    parsedValue = true;
  } else if (mapped_value.toLowerCase() === "false") {
    parsedValue = false;
  } else if (/^\d+$/.test(mapped_value)) {
    parsedValue = Number(mapped_value);
  }

  const response = await fetch(`${API_BASE}/api/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filename,
      raw_config,
      vendor,
      raw_line,
      schema_path,
      mapped_value: parsedValue,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? `Training failed with status ${response.status}`);
  }

  return data as Analysis;
}

export function exportAnalysisJson(data: unknown, filename = "prism-compliance-results.json"): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

export async function exportCompliancePdf(analysis: Analysis): Promise<void> {
  const response = await fetch(`${API_BASE}/api/report/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(analysis),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail ?? `PDF export failed with status ${response.status}`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${analysis.filename.replace(/\.[^.]+$/, "")}-compliance-report.pdf`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
