# AICTE FDR Prototype — Single-file Development Handoff

Version 1.0 | Synthetic dataset | Frozen demo clock: 26 October 2026, 10:00 IST

## 1. Instructions to the development agent

Build only the Security Deposit/FDR Management Portal described here. This file contains complete seed data, a document-fixture generator, a mock bank verification contract, expected scenarios and implementation acceptance checks. Extract the labelled code blocks into their named files. No private data or live financial credentials are included.

All names, institutions, banks and instruments are fictional. Every generated document must carry SYNTHETIC - FOR PROTOTYPE ONLY. Bank verification in this package is simulated. Never present it as a live bank confirmation. No actual AICTE amounts, release conditions or deadlines are established by these examples.

### Required scope
- College and AICTE workspaces; college, officer and competent-authority permissions.
- Institution/instrument repository; secure document upload and version history.
- Actual OCR execution on uploaded images/PDFs, editable extracted fields, confidence/review flags and page evidence.
- Independent mock bank lookup, field comparison, source timestamps, discrepancies and manual confirmation fallback.
- Maturity/validity monitoring, configurable reminders and overdue escalation.
- Linked renewal/replacement history; release/discharge/refund review, authorization and execution tracking.
- Dashboards, search, reports and append-only action history.
- No money movement, public signup, AI forgery verdicts or wider approval-process automation.

### Dataset size
10 colleges; 3 fictional banks; 12 identity fixtures; 30 submissions/scenarios; 29 document manifests; 28 bank rows; 2 historical verification examples; 3 release cases. One bank reference is intentionally absent and another submission intentionally repeats an existing reference. The manifest contains exact ground truth, not fabricated OCR output.

### Seed interpretation
All submissions begin SUBMITTED/NOT_INITIATED for replay. Historical verification and release examples are independent related records: derive their badges separately; do not silently treat those cases as fully accepted. Submitted successor is not accepted automatically. A completed release fixture has prior authorization; replay its transitions or show the related request history.

## 2. Bootstrap procedure
1. Save the next JSON block as seed.json.
2. Save the generator block as generate_fixtures.py in the same directory.
3. Install Pillow and run `python generate_fixtures.py`.
4. Import seed.json into appropriate relational tables; keep bank_records in the mock bank service/database, outside college write permissions.
5. Import generated documents and manifest paths into private document storage. Generate actual file hashes during import.
6. Provision test identities using the authentication provider. User rows are identity fixtures, not login credentials. Map generated auth IDs to fixture IDs; never expose privileged keys in the browser.
7. Run OCR against generated images, then compare against ground_truth for evaluation. Never read ground_truth as though it were OCR output.
8. Start the mock verification endpoint and replay test_cases with the frozen clock.

Pillow is used only to render synthetic documents; it is not an OCR model. OCR model/runtime installation is a separate dependency.

## 3. Complete seed dataset — seed.json

