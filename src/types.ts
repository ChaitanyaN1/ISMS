export interface AuthUser {
  user_id: string;
  username: string;
  full_name: string;
  email: string;
  role: 'Admin' | 'Auditor' | 'Risk Owner' | 'Viewer' | string;
  last_login?: string;
}

export interface AuditRecord {
  audit_id: string;
  title: string;
  organization: string;
  department: string;
  audit_type: string;
  status: 'Planned' | 'In Progress' | 'Completed' | 'Closed' | string;
  audit_date: string;
  start_date: string;
  end_date: string;
  lead_auditor: string;
  audit_team: string;
  created_by: string;
  scope: string;
  objectives: string;
  compliance: number | null;
  approval_status: 'Draft' | 'In Review' | 'Approved' | 'Changes Requested' | string;
  approved_by: string;
  approved_at: string;
  report_version: string;
  approval_notes: string;
  record_type: 'DEMO' | 'USER' | string;
}

export interface ControlTestRecord {
  test_id: string;
  audit_id: string;
  control_id: string;
  control_title: string;
  domain: string;
  procedure: string;
  sample_size: number;
  status: 'Compliant' | 'Partially Compliant' | 'Non-Compliant' | 'Not Applicable' | 'Not Tested' | string;
  auditor_notes: string;
  evidence_ref: string;
  tested_by: string;
  tested_at: string;
  record_type: string;
}

export interface FindingRecord {
  finding_id: string;
  audit_id: string;
  control_id: string;
  title: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | string;
  status: 'Open' | 'In Remediation' | 'Resolved' | 'Closed' | string;
  affected_asset: string;
  criteria: string;
  condition: string;
  cause: string;
  impact: string;
  recommendation: string;
  owner: string;
  found_date: string;
  due_date: string;
  record_type: string;
}

export interface ActionRecord {
  action_id: string;
  finding_id: string;
  title: string;
  action_type: string;
  owner: string;
  due_date: string;
  status: 'Open' | 'In Progress' | 'Completed' | 'Verified' | string;
  corrective_action: string;
  preventive_action: string;
  verification_notes: string;
  evidence_notes: string;
  record_type: string;
}

export interface ControlSoARecord {
  control_id: string;
  domain: string;
  title: string;
  description: string;
  applicability: 'Applicable' | 'Not Applicable' | string;
  implementation_status: 'Implemented' | 'Partially Implemented' | 'Not Implemented' | 'Not Applicable' | string;
  justification: string;
  owner: string;
  nist_csf: string;
  soc2: string;
  record_type: string;
}

export interface RiskRecord {
  risk_id: string;
  title: string;
  asset: string;
  threat: string;
  likelihood: number;
  impact: number;
  inherent_score: number;
  treatment: string;
  linked_controls: string;
  residual_score: number;
  owner: string;
  status: string;
  record_type: string;
}

export interface RequirementRecord {
  req_id: string;
  framework: string;
  reference: string;
  requirement_summary: string;
  mapped_controls: string;
  status: string;
  notes: string;
  record_type: string;
}

export interface EvidenceRecord {
  evidence_id: string;
  title: string;
  entity_type: string;
  entity_id: string;
  audit_id: string;
  control_id: string;
  file_name: string;
  stored_path: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  uploaded_by: string;
  uploaded_at: string;
  verified_status: string;
  notes: string;
  record_type: string;
}

export interface AuditLogEntry {
  log_id: number;
  timestamp: string;
  actor: string;
  role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: string;
  prev_hash: string;
  entry_hash: string;
}

export interface UserAccountRow {
  user_id: string;
  username: string;
  full_name: string;
  email: string;
  role: string;
  failed_attempts: number;
  locked_until: string;
  is_active: number;
  created_at: string;
  last_login: string;
  record_type: string;
}

export interface ClauseItem {
  clause_id: string;
  section: string;
  title: string;
  summary: string;
  amendment_2024: string;
}

export interface WorkspaceSnapshot {
  audits: AuditRecord[];
  tests: ControlTestRecord[];
  findings: FindingRecord[];
  actions: ActionRecord[];
  controls: ControlSoARecord[];
  risks: RiskRecord[];
  requirements: RequirementRecord[];
  evidence: EvidenceRecord[];
  audit_logs: AuditLogEntry[];
  users: UserAccountRow[];
  clauses: ClauseItem[];
  log_chain: {
    valid: boolean;
    checked_entries: number;
    broken_log_id: number | null;
    head_hash: string;
  };
}

export type AppView =
  | 'landing'
  | 'login'
  | 'dashboard'
  | 'audits'
  | 'audit-detail'
  | 'new-audit'
  | 'findings'
  | 'controls-soa'
  | 'risks'
  | 'evidence'
  | 'reports'
  | 'users'
  | 'settings'
  | 'legal-privacy'
  | 'legal-terms'
  | 'not-found';
