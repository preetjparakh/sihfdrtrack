"use client";

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import CollegeStatusPage from "./CollegeStatusPage";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const NAV = [
  ["overview", "Overview", "◫"],
  ["submissions", "FDR submissions", "▤"],
  ["renewals", "Renewals", "⟳"],
  ["releases", "Release queue", "⇧"],
  ["reports", "Reports", "▥"],
  ["audit", "Audit trail", "◷"],
  ["college-status", "College status", "⌖"],
] as const;
const BANK_OPTIONS = [
  ["DEMO-BANK-01", "Aegis National Trust"],
  ["DEMO-BANK-02", "Vanguard Horizon Bank"],
  ["DEMO-BANK-03", "Crestview Commerce Bank"],
  ["DEMO-BANK-04", "Meridian Reserve Corp"],
  ["DEMO-BANK-05", "Silverline Federal Credit Union"],
  ["DEMO-BANK-06", "Solstice Merchant Bank"],
] as const;

function bankName(bankId?: string) {
  return BANK_OPTIONS.find(([id]) => id === bankId)?.[1] || bankId || "—";
}

function displayAuditState(value: unknown) {
  let serialized = JSON.stringify(value ?? "—");
  serialized = serialized.replaceAll("DEMO-FDR-", "FDR-2026-");
  for (const [id, name] of BANK_OPTIONS) serialized = serialized.replaceAll(id, name);
  return serialized;
}

type Persona = { id: string; email: string; role: "COLLEGE" | "OFFICER" | "APPROVER"; institution_id?: string; institution_name?: string; badge: string };
type Submission = {
  id: string; institution_id: string; scenario: string; application_reference: string; instrument_type: string;
  entered_bank_id?: string; entered_fdr_number: string; entered_depositor_name: string; entered_principal_amount: string;
  entered_currency: string; entered_issue_date: string; entered_maturity_date: string; entered_instrument_status: string; review_status: string;
  verification_status: string; submitted_at: string; assigned_officer_id?: string; predecessor_submission_id?: string;
  documents?: DocumentRecord[]; ocr_results?: OCRRecord[]; discrepancies?: Discrepancy[]; verifications?: Record<string, unknown>[];
};
type DocumentRecord = { id: string; filename: string; mime_type: string; file_path: string; sha256: string };
type OCRRecord = { id: string; field: string; raw_value: string; normalized_value?: string; confidence?: number; corrected_value?: string; review_status: string };
type Discrepancy = { id: string; field: string; submitted_value?: string; document_value?: string; source_value?: string; reason: string; college_response?: string; resolution?: string };
type Dashboard = { demo_clock: string; display_time: string; total_submissions: number; pending_review: number; under_review: number; pending_bank_confirmation: number; confirmed_submissions: number; mismatched_submissions: number; active_discrepancies: number; approaching_maturity: number; matured: number; pending_renewals: number; pending_releases: number };
type ReportItem = { submission_id: string; institution_id: string; application_reference: string; scenario: string; fdr_number: string; amount: string; review_status: string; verification_status: string; instrument_status: string; maturity_date: string; days_to_maturity: number | null; renewal_id: string | null; renewal_status: string | null; release_status: string | null; active_discrepancies: number };
type Release = { id: string; submission_id: string; request_type: string; reason: string; status: string; requested_at?: string; officer_recommendation?: string; recommended_at?: string; authority_decision?: string; decision_reason?: string; approved_at?: string; execution_reference?: string; executed_at?: string };
type Renewal = { id: string; predecessor: Record<string, string> | null; successor: Record<string, string> | null; status: string; linked_at: string };
type Audit = { id: string; entity_type: string; entity_id: string; actor_id: string; action: string; timestamp: string; before_state: unknown; after_state: unknown; reason?: string };
type NotificationRecord = { id: string; submission_id: string; event_type: string; deadline_type: string; due_date: string; offset_days: number; scheduled_at: string; sent_at?: string; delivery_status: string };