```json
{
  "meta": {
    "dataset_version": "1.0",
    "synthetic": true,
    "demo_now": "2026-10-26T04:30:00Z",
    "display_timezone": "Asia/Kolkata",
    "notes": "All institutions, banks, references and amounts are fictitious. No real AICTE policy is encoded."
  },
  "institutions": [
    {
      "id": "INST-001",
      "name": "College A (Synthetic)",
      "region": "North",
      "email": "college1@example.invalid",
      "representative_user_id": "USER-C01"
    },
    {
      "id": "INST-002",
      "name": "College B (Synthetic)",
      "region": "South",
      "email": "college2@example.invalid",
      "representative_user_id": "USER-C02"
    },
    {
      "id": "INST-003",
      "name": "College C (Synthetic)",
      "region": "East",
      "email": "college3@example.invalid",
      "representative_user_id": "USER-C03"
    },
    {
      "id": "INST-004",
      "name": "College D (Synthetic)",
      "region": "West",
      "email": "college4@example.invalid",
      "representative_user_id": "USER-C04"
    },
    {
      "id": "INST-005",
      "name": "College E (Synthetic)",
      "region": "North",
      "email": "college5@example.invalid",
      "representative_user_id": "USER-C05"
    },
    {
      "id": "INST-006",
      "name": "College F (Synthetic)",
      "region": "South",
      "email": "college6@example.invalid",
      "representative_user_id": "USER-C06"
    },
    {
      "id": "INST-007",
      "name": "College G (Synthetic)",
      "region": "East",
      "email": "college7@example.invalid",
      "representative_user_id": "USER-C07"
    },
    {
      "id": "INST-008",
      "name": "College H (Synthetic)",
      "region": "West",
      "email": "college8@example.invalid",
      "representative_user_id": "USER-C08"
    },
    {
      "id": "INST-009",
      "name": "College I (Synthetic)",
      "region": "North",
      "email": "college9@example.invalid",
      "representative_user_id": "USER-C09"
    },
    {
      "id": "INST-010",
      "name": "College J (Synthetic)",
      "region": "South",
      "email": "college10@example.invalid",
      "representative_user_id": "USER-C10"
    }
  ],
  "banks": [
    {
      "id": "DEMO-BANK-01",
      "name": "Synthetic Bank 1",
      "branch": "Demo Branch 1",
      "verification_endpoint": "/mock-bank/v1/fdr-verifications",
      "environment": "MOCK"
    },
    {
      "id": "DEMO-BANK-02",
      "name": "Synthetic Bank 2",
      "branch": "Demo Branch 2",
      "verification_endpoint": "/mock-bank/v1/fdr-verifications",
      "environment": "MOCK"
    },
    {
      "id": "DEMO-BANK-03",
      "name": "Synthetic Bank 3",
      "branch": "Demo Branch 3",
      "verification_endpoint": "/mock-bank/v1/fdr-verifications",
      "environment": "MOCK"
    }
  ],
  "users": [
    {
      "id": "USER-C01",
      "email": "college1@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-001"
    },
    {
      "id": "USER-C02",
      "email": "college2@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-002"
    },
    {
      "id": "USER-C03",
      "email": "college3@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-003"
    },
    {
      "id": "USER-C04",
      "email": "college4@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-004"
    },
    {
      "id": "USER-C05",
      "email": "college5@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-005"
    },
    {
      "id": "USER-C06",
      "email": "college6@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-006"
    },
    {
      "id": "USER-C07",
      "email": "college7@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-007"
    },
    {
      "id": "USER-C08",
      "email": "college8@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-008"
    },
    {
      "id": "USER-C09",
      "email": "college9@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-009"
    },
    {
      "id": "USER-C10",
      "email": "college10@example.invalid",
      "role": "COLLEGE",
      "institution_id": "INST-010"
    },
    {
      "id": "USER-O01",
      "email": "officer@example.invalid",
      "role": "OFFICER",
      "institution_id": null
    },
    {
      "id": "USER-A01",
      "email": "authority@example.invalid",
      "role": "APPROVER",
      "institution_id": null
    }
  ],
  "submissions": [
    {
      "id": "SUB-001",
      "institution_id": "INST-001",
      "scenario": "MATCH",
      "application_reference": "DEMO-APP-INST-001",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000001",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-001"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-002",
      "institution_id": "INST-002",
      "scenario": "AMOUNT_MISMATCH",
      "application_reference": "DEMO-APP-INST-002",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000002",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1500000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-002"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-003",
      "institution_id": "INST-003",
      "scenario": "MATURITY_MISMATCH",
      "application_reference": "DEMO-APP-INST-003",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000003",
        "depositor_name": "College C (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2028-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-003"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-004",
      "institution_id": "INST-004",
      "scenario": "NAME_MISMATCH",
      "application_reference": "DEMO-APP-INST-004",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000004",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-004"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-005",
      "institution_id": "INST-005",
      "scenario": "NOT_FOUND",
      "application_reference": "DEMO-APP-INST-005",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000005",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-005"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-006",
      "institution_id": "INST-006",
      "scenario": "SOURCE_UNAVAILABLE",
      "application_reference": "DEMO-APP-INST-006",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000006",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-006"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-007",
      "institution_id": "INST-007",
      "scenario": "PARTIAL_RESPONSE",
      "application_reference": "DEMO-APP-INST-007",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000007",
        "depositor_name": "College G (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": null,
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-007"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-008",
      "institution_id": "INST-008",
      "scenario": "CLOSED",
      "application_reference": "DEMO-APP-INST-008",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000008",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "CLOSED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-008"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-009",
      "institution_id": "INST-009",
      "scenario": "MATURED",
      "application_reference": "DEMO-APP-INST-009",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000009",
        "depositor_name": "College I (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-16",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-009"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-010",
      "institution_id": "INST-010",
      "scenario": "DUE_90",
      "application_reference": "DEMO-APP-INST-010",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000010",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-01-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-010"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-011",
      "institution_id": "INST-001",
      "scenario": "DUE_60",
      "application_reference": "DEMO-APP-INST-001",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000011",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-12-25",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-011"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-012",
      "institution_id": "INST-002",
      "scenario": "DUE_30",
      "application_reference": "DEMO-APP-INST-002",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000012",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-11-25",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-012"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-013",
      "institution_id": "INST-003",
      "scenario": "DUE_7",
      "application_reference": "DEMO-APP-INST-003",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000013",
        "depositor_name": "College C (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-11-02",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-013"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-014",
      "institution_id": "INST-004",
      "scenario": "DUE_1",
      "application_reference": "DEMO-APP-INST-004",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000014",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-27",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-014"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-015",
      "institution_id": "INST-005",
      "scenario": "DUE_TODAY",
      "application_reference": "DEMO-APP-INST-005",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000015",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-26",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-015"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-016",
      "institution_id": "INST-006",
      "scenario": "OVERDUE",
      "application_reference": "DEMO-APP-INST-006",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000016",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-18",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-016"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": "2026-10-18",
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": true
    },
    {
      "id": "SUB-017",
      "institution_id": "INST-007",
      "scenario": "MISSING_DOCUMENT",
      "application_reference": "DEMO-APP-INST-007",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000017",
        "depositor_name": "College G (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-018",
      "institution_id": "INST-008",
      "scenario": "UNREADABLE",
      "application_reference": "DEMO-APP-INST-008",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000018",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-018"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-019",
      "institution_id": "INST-001",
      "scenario": "DUPLICATE",
      "application_reference": "DEMO-APP-INST-001",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000001",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-019"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-020",
      "institution_id": "INST-010",
      "scenario": "AMBIGUOUS_DATE",
      "application_reference": "DEMO-APP-INST-010",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000020",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": null,
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-020"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-021",
      "institution_id": "INST-001",
      "scenario": "LEADING_ZERO",
      "application_reference": "DEMO-APP-INST-001",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "00000021",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-021"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-022",
      "institution_id": "INST-002",
      "scenario": "RENEWAL_OLD",
      "application_reference": "DEMO-APP-INST-002",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000022",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-23",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-022"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": true
    },
    {
      "id": "SUB-023",
      "institution_id": "INST-002",
      "scenario": "RENEWAL_NEW",
      "application_reference": "DEMO-APP-INST-002",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000023",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-023"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": "SUB-022",
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": true
    },
    {
      "id": "SUB-024",
      "institution_id": "INST-004",
      "scenario": "RELEASE_REQUESTED",
      "application_reference": "DEMO-APP-INST-004",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000024",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-024"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-025",
      "institution_id": "INST-005",
      "scenario": "RELEASE_APPROVED",
      "application_reference": "DEMO-APP-INST-005",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000025",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-025"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-026",
      "institution_id": "INST-006",
      "scenario": "RELEASE_COMPLETED",
      "application_reference": "DEMO-APP-INST-006",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000026",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-026"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-027",
      "institution_id": "INST-007",
      "scenario": "MANUAL_PENDING",
      "application_reference": "DEMO-APP-INST-007",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000027",
        "depositor_name": "College G (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-027"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-028",
      "institution_id": "INST-008",
      "scenario": "MANUAL_CONFIRMED",
      "application_reference": "DEMO-APP-INST-008",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000028",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-028"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-029",
      "institution_id": "INST-009",
      "scenario": "LIEN_MISMATCH",
      "application_reference": "DEMO-APP-INST-009",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000029",
        "depositor_name": "College I (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-029"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    },
    {
      "id": "SUB-030",
      "institution_id": "INST-010",
      "scenario": "STALE_CONFIRMATION",
      "application_reference": "DEMO-APP-INST-010",
      "instrument_type": "FDR",
      "entered_fields": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000030",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "document_ids": [
        "DOC-030"
      ],
      "submitted_at": "2026-10-26T03:30:00Z",
      "assigned_officer_id": "USER-O01",
      "review_status": "SUBMITTED",
      "verification_status": "NOT_INITIATED",
      "renewal_due_date": null,
      "document_valid_until": null,
      "predecessor_submission_id": null,
      "required_document_types": [
        "FDR"
      ],
      "demo_renewal_required": false
    }
  ],
  "documents": [
    {
      "id": "DOC-001",
      "submission_id": "SUB-001",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-001",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000001",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-002",
      "submission_id": "SUB-002",
      "type": "FDR",
      "layout_id": "L2",
      "variant": "rotated",
      "file_stem": "DOC-002",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000002",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1500000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-003",
      "submission_id": "SUB-003",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "low_contrast",
      "file_stem": "DOC-003",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000003",
        "depositor_name": "College C (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-004",
      "submission_id": "SUB-004",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-004",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000004",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-005",
      "submission_id": "SUB-005",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-005",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000005",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-006",
      "submission_id": "SUB-006",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-006",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000006",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-007",
      "submission_id": "SUB-007",
      "type": "FDR",
      "layout_id": "L2",
      "variant": "rotated",
      "file_stem": "DOC-007",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000007",
        "depositor_name": "College G (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": null,
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-008",
      "submission_id": "SUB-008",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "low_contrast",
      "file_stem": "DOC-008",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000008",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "CLOSED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-009",
      "submission_id": "SUB-009",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-009",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000009",
        "depositor_name": "College I (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-16",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-010",
      "submission_id": "SUB-010",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-010",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000010",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-01-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-011",
      "submission_id": "SUB-011",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-011",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000011",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-12-25",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-012",
      "submission_id": "SUB-012",
      "type": "FDR",
      "layout_id": "L2",
      "variant": "rotated",
      "file_stem": "DOC-012",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000012",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-11-25",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-013",
      "submission_id": "SUB-013",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "low_contrast",
      "file_stem": "DOC-013",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000013",
        "depositor_name": "College C (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-11-02",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-014",
      "submission_id": "SUB-014",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-014",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000014",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-27",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-015",
      "submission_id": "SUB-015",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-015",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000015",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-26",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-016",
      "submission_id": "SUB-016",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-016",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000016",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-18",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-018",
      "submission_id": "SUB-018",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "blurred",
      "file_stem": "DOC-018",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000018",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": true,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-019",
      "submission_id": "SUB-019",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-019",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000001",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-020",
      "submission_id": "SUB-020",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-020",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000020",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "04/05/2027",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": true,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-021",
      "submission_id": "SUB-021",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-021",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "00000021",
        "depositor_name": "College A (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-022",
      "submission_id": "SUB-022",
      "type": "FDR",
      "layout_id": "L2",
      "variant": "rotated",
      "file_stem": "DOC-022",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000022",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2026-10-23",
        "instrument_status": "MATURED",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-023",
      "submission_id": "SUB-023",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "low_contrast",
      "file_stem": "DOC-023",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000023",
        "depositor_name": "College B (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-024",
      "submission_id": "SUB-024",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-024",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000024",
        "depositor_name": "College D (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-025",
      "submission_id": "SUB-025",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-025",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000025",
        "depositor_name": "College E (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-026",
      "submission_id": "SUB-026",
      "type": "FDR",
      "layout_id": "L1",
      "variant": "clean",
      "file_stem": "DOC-026",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000026",
        "depositor_name": "College F (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-027",
      "submission_id": "SUB-027",
      "type": "FDR",
      "layout_id": "L2",
      "variant": "rotated",
      "file_stem": "DOC-027",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000027",
        "depositor_name": "College G (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-028",
      "submission_id": "SUB-028",
      "type": "FDR",
      "layout_id": "L3",
      "variant": "low_contrast",
      "file_stem": "DOC-028",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-01",
        "fdr_number": "DEMO-FDR-000028",
        "depositor_name": "College H (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-029",
      "submission_id": "SUB-029",
      "type": "FDR",
      "layout_id": "L4",
      "variant": "clean",
      "file_stem": "DOC-029",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-02",
        "fdr_number": "DEMO-FDR-000029",
        "depositor_name": "College I (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    },
    {
      "id": "DOC-030",
      "submission_id": "SUB-030",
      "type": "FDR",
      "layout_id": "L5",
      "variant": "clean",
      "file_stem": "DOC-030",
      "uploaded_at": "2026-10-26T03:25:00Z",
      "ground_truth": {
        "bank_id": "DEMO-BANK-03",
        "fdr_number": "DEMO-FDR-000030",
        "depositor_name": "College J (Synthetic)",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-01-15",
        "maturity_date": "2027-04-24",
        "instrument_status": "ACTIVE",
        "beneficiary_name": "AICTE (demo only)",
        "lien_status": "MARKED",
        "lien_in_favour_of": "AICTE (demo only)",
        "status_as_of": "2026-10-26T04:00:00Z",
        "record_updated_at": "2026-10-25T04:00:00Z"
      },
      "expected_ocr_review": false,
      "watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    }
  ],
  "bank_records": [
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000001",
      "depositor_name": "College A (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000002",
      "depositor_name": "College B (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000003",
      "depositor_name": "College C (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000004",
      "depositor_name": "Different Institution (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000006",
      "depositor_name": "College F (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000007",
      "depositor_name": "College G (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": null,
      "lien_in_favour_of": null,
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000008",
      "depositor_name": "College H (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "CLOSED",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000009",
      "depositor_name": "College I (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-10-16",
      "instrument_status": "MATURED",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000010",
      "depositor_name": "College J (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-01-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000011",
      "depositor_name": "College A (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-12-25",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000012",
      "depositor_name": "College B (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-11-25",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000013",
      "depositor_name": "College C (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-11-02",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000014",
      "depositor_name": "College D (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-10-27",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000015",
      "depositor_name": "College E (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-10-26",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000016",
      "depositor_name": "College F (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-10-18",
      "instrument_status": "MATURED",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000017",
      "depositor_name": "College G (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000018",
      "depositor_name": "College H (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000020",
      "depositor_name": "College J (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "00000021",
      "depositor_name": "College A (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000022",
      "depositor_name": "College B (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2026-10-23",
      "instrument_status": "MATURED",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000023",
      "depositor_name": "College B (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000024",
      "depositor_name": "College D (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000025",
      "depositor_name": "College E (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000026",
      "depositor_name": "College F (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000027",
      "depositor_name": "College G (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-01",
      "fdr_number": "DEMO-FDR-000028",
      "depositor_name": "College H (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-02",
      "fdr_number": "DEMO-FDR-000029",
      "depositor_name": "College I (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "Other Beneficiary (Synthetic)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    },
    {
      "bank_id": "DEMO-BANK-03",
      "fdr_number": "DEMO-FDR-000030",
      "depositor_name": "College J (Synthetic)",
      "principal_amount": "1000000.00",
      "currency": "INR",
      "issue_date": "2026-01-15",
      "maturity_date": "2027-04-24",
      "instrument_status": "ACTIVE",
      "beneficiary_name": "AICTE (demo only)",
      "lien_status": "MARKED",
      "lien_in_favour_of": "AICTE (demo only)",
      "status_as_of": "2026-10-26T04:00:00Z",
      "record_updated_at": "2026-10-25T04:00:00Z"
    }
  ],
  "verification_history": [
    {
      "id": "VER-028",
      "submission_id": "SUB-028",
      "method": "MANUAL_BANK_CONFIRMATION",
      "environment": "MOCK",
      "status": "CONFIRMED",
      "confirmed_fields": [
        "fdr_number",
        "principal_amount",
        "maturity_date",
        "depositor_name"
      ],
      "requested_at": "2026-10-26T03:40:00Z",
      "responded_at": "2026-10-26T04:00:00Z",
      "source_reference": "DEMO-CONF-028",
      "evidence_note": "Synthetic bank confirmation. Not real bank evidence.",
      "recorded_by": "USER-O01"
    },
    {
      "id": "VER-030",
      "submission_id": "SUB-030",
      "method": "MOCK_API",
      "environment": "MOCK",
      "status": "CONFIRMED",
      "confirmed_fields": [
        "fdr_number",
        "principal_amount",
        "maturity_date",
        "depositor_name"
      ],
      "requested_at": "2026-09-01T03:00:00Z",
      "responded_at": "2026-09-01T04:00:00Z",
      "source_reference": "DEMO-CONF-030",
      "evidence_note": "Synthetic bank confirmation. Not real bank evidence.",
      "recorded_by": "USER-O01"
    }
  ],
  "release_requests": [
    {
      "id": "REL-024",
      "submission_id": "SUB-024",
      "request_type": "FDR_DISCHARGE",
      "reason": "Synthetic conditions fulfilled for demo review",
      "status": "UNDER_REVIEW",
      "requested_at": "2026-10-20T04:00:00Z",
      "approved_by": null,
      "approved_at": null,
      "executed_at": null,
      "execution_reference": null
    },
    {
      "id": "REL-025",
      "submission_id": "SUB-025",
      "request_type": "FDR_DISCHARGE",
      "reason": "Synthetic conditions fulfilled for demo review",
      "status": "APPROVED_EXECUTION_PENDING",
      "requested_at": "2026-10-20T04:00:00Z",
      "approved_by": "USER-A01",
      "approved_at": "2026-10-24T04:00:00Z",
      "executed_at": null,
      "execution_reference": null
    },
    {
      "id": "REL-026",
      "submission_id": "SUB-026",
      "request_type": "FDR_DISCHARGE",
      "reason": "Synthetic conditions fulfilled for demo review",
      "status": "COMPLETED",
      "requested_at": "2026-10-20T04:00:00Z",
      "approved_by": "USER-A01",
      "approved_at": "2026-10-24T04:00:00Z",
      "executed_at": "2026-10-25T04:00:00Z",
      "execution_reference": "DEMO-DISCHARGE-26"
    }
  ],
  "audit_events": [
    {
      "id": "AUD-001",
      "submission_id": "SUB-001",
      "actor_id": "USER-C01",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-002",
      "submission_id": "SUB-002",
      "actor_id": "USER-C02",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-003",
      "submission_id": "SUB-003",
      "actor_id": "USER-C03",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-004",
      "submission_id": "SUB-004",
      "actor_id": "USER-C04",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-005",
      "submission_id": "SUB-005",
      "actor_id": "USER-C05",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-006",
      "submission_id": "SUB-006",
      "actor_id": "USER-C06",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-007",
      "submission_id": "SUB-007",
      "actor_id": "USER-C07",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-008",
      "submission_id": "SUB-008",
      "actor_id": "USER-C08",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-009",
      "submission_id": "SUB-009",
      "actor_id": "USER-C09",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-010",
      "submission_id": "SUB-010",
      "actor_id": "USER-C10",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-011",
      "submission_id": "SUB-011",
      "actor_id": "USER-C01",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-012",
      "submission_id": "SUB-012",
      "actor_id": "USER-C02",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-013",
      "submission_id": "SUB-013",
      "actor_id": "USER-C03",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-014",
      "submission_id": "SUB-014",
      "actor_id": "USER-C04",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-015",
      "submission_id": "SUB-015",
      "actor_id": "USER-C05",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-016",
      "submission_id": "SUB-016",
      "actor_id": "USER-C06",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-017",
      "submission_id": "SUB-017",
      "actor_id": "USER-C07",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-018",
      "submission_id": "SUB-018",
      "actor_id": "USER-C08",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-019",
      "submission_id": "SUB-019",
      "actor_id": "USER-C01",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-020",
      "submission_id": "SUB-020",
      "actor_id": "USER-C10",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-021",
      "submission_id": "SUB-021",
      "actor_id": "USER-C01",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-022",
      "submission_id": "SUB-022",
      "actor_id": "USER-C02",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-023",
      "submission_id": "SUB-023",
      "actor_id": "USER-C02",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-024",
      "submission_id": "SUB-024",
      "actor_id": "USER-C04",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-025",
      "submission_id": "SUB-025",
      "actor_id": "USER-C05",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-026",
      "submission_id": "SUB-026",
      "actor_id": "USER-C06",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-027",
      "submission_id": "SUB-027",
      "actor_id": "USER-C07",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-028",
      "submission_id": "SUB-028",
      "actor_id": "USER-C08",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-029",
      "submission_id": "SUB-029",
      "actor_id": "USER-C09",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    },
    {
      "id": "AUD-030",
      "submission_id": "SUB-030",
      "actor_id": "USER-C10",
      "action": "SUBMITTED",
      "at": "2026-10-26T03:30:00Z",
      "environment": "MOCK"
    }
  ],
  "test_cases": [
    {
      "id": "TEST-001",
      "submission_id": "SUB-001",
      "scenario": "MATCH",
      "description": "Exact match",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-002",
      "submission_id": "SUB-002",
      "scenario": "AMOUNT_MISMATCH",
      "description": "Document and entered amount differ from bank",
      "expected_result": "MISMATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-003",
      "submission_id": "SUB-003",
      "scenario": "MATURITY_MISMATCH",
      "description": "Entered date differs from document and bank",
      "expected_result": "MISMATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-004",
      "submission_id": "SUB-004",
      "scenario": "NAME_MISMATCH",
      "description": "Bank depositor differs",
      "expected_result": "MISMATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-005",
      "submission_id": "SUB-005",
      "scenario": "NOT_FOUND",
      "description": "No record in bank fixture",
      "expected_result": "NOT_FOUND_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-006",
      "submission_id": "SUB-006",
      "scenario": "SOURCE_UNAVAILABLE",
      "description": "Simulated bank outage",
      "expected_result": "SOURCE_UNAVAILABLE",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-007",
      "submission_id": "SUB-007",
      "scenario": "PARTIAL_RESPONSE",
      "description": "Bank cannot confirm lien",
      "expected_result": "PARTIAL_CONFIRMATION",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-008",
      "submission_id": "SUB-008",
      "scenario": "CLOSED",
      "description": "Bank says deposit closed",
      "expected_result": "CLOSED_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-009",
      "submission_id": "SUB-009",
      "scenario": "MATURED",
      "description": "Matured instrument",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": -10,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-010",
      "submission_id": "SUB-010",
      "scenario": "DUE_90",
      "description": "90 day reminder boundary",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 90,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-011",
      "submission_id": "SUB-011",
      "scenario": "DUE_60",
      "description": "60 day boundary",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 60,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-012",
      "submission_id": "SUB-012",
      "scenario": "DUE_30",
      "description": "30 day boundary",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 30,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-013",
      "submission_id": "SUB-013",
      "scenario": "DUE_7",
      "description": "7 day boundary",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 7,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-014",
      "submission_id": "SUB-014",
      "scenario": "DUE_1",
      "description": "1 day boundary",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 1,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-015",
      "submission_id": "SUB-015",
      "scenario": "DUE_TODAY",
      "description": "Maturity today",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 0,
      "expected_reminder_today": true,
      "expected_overdue": false
    },
    {
      "id": "TEST-016",
      "submission_id": "SUB-016",
      "scenario": "OVERDUE",
      "description": "Renewal deadline missed",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": -8,
      "expected_reminder_today": false,
      "expected_overdue": true
    },
    {
      "id": "TEST-017",
      "submission_id": "SUB-017",
      "scenario": "MISSING_DOCUMENT",
      "description": "Required file absent",
      "expected_result": "BLOCK_MISSING_DOCUMENT",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-018",
      "submission_id": "SUB-018",
      "scenario": "UNREADABLE",
      "description": "OCR cannot confidently extract",
      "expected_result": "OCR_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-019",
      "submission_id": "SUB-019",
      "scenario": "DUPLICATE",
      "description": "Second submission repeats bank/reference",
      "expected_result": "DUPLICATE_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-020",
      "submission_id": "SUB-020",
      "scenario": "AMBIGUOUS_DATE",
      "description": "Ambiguous document date requires review",
      "expected_result": "DATE_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-021",
      "submission_id": "SUB-021",
      "scenario": "LEADING_ZERO",
      "description": "Reference has leading zeros",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-022",
      "submission_id": "SUB-022",
      "scenario": "RENEWAL_OLD",
      "description": "Predecessor awaiting successor acceptance",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": -3,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-023",
      "submission_id": "SUB-023",
      "scenario": "RENEWAL_NEW",
      "description": "Successor pending review",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-024",
      "submission_id": "SUB-024",
      "scenario": "RELEASE_REQUESTED",
      "description": "Request under scrutiny",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-025",
      "submission_id": "SUB-025",
      "scenario": "RELEASE_APPROVED",
      "description": "Approved but not executed",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-026",
      "submission_id": "SUB-026",
      "scenario": "RELEASE_COMPLETED",
      "description": "Execution evidence recorded",
      "expected_result": "FIELDS_MATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-027",
      "submission_id": "SUB-027",
      "scenario": "MANUAL_PENDING",
      "description": "Manual bank confirmation needed",
      "expected_result": "MANUAL_PENDING",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-028",
      "submission_id": "SUB-028",
      "scenario": "MANUAL_CONFIRMED",
      "description": "Manual evidence recorded",
      "expected_result": "MANUAL_CONFIRMED",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-029",
      "submission_id": "SUB-029",
      "scenario": "LIEN_MISMATCH",
      "description": "Bank lien beneficiary differs",
      "expected_result": "MISMATCH",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    },
    {
      "id": "TEST-030",
      "submission_id": "SUB-030",
      "scenario": "STALE_CONFIRMATION",
      "description": "Old confirmation requires review under demo policy",
      "expected_result": "REVERIFY_REVIEW",
      "expected_maturity_offset_days": 180,
      "expected_reminder_today": false,
      "expected_overdue": false
    }
  ],
  "rules": {
    "required_fields": [
      "bank_id",
      "fdr_number",
      "depositor_name",
      "principal_amount",
      "currency",
      "issue_date",
      "maturity_date"
    ],
    "reminder_days_before": [
      90,
      60,
      30,
      7,
      1
    ],
    "notify_on_due_date": true,
    "overdue_followup_days": [
      1,
      7
    ],
    "verification_max_age_days_demo": 30,
    "renewal_required_default": false,
    "regulatory_note": "Demo configuration only. Replace with authorized requirements."
  }
}
```

## 4. Document generator — generate_fixtures.py

```python
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

base = Path(__file__).resolve().parent
seed = json.loads((base / "seed.json").read_text())
out = base / "fixtures"
out.mkdir(exist_ok=True)
fonts = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
def font(size):
    for name in fonts:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

labels = [
    ("fdr_number", "FDR Number"), ("bank_id", "Issuing Bank"),
    ("depositor_name", "Depositor"), ("principal_amount", "Principal INR"),
    ("currency", "Currency"), ("issue_date", "Issue Date"),
    ("maturity_date", "Maturity Date"), ("beneficiary_name", "Beneficiary"),
    ("lien_status", "Lien Status"), ("lien_in_favour_of", "Lien In Favour Of")
]
manifest = []
for doc in seed["documents"]:
    image = Image.new("RGB", (1600, 1600), "white")
    draw = ImageDraw.Draw(image)
    layout = int(doc["layout_id"][1:])
    x = 65 + layout * 8
    draw.rectangle((35, 35, 1560, 1550), outline="black", width=3)
    draw.text((x, 65), "SYNTHETIC - FOR PROTOTYPE ONLY", fill="black", font=font(32))
    draw.text((x, 130), "FIXED DEPOSIT RECEIPT", fill="black", font=font(42))
    draw.text((x, 195), "Fictional bank document - no financial value", fill="black", font=font(26))
    pairs = list(labels)
    if layout == 2:
        pairs = pairs[2:] + pairs[:2]
    elif layout == 3:
        pairs = list(reversed(pairs))
    y = 280
    for key, label in pairs:
        value = doc["ground_truth"].get(key)
        text = "NOT STATED" if value is None else str(value)
        if key == "principal_amount" and layout == 4:
            text = "10,00,000.00" if text == "1000000.00" else text
        if key in ("issue_date", "maturity_date") and layout == 5 and len(text) == 10 and text[4] == "-":
            year, month, day = text.split("-")
            text = f"{day}-{month}-{year}"
        if layout in (1, 3, 5):
            draw.text((x, y), label + ": " + text, fill="black", font=font(28))
        else:
            draw.text((x, y), label, fill="black", font=font(27))
            draw.text((x + 470, y), text, fill="black", font=font(27))
        y += 92
    draw.text((x, 1380), "No real stamp, signature or bank authorization", fill="black", font=font(25))
    if doc["variant"] == "rotated":
        image = image.rotate(2, fillcolor="white")
    elif doc["variant"] == "low_contrast":
        image = image.point(lambda n: int(170 + n / 3))
    elif doc["variant"] == "blurred":
        image = image.resize((240, 240)).resize((1600, 1600)).filter(ImageFilter.GaussianBlur(5))
    image.save(out / (doc["id"] + ".png"))
    image.save(out / (doc["id"] + ".pdf"), "PDF", resolution=150)
    manifest.append({"document_id": doc["id"], "png": "fixtures/" + doc["id"] + ".png", "pdf": "fixtures/" + doc["id"] + ".pdf", "submission_id": doc["submission_id"]})
(out / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Generated {len(manifest)} PNGs and {len(manifest)} image-based PDFs")

```