async function api<T>(path: string, userId: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-Demo-User-Id", userId);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API}${path}`, { ...options, headers, cache: "no-store" });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

function Badge({ children, tone = "" }: { children: React.ReactNode; tone?: string }) {
  const status = String(children).toLowerCase().replaceAll("_", "-");
  return <span className={`badge ${tone || status}`}>{children}</span>;
}

function IconMark() {
  return <div className="brand-mark"><span>A</span><i /></div>;
}

export default function Home() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [userId, setUserId] = useState("USER-C01");
  const [page, setPage] = useState<string>("overview");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [releases, setReleases] = useState<Release[]>([]);
  const [renewals, setRenewals] = useState<Renewal[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [notifications, setNotifications] = useState<NotificationRecord[]>([]);
  const [selected, setSelected] = useState<Submission | null>(null);
  const [clock, setClock] = useState("Loading demo clock…");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [draftId, setDraftId] = useState("");
  const [ocr, setOcr] = useState<OCRRecord[]>([]);
  const [documentUrl, setDocumentUrl] = useState("");
  const [form, setForm] = useState({ application_reference: "", bank_id: "DEMO-BANK-01", fdr_number: "", depositor_name: "", principal_amount: "", issue_date: "2026-01-15", maturity_date: "2027-04-24" });

  const currentUser = personas.find((p) => p.id === userId);
  const isOfficer = currentUser?.role === "OFFICER";
  const isApprover = currentUser?.role === "APPROVER";
  const isCollege = currentUser?.role === "COLLEGE";

  useEffect(() => {
    if (!isOfficer && page === "college-status") setPage("overview");
  }, [isOfficer, page]);

  const refresh = useCallback(async () => {
    if (!userId) return;
    setError("");
    try {
      const [dash, subs, rels, rens, audits, report, reminders] = await Promise.all([
        api<Dashboard>("/api/dashboard", userId),
        api<Submission[]>("/api/submissions", userId),
        api<Release[]>("/api/release-requests", userId),
        api<Renewal[]>("/api/renewals", userId),
        api<Audit[]>("/api/audit?limit=80", userId),
        api<{ items: ReportItem[] }>("/api/reports", userId),
        api<NotificationRecord[]>("/api/notifications", userId),
      ]);
      setDashboard(dash);
      setSubmissions(subs);
      setReleases(rels);
      setRenewals(rens);
      setAudit(audits);
      setReports(report.items);
      setNotifications(reminders);
      setClock(dash.display_time);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load portal data.");
    }
  }, [userId]);

  useEffect(() => {
    api<Persona[]>("/api/auth/personas", "USER-C01").then((items) => {
    const demoPersonas = items.filter((item) => ["USER-C01", "USER-O01", "USER-A01"].includes(item.id));
    setPersonas(demoPersonas);
    if (demoPersonas.some((item) => item.id === userId)) return;
    setUserId(demoPersonas[0]?.id || "USER-C01");
    }).catch((e: unknown) => setError(e instanceof Error ? e.message : "Backend unavailable."));
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    const timer = window.setInterval(() => { void refresh(); }, 20_000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const filteredSubmissions = useMemo(() => {
    if (page === "submissions" && isOfficer) {
      return submissions.filter((s) => ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(s.review_status));
    }
    return submissions;
  }, [page, isOfficer, submissions]);

  async function perform(action: () => Promise<unknown>, success: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      setNotice(success);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  async function selectSubmission(item: Submission) {
    setSelected(item);
    try {
      const detail = await api<Submission>(`/api/submissions/${item.id}`, userId);
      setSelected(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to open submission.");
    }
  }

  async function createDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await perform(async () => {
      const result = await api<Submission>("/api/submissions", userId, {
        method: "POST",
        body: JSON.stringify({ ...form, instrument_type: "FDR", currency: "INR", beneficiary_name: "AICTE (demo only)", lien_status: "MARKED", lien_in_favour_of: "AICTE (demo only)" }),
      });
      setDraftId(result.id);
      setShowNew(false);
      setPage("submissions");
      setForm({ application_reference: "", bank_id: "DEMO-BANK-01", fdr_number: "", depositor_name: "", principal_amount: "", issue_date: "2026-01-15", maturity_date: "2027-04-24" });
    }, "Draft created. Upload the instrument to review clearly labeled demonstration values.");
  }

  async function uploadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !draftId) return;
    if (file.size > 15 * 1024 * 1024) {
      setError("File exceeds the 15 MB limit.");
      return;
    }
    const extension = file.name.split(".").pop()?.toLowerCase();
    const supportedType = ["image/png", "image/jpeg", "application/pdf"].includes(file.type);
    const supportedExtension = ["png", "jpg", "jpeg", "pdf"].includes(extension || "");
    if (!supportedType && !supportedExtension) {
      setError("Upload a PNG, JPEG, or PDF document.");
      event.target.value = "";
      return;
    }
    setBusy(true);
    setError("");
    try {
      const body = new FormData();
      const contentType = ({
        png: "image/png",
        jpg: "image/jpeg",
        jpeg: "image/jpeg",
        pdf: "application/pdf",
      } as Record<string, string>)[extension || ""] || "application/octet-stream";
      body.append("file", new Blob([file], { type: contentType }), file.name);
      body.append("doc_type", "FDR_RECEIPT");
      const document = await api<DocumentRecord>(`/api/submissions/${draftId}/documents`, userId, { method: "POST", body });
      const extracted = await api<OCRRecord[]>(`/api/documents/${document.id}/ocr`, userId);
      setOcr(extracted);
      setDocumentUrl(URL.createObjectURL(file));
      setNotice(`Document secured. SHA-256 ${document.sha256.slice(0, 16)}…`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload or OCR failed.");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  async function correctOcr(result: OCRRecord) {
    const value = window.prompt(`Correct ${result.field}`, result.corrected_value || result.normalized_value || result.raw_value);
    if (value === null || !value.trim()) return;
    await perform(() => api(`/api/ocr-results/${result.id}/correct`, userId, {
      method: "PUT", body: JSON.stringify({ corrected_value: value.trim(), reason: "College representative visual review" }),
    }), `${result.field} correction recorded with provenance.`);
    if (selected) await selectSubmission(selected);
  }

  async function submitDraft(id: string) {
    setBusy(true);
    setError("");
    try {
      const result = await api<{ acknowledgement_id: string }> (`/api/submissions/${id}/submit`, userId, { method: "POST" });
      setNotice(`Finalized and routed to scrutiny. Acknowledgement: ${result.acknowledgement_id}`);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submission could not be finalized.");
      return;
    } finally {
      setBusy(false);
    }
    setDraftId("");
    setOcr([]);
    if (documentUrl) URL.revokeObjectURL(documentUrl);
    setDocumentUrl("");
  }

  async function verifyCase(item: Submission) {
    await perform(() => api(`/api/submissions/${item.id}/verify-bank`, userId, { method: "POST" }), `Independent demonstration bank-service check completed for ${item.id}.`);
    await selectSubmission(item);
  }

  async function acceptCase(item: Submission) {
    await perform(() => api(`/api/submissions/${item.id}/accept`, userId, { method: "POST" }), `${item.id} accepted.`);
    setSelected(null);
  }

  async function startReview(item: Submission) {
    await perform(() => api(`/api/submissions/${item.id}/start-review`, userId, { method: "POST" }), `${item.id} moved to officer review.`);
    setSelected(null);
  }

  async function rejectCase(item: Submission) {
    const reason = window.prompt(`Reason for rejecting ${item.id}`);
    if (!reason?.trim()) return;
    await perform(() => api(`/api/submissions/${item.id}/reject`, userId, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }), `${item.id} rejected with a recorded reason.`);
    setSelected(null);
  }

  async function respondToDiscrepancy(item: Discrepancy) {
    const response = window.prompt(`Clarification for ${item.field}`);
    if (!response?.trim()) return;
    await perform(() => api(`/api/discrepancies/${item.id}/respond`, userId, { method: "POST", body: JSON.stringify({ response }) }), "Clarification sent to the scrutiny officer.");
    if (selected) await selectSubmission(selected);
  }

  async function resolveDiscrepancy(item: Discrepancy) {
    const resolution = window.prompt("Resolution: RESOLVED_ACCEPTED or RESOLVED_REJECTED", "RESOLVED_ACCEPTED");
    if (!resolution?.trim()) return;
    await perform(() => api(`/api/discrepancies/${item.id}/resolve`, userId, {
      method: "POST",
      body: JSON.stringify({ resolution: resolution.trim().toUpperCase() }),
    }), "Discrepancy resolution recorded.");
    if (selected) await selectSubmission(selected);
  }

  async function issueDiscrepancy(item: Submission) {
    const field = window.prompt("Field requiring clarification (e.g. lien_status, beneficiary_name)");
    if (!field?.trim()) return;
    const reason = window.prompt("Explain the discrepancy and what evidence is required");
    if (!reason?.trim()) return;
    await perform(() => api(`/api/submissions/${item.id}/discrepancies`, userId, {
      method: "POST",
      body: JSON.stringify({ field: field.trim(), reason: reason.trim() }),
    }), "Discrepancy query routed to the institution.");
    await selectSubmission(item);
  }

  async function manualConfirm(item: Submission) {
    const contact_source = window.prompt("Verified bank contact source (e.g. official branch phone/email)");
    if (!contact_source?.trim()) return;
    const notes = window.prompt("Record verification notes and provenance");
    if (!notes?.trim()) return;
    await perform(() => api(`/api/submissions/${item.id}/manual-confirm`, userId, {
      method: "POST",
      body: JSON.stringify({
        contact_source,
        notes,
        confirmed_fields: {
          fdr_number: item.entered_fdr_number,
          principal_amount: item.entered_principal_amount,
          maturity_date: item.entered_maturity_date,
          depositor_name: item.entered_depositor_name,
        },
      }),
    }), "Manual bank confirmation recorded with officer provenance.");
    await selectSubmission(item);
  }

  async function openPrivateDocument(document: DocumentRecord) {
    const preview = window.open("about:blank", "_blank");
    if (!preview) {
      setError("Allow pop-ups to open this private document.");
      return;
    }
    try {
      const response = await fetch(`${API}/api/documents/${document.id}/file`, {
        headers: { "X-Demo-User-Id": userId },
      });
      if (!response.ok) throw new Error("Document could not be opened.");
      const url = URL.createObjectURL(await response.blob());
      preview.location.href = url;
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (e) {
      preview.close();
      setError(e instanceof Error ? e.message : "Document could not be opened.");
    }
  }

  async function releaseAction(path: string, body: unknown, success: string) {
    await perform(() => api(path, userId, { method: "POST", body: JSON.stringify(body) }), success);
  }

  async function startRelease(item: Submission) {
    const request_type = window.prompt("Request type: RELEASE, REFUND, or DISCHARGE", "RELEASE")?.trim().toUpperCase();
    if (!request_type || !["RELEASE", "REFUND", "DISCHARGE"].includes(request_type)) return;
    const reason = window.prompt(`Reason for release of ${item.id}`);
    if (reason?.trim()) await releaseAction(`/api/submissions/${item.id}/release-requests`, { request_type, reason }, `${request_type.toLowerCase()} request submitted.`);
  }

  async function reviewRelease(item: Release) {
    const zero_liabilities_verified = window.confirm("Have zero liabilities been independently verified? Choose Cancel to return the request with reasons.");
    const recommendation = window.prompt(zero_liabilities_verified ? "Officer recommendation and evidence notes" : "Reasons the request must be returned");
    if (recommendation?.trim()) await releaseAction(
      `/api/release-requests/${item.id}/recommend`,
      { recommendation, zero_liabilities_verified },
      zero_liabilities_verified ? "Recommendation sent to competent authority." : "Release request returned for further information.",
    );
  }

  async function decideRelease(item: Release) {
    const decision = window.prompt("Decision: APPROVED, RETURNED, or REJECTED", "APPROVED")?.toUpperCase();
    if (!decision || !["APPROVED", "RETURNED", "REJECTED"].includes(decision)) return;
    const reason = window.prompt("Decision reasons");
    if (reason?.trim()) await releaseAction(`/api/release-requests/${item.id}/decision`, { decision, reason }, `Release ${decision.toLowerCase()}.`);
  }

  async function executeRelease(item: Release) {
    const discharge_reference = window.prompt("Formal bank discharge reference");
    if (!discharge_reference?.trim()) return;
    const evidence = window.prompt("Execution evidence / confirmation notes");
    if (evidence?.trim()) await releaseAction(`/api/release-requests/${item.id}/execute`, { discharge_reference, evidence }, "Formal discharge recorded; release completed.");
  }

  async function triggerReminders() {
    await perform(() => api("/api/reminders/run", userId, { method: "POST" }), "Reminder schedule updated; due reminders sent.");
  }

  async function advanceClock() {
    const days = Number(window.prompt("Advance frozen demo clock by how many days?", "30"));
    if (!Number.isFinite(days)) return;
    await perform(() => api("/api/demo/clock/advance", userId, { method: "POST", body: JSON.stringify({ days }) }), `Demo clock advanced by ${days} days.`);
  }

  const pageTitle = NAV.find(([key]) => key === page)?.[1] || "Overview";

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><IconMark /><div><strong>AICTE</strong><small>SECURITY DEPOSIT PORTAL</small></div></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav>{NAV.filter(([key]) => key !== "college-status" || isOfficer).map(([key, label, icon]) => <button key={key} className={page === key ? "nav-item active" : "nav-item"} onClick={() => { setPage(key); setSelected(null); }}><span className="nav-icon">{icon}</span>{key === "submissions" && isOfficer ? "To be verified" : label}{key === "submissions" && isOfficer && <span className="nav-count">{submissions.filter((s) => ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(s.review_status)).length}</span>}</button>)}</nav>
        <div className="sidebar-bottom"><div className="security-note"><span className="lock">◆</span><div><b>Protected workspace</b><small>Role-scoped access enabled</small></div></div><div className="sidebar-version">FDR TRACK <span>AICTE</span></div></div>
      </aside>

      <main className="main"> 
        <header className="topbar">
          <div className="crumb"><span>AICTE</span><i>/</i><b>{pageTitle}</b></div>
          <div className="top-actions">
            <div className="clock-chip"><span className="clock-dot" /><span>{clock}</span></div>
            <span className="synthetic-tag">SELECT PERSONA</span>
            <select className="persona-select" aria-label="Demo persona" value={userId} onChange={(e) => { setUserId(e.target.value); setSelected(null); setDraftId(""); setOcr([]); }}>
              {personas.map((persona) => <option key={persona.id} value={persona.id}>{persona.badge}</option>)}
            </select>
            <div className="avatar">{currentUser?.id.slice(-3) || "…"}</div>
          </div>
        </header>

        <section className="content">
          <div className="page-heading">
            <div><p className="eyebrow">{isOfficer ? "REGULATORY WORKSPACE" : isApprover ? "AUTHORITY WORKSPACE" : "INSTITUTION WORKSPACE"}</p><h1>{page === "submissions" && isOfficer ? "To be verified" : pageTitle}</h1><p className="subheading">{page === "overview" ? "A clear view of every instrument, verification, and action that needs attention." : page === "college-status" ? "A national view of the illustrative FDR portfolio and institution review history." : `Manage ${pageTitle.toLowerCase()} with traceable, role-authorized actions.`}</p></div>
            <div className="heading-actions">{(isOfficer || isApprover) && <button className="button secondary" onClick={() => void refresh()} disabled={busy}>↻ Refresh workspace</button>}{isOfficer && <button className="button secondary" onClick={triggerReminders} disabled={busy}>Run reminder job</button>}{isCollege && <button className="button primary" onClick={() => setShowNew(true)}>＋ New FDR submission</button>}</div>
          </div>
          {page !== "college-status" && <div className="prototype-banner"><span className="banner-icon">V</span><div><b>Record review evidence under consideration</b><span>Uploaded-document review values and bank responses are for authoritative verification.</span></div><span className="watermark">VERIFICATION ENVIRONMENT</span></div>}
          {error && <div className="toast error"><b>Action needs attention</b><span>{error}</span><button onClick={() => setError("")}>×</button></div>}
          {notice && <div className="toast success"><b>Done</b><span>{notice}</span><button onClick={() => setNotice("")}>×</button></div>}

          {page === "overview" && <Overview dashboard={dashboard} submissions={submissions} reports={reports} releases={releases} renewals={renewals} audit={audit} notifications={notifications} isOfficer={!!isOfficer} onOpen={(s) => void selectSubmission(s)} onNavigate={setPage} onAdvance={advanceClock} />}
          {page === "submissions" && <SubmissionsPage items={filteredSubmissions} role={currentUser?.role} onOpen={(s) => void selectSubmission(s)} onVerify={verifyCase} onStartReview={startReview} onAccept={acceptCase} onReject={rejectCase} onRelease={startRelease} />}
          {page === "renewals" && <RenewalsPage items={renewals} submissions={submissions} role={currentUser?.role} onOpen={(s) => void selectSubmission(s)} onCreate={async (s) => {
            const fdr_number = window.prompt("Successor FDR number");
            if (!fdr_number?.trim()) return;
            const application_reference = window.prompt("Successor application reference", `${s.application_reference}-R1`);
            if (!application_reference?.trim()) return;
            await perform(async () => {
              const linked = await api<{ successor: string }>(`/api/submissions/${s.id}/renewal`, userId, { method: "POST", body: JSON.stringify({ application_reference, instrument_type: "FDR", bank_id: s.entered_bank_id || "DEMO-BANK-01", fdr_number, depositor_name: s.entered_depositor_name, principal_amount: s.entered_principal_amount, currency: s.entered_currency, issue_date: "2026-10-26", maturity_date: "2027-10-26" }) });
              setDraftId(linked.successor);
            }, "Successor draft linked. Upload its instrument; the predecessor stays active until acceptance.");
          }} />}
          {page === "releases" && <ReleasesPage items={releases} role={currentUser?.role} submissions={submissions} onOpen={(s) => void selectSubmission(s)} onReview={reviewRelease} onDecide={decideRelease} onExecute={executeRelease} />}
          {page === "reports" && <ReportsPage items={reports} userId={userId} onOpen={(id) => { const submission = submissions.find((item) => item.id === id); if (submission) void selectSubmission(submission); }} />}
          {page === "audit" && <AuditPage items={audit} />}
          {page === "college-status" && isOfficer && <CollegeStatusPage />}

          {selected && <SubmissionDrawer item={selected} role={currentUser?.role} userId={userId} onClose={() => setSelected(null)} onVerify={refresh} onUpdate={setSelected} onStartReview={() => void startReview(selected)} onAccept={() => void acceptCase(selected)} onReject={() => void rejectCase(selected)} onRelease={() => void startRelease(selected)} onResponse={respondToDiscrepancy} onResolve={resolveDiscrepancy} onIssueQuery={() => void issueDiscrepancy(selected)} onManual={() => void manualConfirm(selected)} onOpenDocument={openPrivateDocument} />}
          {showNew && <div className="modal-backdrop" onClick={() => setShowNew(false)}><div className="modal" onClick={(e) => e.stopPropagation()}><div className="modal-title"><div><p className="eyebrow">INSTRUMENT INTAKE</p><h2>Start a new submission</h2></div><button className="icon-button" onClick={() => setShowNew(false)}>×</button></div><p className="modal-copy">Create a draft, then upload a private scan for demonstration-value review.</p><form className="form-grid" onSubmit={(e) => void createDraft(e)}>{[
            ["application_reference", "Application reference"], ["bank_id", "Bank ID"], ["fdr_number", "FDR number"], ["depositor_name", "Depositor name"], ["principal_amount", "Principal amount (INR)"], ["issue_date", "Issue date"], ["maturity_date", "Maturity date"], 
          ].map(([key, label]) => <label key={key}>{label}{key === "bank_id" ? <select required value={form.bank_id} onChange={(e) => setForm({ ...form, bank_id: e.target.value })}>{BANK_OPTIONS.map(([id, name]) => <option key={id} value={id}>{name}</option>)}</select> : <input required value={form[key as keyof typeof form]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} type={key.includes("date") ? "date" : "text"} />}</label>)}<div className="form-footer"><span>Private storage · 15 MB max · PNG, JPEG, PDF</span><button className="button primary" disabled={busy}>Create draft →</button></div></form></div></div>}

          {draftId && <div className="modal-backdrop"><div className="modal wide-modal"><div className="modal-title"><div><p className="eyebrow">DRAFT · {draftId}</p><h2>Upload and review instrument</h2></div><button className="icon-button" onClick={() => { setDraftId(""); setOcr([]); if (documentUrl) URL.revokeObjectURL(documentUrl); setDocumentUrl(""); }}>×</button></div><p className="modal-copy">Choose a PDF or image. The portal displays review values </p><div className="upload-box"><span className="upload-icon">↑</span><label className="button secondary">Choose instrument file<input type="file" accept="image/png,image/jpeg,application/pdf" onChange={(e) => void uploadFile(e)} /></label><small>PDF, PNG or JPEG · maximum 15 MB · privately stored</small></div>{ocr.length > 0 && <><div className="mock-notice"><b>EXPRESSED VALUES</b><span>These values are extracted from the uploaded file. Manually review the document visually & ensure correct values before submission.</span></div><h3 className="section-title">Document review values</h3><div className="ocr-review"><div className="document-preview">{documentUrl ? <iframe title="Uploaded instrument preview" src={documentUrl} /> : <div className="preview-placeholder">Document preview</div>}</div><div className="ocr-fields">{ocr.map((field) => <div className="ocr-row" key={field.id}><div><b>{field.field.replaceAll("_", " ")}</b><small>{field.raw_value}</small></div><div><strong>{field.corrected_value || field.normalized_value || field.raw_value}</strong><small>Cumulative confidence {Math.round((field.confidence || 0) * 100)}%</small></div><button className="text-button" onClick={() => void correctOcr(field)}>Edit</button></div>)}</div></div><div className="modal-actions"><span>Edits are recorded with reviewer provenance.</span><button className="button primary" disabled={busy} onClick={() => void submitDraft(draftId)}>Finalize & get acknowledgement →</button></div></>}</div></div>}
        </section>
      </main>
    </div>
  );
}

function Overview({ dashboard, submissions, reports, releases, renewals, audit, notifications, isOfficer, onOpen, onNavigate, onAdvance }: { dashboard: Dashboard | null; submissions: Submission[]; reports: ReportItem[]; releases: Release[]; renewals: Renewal[]; audit: Audit[]; notifications: NotificationRecord[]; isOfficer: boolean; onOpen: (s: Submission) => void; onNavigate: (page: string) => void; onAdvance: () => void }) {
  const active = reports.filter((item) => item.instrument_status === "ACTIVE" && item.review_status === "ACCEPTED").length;
  const renewed = renewals.filter((item) => item.status === "ACCEPTED").length;
  const released = reports.filter((item) => item.release_status === "COMPLETED").length;
  const stats = dashboard ? [
    ["Total instruments", dashboard.total_submissions, `${active} currently active`, "blue"],
    ["Pending review", dashboard.pending_review, "Awaiting scrutiny action", "amber"],
    ["Approaching maturity", dashboard.approaching_maturity, `${dashboard.matured} matured / due`, "red"],
    ["Pending release", dashboard.pending_releases, `${released} completed · ${renewed} renewed`, "green"],
  ] : [];
  const recent = [...submissions].sort((a, b) => b.submitted_at.localeCompare(a.submitted_at)).slice(0, 6);
  const recentEvents = audit.slice(0, 4);
  return <>
    <div className="stat-grid">{stats.map(([label, value, caption, color]) => <div className="stat-card" key={String(label)}><div className="stat-top"><span>{label}</span><i className={`stat-icon ${color}`}>◈</i></div><strong className="stat-value">{value}</strong><small>{caption}</small></div>)}</div>
    <div className="overview-grid">
      <section className="panel">
        <div className="panel-heading"><div><h2>{isOfficer ? "Priority scrutiny queue" : "Recent instruments"}</h2><p>{isOfficer ? "Latest cases and their current verification and review states" : "Recent submissions and live instrument status"}</p></div><span className="live-indicator"><i /> LIVE QUEUE</span></div>
        {recent.length ? <div className="table-wrap"><table><thead><tr><th>INSTRUMENT</th><th>INSTITUTION</th><th>MATURITY</th><th>VERIFICATION</th><th>REVIEW</th><th /></tr></thead><tbody>{recent.map((s) => <tr key={s.id} onClick={() => onOpen(s)}><td><b>{s.entered_fdr_number}</b><small>{s.id} · {s.application_reference}</small></td><td>{s.institution_id}</td><td>{s.entered_maturity_date}</td><td><Badge>{s.verification_status}</Badge></td><td><Badge>{s.review_status}</Badge></td><td><button className="row-arrow" aria-label={`Open ${s.id}`}>↗</button></td></tr>)}</tbody></table></div> : <div className="empty-state"><span>◈</span><b>No instruments yet</b><p>Submitted instruments will appear here as soon as they are saved.</p></div>}
      </section>
      <aside className="panel side-panel">
        <div className="panel-heading"><div><h2>Release workflow</h2><p>Multi-step authorization queue</p></div><span className="mini-count">{releases.filter((r) => !["COMPLETED", "REJECTED"].includes(r.status)).length}</span></div>
        <div className="release-steps"><div className="step"><span>1</span><div><b>Officer scrutiny</b><small>{releases.filter((r) => r.status === "REQUESTED").length} awaiting recommendation</small></div></div><div className="step"><span>2</span><div><b>Authority decision</b><small>{releases.filter((r) => r.status === "RECOMMENDED").length} awaiting decision</small></div></div><div className="step"><span>3</span><div><b>Bank discharge</b><small>{releases.filter((r) => r.status === "APPROVED_EXECUTION_PENDING").length} awaiting execution evidence</small></div></div></div>
        <div className="clock-card"><div><small>FROZEN DEMO CLOCK</small><b>{dashboard?.display_time || "Loading…"}</b></div>{isOfficer && <button title="Advance demo time" onClick={onAdvance}>＋</button>}</div>
      </aside>
    </div>
    <section className="panel lifecycle-panel"><div className="panel-heading"><div><h2>Lifecycle at a glance</h2><p>Live totals from the instrument register, renewal links, and release queue.</p></div><button className="text-button" onClick={() => onNavigate("reports")}>Open management report →</button></div><div className="lifecycle-grid"><button onClick={() => onNavigate("submissions")}><b>{active}</b><span>Active instruments</span></button><button onClick={() => onNavigate("reports")}><b>{dashboard?.approaching_maturity ?? 0}</b><span>Due within 90 days</span></button><button onClick={() => onNavigate("renewals")}><b>{renewals.filter((item) => item.status === "PENDING").length}</b><span>Renewal links pending</span></button><button onClick={() => onNavigate("releases")}><b>{released}</b><span>Release completed</span></button></div></section>
    <div className="overview-grid">
      <section className="panel status-panel"><div className="panel-heading"><div><h2>Verification status guide</h2><p>Seven distinct outcomes keep bank status and officer action clear.</p></div></div><div className="status-list">{["CONFIRMED", "PARTIAL", "MISMATCH", "NOT_FOUND", "SOURCE_UNAVAILABLE", "MANUAL_REQUIRED", "NOT_INITIATED"].map((item) => <div key={item}><Badge>{item}</Badge><small>{statusDescription(item)}</small></div>)}</div></section>
      <section className="panel activity-panel"><div className="panel-heading"><div><h2>Latest authority actions</h2><p>Recent scrutiny, decision, and release events.</p></div><button className="text-button" onClick={() => onNavigate("audit")}>View audit trail →</button></div>{recentEvents.length ? <div className="activity-list">{recentEvents.map((item) => <button key={item.id} onClick={() => { const submission = submissions.find((row) => row.id === item.entity_id); if (submission) onOpen(submission); else onNavigate("audit"); }}><b>{item.action.replaceAll("_", " ")}</b><span>{item.entity_id} · {item.timestamp}</span></button>)}</div> : <div className="muted-block">Authority actions appear here after an officer or competent authority acts on a case.</div>}</section>
    </div>
    <section className="panel reminder-panel"><div className="panel-heading"><div><h2>Alerts and reminders</h2><p>In-portal maturity, pending-review, discrepancy, and overdue notices.</p></div><span className="mini-count">{notifications.length} alerts</span></div>{notifications.length ? <div className="reminder-list">{[...notifications].sort((a, b) => {
      const priority = (type: string) => type === "OPEN_DISCREPANCY" ? 0 : type === "PENDING_REVIEW" ? 1 : 2;
      return priority(a.deadline_type) - priority(b.deadline_type) || b.scheduled_at.localeCompare(a.scheduled_at);
    }).slice(0, 8).map((item) => <div key={item.id}><span className="reminder-date">{item.due_date}</span><div><b>{item.deadline_type.replaceAll("_", " ")} · {item.submission_id}</b><small>{item.deadline_type === "PENDING_REVIEW" ? "Awaiting officer action" : item.deadline_type === "OPEN_DISCREPANCY" ? "Clarification requires action" : item.offset_days < 0 ? `${Math.abs(item.offset_days)} days overdue` : item.offset_days === 0 ? "Due today" : `${item.offset_days} days before due date`}</small></div><Badge>{item.delivery_status}</Badge></div>)}</div> : <div className="muted-block">No reminders are scheduled. An officer can run the in-portal reminder job to calculate deadlines and pending actions.</div>}</section>
  </>;
}

function statusDescription(status: string) {
  const texts: Record<string, string> = { CONFIRMED: "Matched to the independent source", PARTIAL: "Some fields are unavailable", MISMATCH: "Conflicting values require review", NOT_FOUND: "No authoritative bank record", SOURCE_UNAVAILABLE: "Bank service outage; retry later", MANUAL_REQUIRED: "Branch verification is needed", NOT_INITIATED: "Verification has not started" };
  return texts[status] || status;
}

function SubmissionsPage({ items, role, onOpen, onVerify, onStartReview, onAccept, onReject, onRelease }: { items: Submission[]; role?: string; onOpen: (s: Submission) => void; onVerify: (s: Submission) => void; onStartReview: (s: Submission) => void; onAccept: (s: Submission) => void; onReject: (s: Submission) => void; onRelease: (s: Submission) => void }) {
  const [search, setSearch] = useState("");
  const matches = items.filter((s) => `${s.id} ${s.entered_fdr_number} ${s.institution_id} ${s.application_reference}`.toLowerCase().includes(search.toLowerCase()));
  const visible = matches.slice(0, 8);
  return <section className="panel"><div className="panel-heading list-heading"><div><h2>Instrument register</h2><p>Showing {visible.length} of {matches.length} matching records · access scoped to your role</p></div><input className="search" placeholder="Search reference, institution…" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="table-wrap"><table><thead><tr><th>FDR / CASE</th><th>INSTITUTION</th><th>AMOUNT</th><th>MATURITY</th><th>VERIFICATION</th><th>REVIEW</th><th>ACTIONS</th></tr></thead><tbody>{visible.map((s) => <tr key={s.id}><td><button className="table-link" onClick={() => onOpen(s)}>{s.entered_fdr_number}</button><small>{s.id} · {s.application_reference}</small></td><td>{s.institution_id}</td><td>{s.entered_currency} {Number(s.entered_principal_amount).toLocaleString("en-IN")}</td><td>{s.entered_maturity_date}</td><td><Badge>{s.verification_status}</Badge></td><td><Badge>{s.review_status}</Badge></td><td><div className="action-group">{role === "OFFICER" && s.review_status === "SUBMITTED" && <button className="tiny-button" onClick={() => onStartReview(s)}>Start review</button>}{role === "OFFICER" && <button className="tiny-button" onClick={() => onVerify(s)}>Verify</button>}{role === "OFFICER" && <button className="tiny-button" onClick={() => onAccept(s)}>Accept</button>}{role === "OFFICER" && ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(s.review_status) && <button className="tiny-button danger-button" onClick={() => onReject(s)}>Reject</button>}{role === "COLLEGE" && s.review_status === "ACCEPTED" && <button className="tiny-button" onClick={() => onRelease(s)}>Release / refund</button>}<button className="row-arrow" aria-label={`Open ${s.id}`} onClick={() => onOpen(s)}>↗</button></div></td></tr>)}</tbody></table>{!visible.length && <div className="empty-state"><b>No matching submissions</b><p>Try changing your search.</p></div>}</div></section>;
}

function SubmissionDrawer({ item, role, userId, onClose, onVerify, onUpdate, onStartReview, onAccept, onReject, onRelease, onResponse, onResolve, onIssueQuery, onManual, onOpenDocument }: { item: Submission; role?: string; userId: string; onClose: () => void; onVerify: () => Promise<void>; onUpdate: (submission: Submission) => void; onStartReview: () => void; onAccept: () => void; onReject: () => void; onRelease: () => void; onResponse: (d: Discrepancy) => void; onResolve: (d: Discrepancy) => void; onIssueQuery: () => void; onManual: () => void; onOpenDocument: (document: DocumentRecord) => void }) {
  const [bankResult, setBankResult] = useState<Record<string, unknown> | null>(null);
  const [bankFields, setBankFields] = useState<Record<string, unknown> | null>(() => {
    const verification = item.verifications?.at(-1) as { confirmed_fields_json?: string } | undefined;
    return verification?.confirmed_fields_json ? JSON.parse(verification.confirmed_fields_json) as Record<string, unknown> : null;
  });
  const [loadingBank, setLoadingBank] = useState(false);
  async function loadBank() {
    setLoadingBank(true);
    try {
      const result = await api<{ verification_attempt: Record<string, unknown>; reconciliation: Record<string, unknown> }>(`/api/submissions/${item.id}/verify-bank`, userId, { method: "POST" });
      setBankResult(result);
      const detail = await api<Submission>(`/api/submissions/${item.id}`, userId);
      const lastVerification = detail.verifications?.at(-1) as { confirmed_fields_json?: string } | undefined;
      setBankFields(lastVerification?.confirmed_fields_json ? JSON.parse(lastVerification.confirmed_fields_json) as Record<string, unknown> : null);
      onUpdate(detail);
      await onVerify();
    } catch (e) {
      setBankResult({ error: e instanceof Error ? e.message : "Verification failed" });
    } finally {
      setLoadingBank(false);
    }
  }
  const discrepancies = item.discrepancies || [];
  const fields: [string, string, string][] = [["Bank", bankName(item.entered_bank_id), "bank_id"], ["FDR number", item.entered_fdr_number, "fdr_number"], ["Depositor", item.entered_depositor_name, "depositor_name"], ["Principal amount", `${item.entered_currency} ${item.entered_principal_amount}`, "principal_amount"], ["Issue date", item.entered_issue_date, "issue_date"], ["Maturity date", item.entered_maturity_date, "maturity_date"]];
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div><p className="eyebrow">CASE REVIEW · {item.id}</p><h2>{item.entered_fdr_number}</h2><span>{item.institution_id} · {item.application_reference}</span></div>
          <button className="icon-button" onClick={onClose}>×</button>
        </div>
        <div className="drawer-status"><Badge>{item.verification_status}</Badge><Badge>{item.review_status}</Badge></div>
        <div className="drawer-actions">
          {role === "OFFICER" && item.review_status === "SUBMITTED" && <button className="button secondary" onClick={onStartReview}>Start review</button>}
          {role === "OFFICER" && <button className="button secondary" onClick={() => void loadBank()} disabled={loadingBank}>{loadingBank ? "Checking…" : "↻ Verify with bank service"}</button>}
          {role === "OFFICER" && <button className="button secondary" onClick={onIssueQuery}>Issue clarification query</button>}
          {role === "OFFICER" && ["MANUAL_REQUIRED", "SOURCE_UNAVAILABLE", "PARTIAL"].includes(item.verification_status) && <button className="button secondary" onClick={onManual}>Record manual confirmation</button>}
          {role === "OFFICER" && <button className="button primary" onClick={onAccept}>Accept instrument</button>}
          {role === "OFFICER" && ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(item.review_status) && <button className="button secondary danger-button" onClick={onReject}>Reject with reason</button>}
          {role === "COLLEGE" && item.review_status === "ACCEPTED" && <button className="button primary" onClick={onRelease}>Request release / refund</button>}
        </div>
        {bankResult && <div className="inline-result"><b>Bank result</b><span>{String((bankResult.verification_attempt as Record<string, unknown> | undefined)?.lookup_status || (bankResult as Record<string, unknown>).error || "Updated")}</span><small>{JSON.stringify(bankResult.reconciliation || {})}</small></div>}
        <h3 className="section-title">Submitted data and bank verification</h3>
        <p className="comparison-note">Confirm financial details with manual verification</p>
        <div className="compare-table">
          <div className="compare-header"><span>FIELD</span><span>SUBMITTED</span><span>BANK SERVICE</span></div>
          {fields.map(([label, submitted, key]) => {
            const bank = bankFields?.[key];
            return <div className="compare-row" key={key}><b>{label}</b><span>{submitted}</span><span>{bank == null ? "Not checked" : String(bank)}</span></div>;
          })}
        </div>
        <h3 className="section-title">Discrepancies <span className="inline-count">{discrepancies.filter((d) => !d.resolution).length} open</span></h3>
        {discrepancies.length ? discrepancies.map((d) => <div className="discrepancy-card" key={d.id}>
          <div><Badge tone="mismatch">{d.field}</Badge><b>{d.reason}</b></div>
          <div className="discrepancy-values"><span>Submitted <strong>{d.submitted_value || "—"}</strong></span><span>Document <strong>{d.document_value || "—"}</strong></span><span>Bank <strong>{d.source_value || "—"}</strong></span></div>
          {d.college_response && <p className="response-note">College response: {d.college_response}</p>}
          {role === "COLLEGE" && !d.college_response && <button className="text-button" onClick={() => onResponse(d)}>Respond to query →</button>}
          {role === "OFFICER" && !d.resolution && <button className="text-button" onClick={() => onResolve(d)}>Record resolution →</button>}
          {d.resolution && <p className="response-note">Resolution: {d.resolution}</p>}
        </div>) : <div className="muted-block">No discrepancies recorded for this submission.</div>}
        <h3 className="section-title">Instrument details</h3>
        <div className="detail-grid">{fields.map(([label, value]) => <div key={label}><small>{label}</small><b>{value}</b></div>)}</div>
        {item.documents?.length ? <div className="document-links"><b>Private documents</b>{item.documents.map((doc) => <button className="document-link" key={doc.id} onClick={() => onOpenDocument(doc)}>▧ {doc.filename} <small>{doc.sha256.slice(0, 12)}…</small></button>)}</div> : null}
      </aside>
    </div>
  );
}

function RenewalsPage({ items, submissions, role, onOpen, onCreate }: { items: Renewal[]; submissions: Submission[]; role?: string; onOpen: (s: Submission) => void; onCreate: (s: Submission) => void }) {
  const visibleItems = items.slice(0, 8);
  const candidates = submissions.filter((s) => s.review_status === "ACCEPTED" && s.entered_instrument_status === "ACTIVE").slice(0, 8);
  return <><section className="panel"><div className="panel-heading"><div><h2>Successor linkage</h2><p>Showing {visibleItems.length} of {items.length} links. Predecessors remain active until an officer formally accepts their successor.</p></div></div>{visibleItems.length ? visibleItems.map((item) => <div className="renewal-card" key={item.id}><div className="renewal-instrument"><small>PREDECESSOR</small><button className="table-link" onClick={() => { const found = submissions.find((s) => s.id === item.predecessor?.id); if (found) onOpen(found); }}>{item.predecessor?.id}</button><b>{item.predecessor?.fdr_number}</b><span>Matures {item.predecessor?.maturity_date}</span><Badge>{item.predecessor?.review_status}</Badge></div><div className="renewal-arrow">→<small>successor</small></div><div className="renewal-instrument successor"><small>PROPOSED SUCCESSOR</small><button className="table-link" onClick={() => { const found = submissions.find((s) => s.id === item.successor?.id); if (found) onOpen(found); }}>{item.successor?.id || "Pending"}</button><b>{item.successor?.fdr_number || "Not submitted"}</b><span>Matures {item.successor?.maturity_date || "—"}</span><Badge>{item.status}</Badge></div></div>) : <div className="empty-state"><span>⟳</span><b>No successor links yet</b><p>Link a new instrument to an accepted predecessor.</p></div>}</section>{role === "COLLEGE" && <section className="panel"><div className="panel-heading"><div><h2>Eligible predecessors</h2><p>Showing up to 8 active accepted instruments. Create a successor draft linked to an accepted FDR.</p></div></div><div className="eligible-list">{candidates.map((s) => <div key={s.id}><div><b>{s.id} · {s.entered_fdr_number}</b><small>{s.entered_principal_amount} INR · maturity {s.entered_maturity_date}</small></div><button className="button secondary" onClick={() => onCreate(s)}>＋ Start renewal</button></div>)}</div></section>}</>;
}

function ReleaseTimeline({ item }: { item: Release }) {
  const stages = [
    { key: "REQUESTED", title: "Requested", detail: item.reason, at: item.requested_at },
    { key: "RECOMMENDED", title: "Recommended", detail: item.officer_recommendation || "Officer scrutiny has not been recorded.", at: item.recommended_at },
    { key: "APPROVED_EXECUTION_PENDING", title: "Approved execution pending", detail: item.decision_reason || (item.authority_decision ? item.authority_decision : "Competent authority decision has not been recorded."), at: item.approved_at },
    { key: "COMPLETED", title: "Completed", detail: item.execution_reference ? `Bank discharge reference: ${item.execution_reference}` : "Formal bank discharge evidence is required to complete the release.", at: item.executed_at },
  ];
  const stopped = ["RETURNED", "REJECTED"].includes(item.status);
  const progressIndex = item.status === "COMPLETED" ? 3
    : item.status === "APPROVED_EXECUTION_PENDING" ? 2
      : item.status === "RECOMMENDED" ? 1
        : stopped ? (item.authority_decision ? 2 : 1) : 0;
  const [activeStage, setActiveStage] = useState(progressIndex);
  useEffect(() => setActiveStage(progressIndex), [progressIndex]);
  const selected = stages[activeStage];
  return <div className={`release-timeline ${stopped ? "is-stopped" : ""}`}>
    <div className="timeline-steps" role="tablist" aria-label={`Release milestones for ${item.id}`}>
      {stages.map((stage, index) => {
        const complete = stopped ? index < progressIndex : index <= progressIndex;
        const isStopped = stopped && index === progressIndex;
        return <button type="button" role="tab" aria-selected={activeStage === index} aria-label={`${stage.title}${complete ? ", complete" : isStopped ? `, ${item.status.toLowerCase()}` : ", pending"}`} className={`timeline-step ${complete ? "complete" : ""} ${activeStage === index ? "selected" : ""} ${isStopped ? "stopped" : ""}`} key={stage.key} onClick={() => setActiveStage(index)}>
          <i>{complete ? "✓" : isStopped ? "!" : index + 1}</i><span>{stage.title}</span>
        </button>;
      })}
    </div>
    <div className="timeline-detail" role="tabpanel"><b>{selected.title}</b><span>{selected.detail}</span><small>{selected.at ? new Date(selected.at).toLocaleString() : stopped ? `Workflow ${item.status.toLowerCase()}` : "Awaiting this milestone"}</small></div>
  </div>;
}

function ReleasesPage({ items, role, submissions, onOpen, onReview, onDecide, onExecute }: { items: Release[]; role?: string; submissions: Submission[]; onOpen: (s: Submission) => void; onReview: (r: Release) => void; onDecide: (r: Release) => void; onExecute: (r: Release) => void }) {
  const visible = items.slice(0, 8);
  return <section className="panel"><div className="panel-heading"><div><h2>Multi-step release and refund</h2><p>Showing {visible.length} of {items.length} requests. Each transition requires the appropriate role and recorded evidence.</p></div><span className="live-indicator"><i /> {items.length} REQUESTS</span></div>{visible.length ? <div className="release-list">{visible.map((item) => <article className="release-card" key={item.id}><div className="release-card-top"><div><small>{item.id} · <button className="table-link" onClick={() => { const submission = submissions.find((row) => row.id === item.submission_id); if (submission) onOpen(submission); }}>{item.submission_id}</button> · {item.request_type}</small><h3>{item.reason}</h3></div><Badge>{item.status}</Badge></div><ReleaseTimeline item={item} />{item.status === "RETURNED" && <p className="workflow-note"><b>Returned:</b> {item.decision_reason || item.officer_recommendation}</p>}{item.status === "REJECTED" && <p className="workflow-note"><b>Rejected:</b> {item.decision_reason}</p>}<div className="release-actions">{role === "OFFICER" && item.status === "REQUESTED" && <button className="button secondary" onClick={() => onReview(item)}>Recommend / review</button>}{role === "APPROVER" && item.status === "RECOMMENDED" && <button className="button primary" onClick={() => onDecide(item)}>Record authority decision</button>}{role === "OFFICER" && item.status === "APPROVED_EXECUTION_PENDING" && <button className="button primary" onClick={() => onExecute(item)}>Record bank discharge</button>}</div></article>)}</div> : <div className="empty-state"><span>⇧</span><b>No release requests</b><p>Release requests from institutions appear here for review.</p></div>}</section>;
}

type ReportAnalysis = {
  generatedAt: string;
  records: ReportItem[];
  total: number;
  active: number;
  pending: number;
  expiring: number;
  matured: number;
  renewed: number;
  released: number;
  discrepancies: number;
};

function createPortfolioAnalysis(items: ReportItem[]): ReportAnalysis {
  return {
    generatedAt: new Date().toISOString(),
    records: items,
    total: items.length,
    active: items.filter((item) => item.instrument_status === "ACTIVE" && item.review_status === "ACCEPTED").length,
    pending: items.filter((item) => ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(item.review_status)).length,
    expiring: items.filter((item) => item.review_status === "ACCEPTED" && item.instrument_status === "ACTIVE" && item.days_to_maturity !== null && item.days_to_maturity >= 0 && item.days_to_maturity <= 90).length,
    matured: items.filter((item) => item.review_status === "ACCEPTED" && item.instrument_status === "ACTIVE" && item.days_to_maturity !== null && item.days_to_maturity <= 0).length,
    renewed: new Set(items.filter((item) => item.renewal_status === "ACCEPTED").map((item) => item.renewal_id).filter(Boolean)).size,
    released: items.filter((item) => item.release_status === "COMPLETED").length,
    discrepancies: items.reduce((total, item) => total + item.active_discrepancies, 0),
  };
}

function makePortfolioPdf(analysis: ReportAnalysis) {
  const money = (value: string) => `INR ${Number(value).toLocaleString("en-IN")}`;
  const lines = [
    "AICTE SECURITY DEPOSIT / FDR PORTFOLIO REPORT",
    `Generated at: ${analysis.generatedAt}`,
    "This report summarizes portal fields and workflow states; validate with authoritative records.",
    "",
    "PORTFOLIO SUMMARY",
    `Records: ${analysis.total} | Active: ${analysis.active} | Pending review: ${analysis.pending}`,
    `Due within 90 days: ${analysis.expiring} | Matured: ${analysis.matured} | Open discrepancies: ${analysis.discrepancies}`,
    `Accepted renewals: ${analysis.renewed} | Completed releases: ${analysis.released}`,
    "",
    "INSTRUMENT REGISTER",
    ...analysis.records.flatMap((item) => [
      `${item.submission_id} | ${item.fdr_number} | ${item.institution_id} | ${money(item.amount)}`,
      `Review: ${item.review_status} | Verification: ${item.verification_status} | Maturity: ${item.maturity_date} | Open issues: ${item.active_discrepancies}`,
    ]),
  ];
  const wrapped = lines.flatMap((line) => line.match(/.{1,88}(\s|$)/g)?.map((part) => part.trimEnd()) || [""]);
  const pages: string[][] = [];
  for (let index = 0; index < wrapped.length; index += 48) pages.push(wrapped.slice(index, index + 48));
  if (!pages.length) pages.push(["No matching records."]);
  const escape = (value: string) => value.replace(/[^\x20-\x7E]/g, "?").replace(/([\\()])/g, "\\$1");
  const objects: string[] = [];
  objects[1] = "<< /Type /Catalog /Pages 2 0 R >>";
  objects[2] = `<< /Type /Pages /Kids [${pages.map((_, index) => `${4 + index * 2} 0 R`).join(" ")}] /Count ${pages.length} >>`;
  objects[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>";
  pages.forEach((page, index) => {
    const pageId = 4 + index * 2;
    const streamId = pageId + 1;
    const commands = ["BT", "/F1 9 Tf", "50 750 Td", "13 TL", ...page.flatMap((line) => [`(${escape(line)}) Tj`, "T*"]), "ET"].join("\n");
    objects[pageId] = `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents ${streamId} 0 R >>`;
    objects[streamId] = `<< /Length ${commands.length} >>\nstream\n${commands}\nendstream`;
  });
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  for (let id = 1; id < objects.length; id++) {
    offsets[id] = pdf.length;
    pdf += `${id} 0 obj\n${objects[id]}\nendobj\n`;
  }
  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length}\n0000000000 65535 f \n`;
  for (let id = 1; id < objects.length; id++) pdf += `${String(offsets[id]).padStart(10, "0")} 00000 n \n`;
  pdf += `trailer\n<< /Size ${objects.length} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  return new Blob([pdf], { type: "application/pdf" });
}

function ReportsPage({ items, userId, onOpen }: { items: ReportItem[]; userId: string; onOpen: (submissionId: string) => void }) {
  const [filter, setFilter] = useState("ALL");
  const [exportError, setExportError] = useState("");
  const [analysis, setAnalysis] = useState<ReportAnalysis | null>(null);
  const [generating, setGenerating] = useState(false);
  const [analysisNotice, setAnalysisNotice] = useState("");
  const filtered = items.filter((item) => filter === "ALL"
    || (filter === "DISCREPANCIES" ? item.active_discrepancies > 0
      : filter === "MATURITY" ? item.days_to_maturity !== null && item.days_to_maturity <= 90
        : filter === "ACTIVE" ? item.instrument_status === "ACTIVE"
          : filter === "RENEWED" ? item.renewal_status === "ACCEPTED"
            : filter === "RELEASED" ? item.release_status === "COMPLETED"
              : filter === "PENDING" ? ["SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"].includes(item.review_status)
                : item.verification_status === filter));
  const visible = filtered.slice(0, 8);
  const counts = createPortfolioAnalysis(items);
  async function generateReport() {
    setGenerating(true);
    setAnalysisNotice("");
    await new Promise((resolve) => window.setTimeout(resolve, 2000 + Math.floor(Math.random() * 2001)));
    setAnalysis(createPortfolioAnalysis(filtered));
    setGenerating(false);
    setAnalysisNotice("Portfolio analysis is ready. This is based on portal fields and workflow states; no OCR was performed.");
  }
  function downloadPdf() {
    if (!analysis) return;
    const url = URL.createObjectURL(makePortfolioPdf(analysis));
    const link = document.createElement("a");
    link.href = url;
    link.download = "aicte-fdr-portfolio-report.pdf";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function openWhatsApp() {
    if (!analysis) return;
    const confirmed = window.confirm("Open WhatsApp to +91 9137397557? Only portfolio-level counts will be prefilled. The PDF is not attached automatically; verify the recipient and attach it manually only if authorized.");
    if (!confirmed) return;
    const reminder = analysis.matured > 0
      ? `Action reminder: review ${analysis.matured} matured instrument(s).`
      : analysis.expiring > 0
        ? `Action reminder: review ${analysis.expiring} instrument(s) due within 90 days.`
        : analysis.discrepancies > 0
          ? `Action reminder: resolve ${analysis.discrepancies} open discrepancy/discrepancies.`
          : "No maturity or discrepancy action is currently indicated in this report.";
    const message = `AICTE FDR portfolio report prepared: ${analysis.total} records, ${analysis.pending} pending review, ${analysis.expiring} due within 90 days, and ${analysis.discrepancies} open discrepancies. ${reminder} I will attach the PDF after confirming this recipient is authorized.`;
    window.open(`https://wa.me/919137397557?text=${encodeURIComponent(message)}`, "_blank", "noopener,noreferrer");
  }
  async function exportCsv() {
    setExportError("");
    try {
      const response = await fetch(`${API}/api/reports/export.csv`, { headers: { "X-Demo-User-Id": userId } });
      if (!response.ok) throw new Error("Report export was denied.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "aicte-fdr-report.csv";
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) {
      setExportError(e instanceof Error ? e.message : "Report export failed.");
    }
  }
  return <><section className="panel"><div className="panel-heading list-heading"><div><h2>Portfolio report</h2><p>Showing {visible.length} of {filtered.length} matching instruments · maturity, verification, renewal, and release status</p></div><div className="report-actions"><select className="search" value={filter} onChange={(e) => { setFilter(e.target.value); setAnalysis(null); }}><option value="ALL">All records</option><option value="PENDING">Pending review</option><option value="ACTIVE">Active instruments</option><option value="MATURITY">Maturing within 90 days / overdue</option><option value="RENEWED">Renewed</option><option value="RELEASED">Released</option><option value="DISCREPANCIES">Open discrepancies</option><option value="MISMATCH">Mismatches</option><option value="SOURCE_UNAVAILABLE">Bank unavailable</option><option value="MANUAL_REQUIRED">Manual required</option></select><button className="button secondary" onClick={() => void exportCsv()}>↓ Export CSV</button><button className="button primary" onClick={() => void generateReport()} disabled={generating}>{generating ? "Preparing analysis…" : "Generate report"}</button></div></div><div className="report-summary-grid"><div><b>{counts.active}</b><span>Active</span></div><div><b>{counts.expiring}</b><span>Due within 90 days</span></div><div><b>{counts.matured}</b><span>Matured</span></div><div><b>{counts.renewed}</b><span>Renewed</span></div><div><b>{counts.released}</b><span>Released</span></div><div><b>{counts.pending}</b><span>Pending review</span></div></div>{exportError && <p className="audit-reason">{exportError}</p>}{analysisNotice && <div className="mock-notice"><b>Analysis ready</b><span>{analysisNotice}</span></div>}{analysis && <div className="analysis-result"><div><b>Management analysis</b><span>Generated {new Date(analysis.generatedAt).toLocaleString()} · {analysis.total} records in the current view</span></div><p>{analysis.pending} pending review · {analysis.expiring} due within 90 days · {analysis.matured} matured · {analysis.discrepancies} open discrepancies · {analysis.renewed} accepted renewals · {analysis.released} completed releases.</p><div className="report-actions"><button className="button secondary" onClick={downloadPdf}>↓ Download PDF</button><button className="button secondary" onClick={openWhatsApp}>Share summary on WhatsApp</button><small>WhatsApp cannot attach files from this page; download the report and attach it yourself after checking recipient authorization.</small></div></div>}<div className="table-wrap"><table><thead><tr><th>CASE</th><th>INSTITUTION</th><th>AMOUNT</th><th>REVIEW</th><th>VERIFICATION</th><th>INSTRUMENT</th><th>MATURITY</th><th>DAYS</th><th>RENEWAL</th><th>RELEASE</th><th>OPEN ISSUES</th></tr></thead><tbody>{visible.map((item) => <tr className="clickable-row" key={item.submission_id} tabIndex={0} role="link" aria-label={`Open report details for ${item.submission_id}`} onClick={() => onOpen(item.submission_id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onOpen(item.submission_id); } }}><td><b>{item.submission_id}</b><small>{item.fdr_number}</small></td><td>{item.institution_id}</td><td>INR {Number(item.amount).toLocaleString("en-IN")}</td><td><Badge>{item.review_status}</Badge></td><td><Badge>{item.verification_status}</Badge></td><td><Badge>{item.instrument_status}</Badge></td><td>{item.maturity_date}</td><td className={item.days_to_maturity !== null && item.days_to_maturity <= 30 ? "urgent-text" : ""}>{item.days_to_maturity ?? "—"}</td><td>{item.renewal_status ? <Badge>{item.renewal_status}</Badge> : "—"}</td><td>{item.release_status ? <Badge>{item.release_status}</Badge> : "—"}</td><td>{item.active_discrepancies}</td></tr>)}</tbody></table></div></section><div className="report-footnote">CSV fields beginning with <code>=</code>, <code>@</code>, <code>+</code>, or <code>-</code> are neutralized to reduce spreadsheet formula injection risk.</div></>;
}

function AuditPage({ items }: { items: Audit[] }) {
  const [search, setSearch] = useState("");
  const matches = items.filter((item) => `${item.action} ${item.actor_id} ${item.entity_id}`.toLowerCase().includes(search.toLowerCase()));
  const visible = matches.slice(0, 8);
  return <section className="panel"><div className="panel-heading list-heading"><div><h2>Append-only authority action log</h2><p>Showing {visible.length} of {matches.length} matching actions · officer and authority actions with actor, UTC time, entity, and before / after states. Draft-only activity is excluded.</p></div><input className="search" placeholder="Filter action, actor, entity…" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="audit-list">{visible.map((item) => <article className="audit-row" key={item.id}><div className="audit-marker" /><div className="audit-main"><div className="audit-title"><b>{item.action.replaceAll("_", " ")}</b><span>{item.timestamp}</span></div><p><strong>{item.actor_id}</strong> · {item.entity_type} / {item.entity_id}</p><div className="audit-states"><div><small>BEFORE STATE</small><code>{displayAuditState(item.before_state)}</code></div><div><small>AFTER STATE</small><code>{displayAuditState(item.after_state)}</code></div></div>{item.reason && <small className="audit-reason">Reason: {item.reason}</small>}</div></article>)}</div>{!visible.length && <div className="empty-state">No authority actions match this filter.</div>}</section>;
}