## 5. Mock bank service contract

### POST /mock-bank/v1/fdr-verifications
Request body: `{"bank_id":"DEMO-BANK-01","fdr_number":"DEMO-FDR-000001"}`.
Authenticate service-to-service. Do not accept a caller-supplied expected answer or scenario code. Select a bank row by the composite bank_id + fdr_number. The following fixed fixtures control source behaviour independently of the client request:
- SUB-005 reference: return HTTP 200 with lookup_status NOT_FOUND, no confirmed fields. Route to review; not automatic fraud/rejection.
- SUB-006 reference: return HTTP 503 SOURCE_UNAVAILABLE. No mismatch finding; retry/manual path.
- SUB-007 reference: return partial fields, omit lien_status and lien_in_favour_of from confirmed_fields; list them in unsupported_fields.
- SUB-027 reference: return HTTP 200 MANUAL_REQUIRED with no confirmed fields.
- Other existing rows: return FOUND and fields from bank_records.
- Unknown references: NOT_FOUND. Unauthorized request: 401/403. Malformed request: 400.

Successful envelope:
```json
{"verification_id":"generated-server-id","environment":"MOCK","source":"DEMO-BANK-01","lookup_status":"FOUND","requested_at":"2026-10-26T04:30:00Z","responded_at":"2026-10-26T04:30:01Z","status_as_of":"2026-10-26T04:00:00Z","confirmed_fields":{"fdr_number":"DEMO-FDR-000001","principal_amount":"1000000.00","currency":"INR","maturity_date":"2027-04-24"},"unsupported_fields":[],"source_reference":"generated-demo-reference"}
```
Example is an envelope illustration; runtime response must include supported fields from the selected bank row. Generate request/response times from the controlled server clock; retain bank status_as_of. Historical fixture times must not be overwritten by a replay request.

### Comparison rules
- Three separate layers: entered-vs-document; document-vs-bank; current source status-vs-required administrative conditions.
- Preserve FDR references as strings including zeros; composite bank/reference uniqueness. Duplicate submission raises review, not an automatic adverse finding.
- Decimal arithmetic for amounts. Strip display grouping for comparisons; never floats for money.
- ISO date normalization only when unambiguous. 04/05/2027 requires explicit format clarification; do not guess.
- Names: whitespace/case normalization allowed. Material differences require review, not probabilistic automatic acceptance.
- Source-unavailable, unsupported and not-found are different results. Null means unknown, not false.
- ACTIVE in a bank row does not establish every AICTE condition. CLOSED is a review alert. MATURED is not release authorization.
- Only source-confirmed fields appear under confirmed_fields. Document-only values remain separate.
- Manual confirmation records approved source/contact provenance, evidence, time and officer. College-uploaded correspondence alone is not independent confirmation.
- QR codes, if added later, must resolve only to approved sources. Arbitrary QR text is not trusted confirmation. No QR/digital signature support is claimed in these fixtures.

## 6. Time, reminders and monitoring

Inject demo_now from meta into date-sensitive logic. Production uses the server clock. Display Asia/Kolkata; timestamps UTC; maturity/validity/deadline fields DATE. Calculate days_until with local calendar dates, not rounded UTC seconds.
- DUE_90/60/30/7/1 produce the corresponding reminder on the frozen day. DUE_TODAY produces due-today notice.
- OVERDUE uses explicit renewal_due_date. Other matured records get maturity follow-up but are not automatically labelled renewal-noncompliant unless an applicable requirement exists.
- document_valid_until is null when no separate expiry applies. Do not invent an FDR expiry date in addition to maturity.
- Do not schedule definitive deadlines using unreviewed ambiguous OCR values. Show provisional dates and task for officer confirmation.
- Example notification key: submission_id + deadline_type + due_date + offset + recipient + channel. Deduplicate retries; log outcomes.
- Once renewal is submitted, stop reminders asking to submit; show verification-pending tasks and continue tracking the unresolved obligation. Acceptance, not upload alone, resolves the applicable renewal requirement.
- Date corrections reschedule future jobs and preserve sent history. Outage or date change must not duplicate alerts.
- The demo 30-day verification freshness rule is illustrative only. Stale confirmation means review/reverify, not automatic invalidity.

Runtime tables (generate values, do not pre-populate fabricated delivery results):
- notifications: id, submission_id, event_type, deadline_type, due_date, offset_days, recipient_user_id, channel, scheduled_at, sent_at, delivery_status, dedupe_key.
- discrepancies: id, submission_id, field, submitted_value, document_value, source_value, reason, evidence_document_id, page, bounding_box, assigned_to, created_at, response_due_date, response, resolved_by, resolved_at, resolution.
- OCR results: id, document_id, engine_version, processed_at, raw_text, field, raw_value, normalized_value, confidence_nullable, page, bounding_box, review_status. Confidence values must be actual engine outputs, not ground-truth labels.
- audit: id, entity_type, entity_id, actor_id, action, timestamp, before, after, reason, source_reference.
- document storage: id, version, private_storage_key, sha256, mime_type, uploaded_by, uploaded_at, predecessor_document_id. Calculate real hashes from generated bytes.

## 7. Persona flows

College: provisioned institution login -> dashboard -> New submission -> upload -> OCR -> review/correct extracted fields -> supporting documents -> checks -> submit -> acknowledgement -> track scrutiny/bank confirmation -> respond to queries -> accepted record -> reminders -> linked renewal or release request -> follow decision/execution -> closure.

Officer: login -> assigned queue -> inspect document and entered/extracted fields -> raise query or initiate verification -> compare source fields -> record evidence -> resolve discrepancy -> accept according to permissions -> monitor dates -> review renewal -> review release -> forward to authority -> record authorized execution.

Authority: login -> release queue -> examine recommendation, evidence and conditions -> approve/reject/return with reason. Officer cannot self-grant approval role. Approval does not set completion automatically.

Dashboard groups: pending review, pending bank confirmation, discrepancies, current accepted instruments, approaching maturity, matured, renewals, release requests, overdue actions. Seed all submitted records as pending initially and replay acceptance; do not show them as accepted solely because bank values match.

Release and renewal actions use recorded authorized checks. No automatic financial operation. Historical renewals remain linked and viewable. A predecessor marked superseded is not automatically discharged.

## 8. Acceptance checks beyond the 30 seed scenarios

1. College A cannot list/download College B documents.
2. Officer cannot perform competent-authority release approval.
3. Repeated submit request creates only one submission; repeated execution cannot execute release twice.
4. Mock bank records cannot be edited by college or portal form updates.
5. An OCR failure preserves upload and routes to review.
6. Bank-confirmed amount/date mismatch shows exact conflicting values and evidence.
7. Partial source response cannot show fully verified lien status.
8. Source outage preserves pending state and retry history.
9. Double scheduler run sends one reminder per dedupe key.
10. Corrected dates remove obsolete future reminders and keep previous audit entries.
11. Replacement upload retains old instrument; only authorized acceptance changes current instrument.
12. Release approval without completion remains execution pending.
13. Audit entries capture actor/time/reason and cannot be edited through ordinary UI.
14. File hash matches stored bytes; transformed image variants are not claimed to be exact duplicates.
15. CLOSED source record does not pass as current simply because amount/date match.

Report OCR field accuracy on labelled documents, mismatch precision/recall, source-response outcomes, processing time and alert timing separately. Synthetic-template accuracy does not establish real-bank performance. Keep a held-out layout for extraction tuning; do not report a universal fraud-detection accuracy.

## 9. External requirements: what is and is not needed

### Nothing external is required for the mock business data
This file supplies institution fixtures, instrument values, bank-side records, adversarial comparisons, reminder boundaries, renewal and release examples. The generator supplies actual uploadable OCR fixtures. No real customer records are needed.

### Software/services to install or configure
- Pillow to run the document generator.
- A real OCR runtime, for example PaddleOCR, and its model files. Start with pretrained inference; no model-training dataset required.
- Frontend/backend/database/private document storage/authentication selected by the team.
- In-app notifications suffice for the demo; email/SMS credentials only if demonstrating actual delivery. Do not send to example.invalid addresses.

### Must be obtained externally for live deployment
- Formally authorized bank verification API/portal/manual confirmation process, its authentication, supported fields and access agreement. A generic bank-account validation API is not FDR verification.
- Authorized AICTE institution records, identity integration and authoritative requirements/deadlines/approval permissions.
- Permissioned, anonymized real FDR samples from multiple banks to test actual format generalization. Public generic OCR datasets cannot establish FDR legitimacy.
- Approved hosting, security and retention requirements.

### Official starting references, not guaranteed integrations
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- Amazon Textract key-value extraction: https://docs.aws.amazon.com/textract/latest/dg/how-it-works-kvp.html
- ICICI corporate FD API listing: https://www.icici.bank.in/business-banking/cms/corporate-api-suite/other-services-api
- API Setu DigiLocker specifications: https://apisetu.gov.in/digilocker

The bank listing is a lead for authorized discussions, not proof that arbitrary third-party FDR verification is available. DigiLocker availability depends on issuer/document support. No API credentials or live access are bundled.

## 10. Agent completion checklist

Extract seeds and generator; generate fixtures; seed roles and linked records; implement private upload and actual OCR; implement separate mock bank lookup; implement three-way comparison; implement manual confirmation; implement timestamps and controlled clock; implement reminders; implement renewal/release flows; implement dashboards/reports/audit; run scenario assertions; label all simulated data and sources visibly. Do not add unrelated modules.
