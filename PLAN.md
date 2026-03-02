# Odoo 18 CE Custom ERP — Implementation Plan (Revised)

## Confirmed Specs
- **Odoo**: 18 Community Edition
- **Country**: Generic (GCC-ready, not hardcoded to UAE)
- **Currency**: Configured at setup (AED/QAR/SAR — handled by Odoo's multi-currency)
- **Language**: English + Arabic (bilingual portal and reports)
- **Contracting flow**: We quote (BOQ) → client sends PO back → project starts
- **Service billing**: Both per-job invoices AND monthly PRO flat-fee contracts
- **Modules**: Separate installable modules per division

---

## Requirement vs Odoo 18 CE Module Mapping

### Legend
- **USE AS-IS** — Standard Odoo covers this fully; zero custom code needed
- **CONFIGURE** — Covered by Odoo but needs setup (stages, groups, etc.)
- **PARTIAL** — Odoo covers 60–80%; small extension or extra field needed
- **CUSTOM** — Not in Odoo CE at all; must be built

---

### Division 1 — Service Sector

| Requirement | Covers By | Status | Notes |
|---|---|---|---|
| Job/work tracking per client request | `project` (project.task) | USE AS-IS | Tasks = jobs. One project per service category or per client |
| Job stages (New → Submitted → Under Process → Approved → Completed → Delivered) | `project` (task stages) | CONFIGURE | Stages are fully configurable per project type |
| Due date on each job | `project` (task deadline) | USE AS-IS | Deadline field built-in |
| Overdue/deadline alerts | `project` + `mail` (scheduled activities) | USE AS-IS | Configure activity types + automated actions |
| Pending work monitoring (kanban, by stage) | `project` | USE AS-IS | Built-in kanban and list views |
| Per-job invoicing | `account` | USE AS-IS | Create invoice per task/client directly |
| Client-wise payment tracking | `account` (partner balance) | USE AS-IS | Partner ledger built-in |
| SOA and client ledger | `account` | USE AS-IS | Partner ledger report built-in |
| Monthly PRO contract management | None | **CUSTOM** | New `ma.service.contract` model |
| Recurring billing for PRO contracts | `account` (recurring invoices) | PARTIAL | Odoo 18 has recurring invoices but they need to be linked and auto-triggered from the contract |
| Client portal: view pending jobs & status | `project` + `portal` | CONFIGURE | Enable portal sharing on project tasks; clients see /my/tasks |
| Client portal: view invoices & balances | `account` + `portal` | USE AS-IS | /my/invoices already exists |
| Government reference field on jobs | `project` | PARTIAL | Extend `project.task` with `govt_ref`, `service_type_id`, auto-sequence |

**Custom work needed for Service:**
- Extend `project.task` with: `service_type_id`, `govt_ref`, `custom_sequence` (JOB/2026/0001)
- New model `ma.service.contract` (monthly PRO contracts + auto recurring invoices)
- Cron: generate monthly invoices from active contracts
- Cron: alert on overdue jobs (complement to Odoo activities)

---

### Division 2 — Contracting

| Requirement | Covered By | Status | Notes |
|---|---|---|---|
| BOQ-based quotation | `sale` (sale.order + order lines) | USE AS-IS | Sale order lines = BOQ items; UoM for m², m, pcs, lot |
| Quotation stages (draft → sent → confirmed) | `sale` | USE AS-IS | Built-in sale order states |
| PO number from client | `sale` | PARTIAL | Extend `sale.order` with `client_po_number`, `client_npo_number` fields |
| Contract value tracking | `sale` (amount_total on sale order) | USE AS-IS | Contract value = confirmed sale order total |
| Link sale order (BOQ) to project | `project` + `sale` (`sale_project` module) | USE AS-IS | Odoo CE has `sale_project` module that links SO → Project |
| Project stages (PO Received → In Progress → Completed → Closed) | `project` | CONFIGURE | Project stages are configurable |
| Project progress monitoring | `project` | USE AS-IS | Built-in |
| Advance / milestone payment invoicing | `account` (down payment invoices on sale orders) | PARTIAL | Odoo has advance invoicing but not milestone schedules |
| Payment milestone schedule | None | **CUSTOM** | New `ma.project.payment` model |
| Balance payment tracking | `account` | USE AS-IS | Remaining amount tracked via sale order invoiced status |
| Client ledger / SOA | `account` | USE AS-IS | Built-in |
| Payment ageing report | `account` | USE AS-IS | Aged Receivable report built-in |
| Project profitability tracking | `project` + `account` | PARTIAL | Need computed fields: contract value vs total costs |
| One-click client project summary | None | **CUSTOM** | Smart button on `res.partner` showing project financials |
| Project type (Glass Partition, Installation, etc.) | None | **CUSTOM** | Small master model `ma.project.type` |

**Custom work needed for Contracting:**
- Extend `sale.order`: add `client_po_number`, `client_npo_number`, `project_type_id`
- Extend `project.project`: add `sale_order_id` link, `project_type_id`, `client_po_number`, profitability computed fields
- New model `ma.project.payment` (payment milestones: advance/progress/retention/final)
- Smart button on `res.partner` for one-click project financial summary

---

### Division 3 — Trading

| Requirement | Covered By | Status | Notes |
|---|---|---|---|
| Inventory management | `stock` | USE AS-IS | Fully covered |
| Purchase & supplier invoices | `purchase` + `account` | USE AS-IS | Fully covered |
| Sales & customer invoices | `sale` + `account` | USE AS-IS | Fully covered |
| Stock tracking | `stock` | USE AS-IS | Fully covered |
| Customer & supplier ledger | `account` | USE AS-IS | Fully covered |
| Profit tracking | `sale_management` (margin) | USE AS-IS | Sale margin is included in CE; shows profit per order line |
| Future e-commerce | `website_sale` | USE AS-IS | Standard module, install when ready |

**Custom work needed for Trading: NONE**
Trading is entirely covered by standard Odoo CE modules. Only configuration and setup needed (product categories, warehouses, pricelists).

---

### Common Requirements (All Divisions)

| Requirement | Covered By | Status | Notes |
|---|---|---|---|
| Full accounting (invoices, receipts, expenses, journal entries) | `account` | USE AS-IS | Fully covered |
| SOA, partner ledger, ageing report | `account` | USE AS-IS | Built-in reports |
| Role-based access control | Odoo core (ir.rule + res.groups) | CONFIGURE | Configure groups and record rules per division |
| HR: employee records | `hr` | USE AS-IS | Fully covered |
| HR: leave management | `hr_holidays` | USE AS-IS | Fully covered |
| HR: passport / national ID / visa expiry tracking | `hr` | **CUSTOM** | Extend `hr.employee` with document expiry fields + cron alerts |
| Document upload & storage | `mail` (attachments via mail.thread) | USE AS-IS | Every record with chatter supports attachments |
| Email notifications & reminders | `mail` + `mail.activity` + automated actions | USE AS-IS | Configure automated actions for stage changes |
| Cloud access, multi-user login | Odoo core | USE AS-IS | Built-in |
| Cross-division dashboard | None (each module has its own) | **CUSTOM** | Unified dashboard showing KPIs across all divisions |
| Division tagging (data isolation) | None | **CUSTOM** | Add `division` field to key models for filtering |
| Arabic language UI | `base` (i18n) | CONFIGURE | Install Arabic language pack; Odoo's translation system handles menus/UI |
| Arabic reports & portal | Custom reports | PARTIAL | Custom QWeb report templates will support both English and Arabic |

---

## Revised Module Architecture

Based on the mapping above, the original 6 modules collapse to **4 lean custom modules**. Standard Odoo handles the rest.

```
Standard Odoo 18 CE (install & configure):
  account, sale, purchase, stock, project, hr,
  hr_holidays, portal, website, mail, sale_project

Custom modules (what we actually build):

  ma_base          ← Division data, unified dashboard, shared menu
    |
    ├── ma_service      ← Extends project.task + adds PRO contract model
    |
    ├── ma_contracting  ← Extends sale.order + project.project + adds payment milestones
    |
    └── ma_hr_ext       ← Extends hr.employee with document/expiry tracking
```

**Eliminated from original plan (not needed):**
- `ma_portal` — Standard Odoo portal already shows tasks and invoices. We only need configuration + minor template tweaks in `ma_service`.
- `ma_trading` — 100% covered by standard Odoo modules; just configure.

---

## Module 1: `ma_base`

### What it does
- Provides the `Division` master model (Service, Contracting, Trading)
- Adds `division_id` field to `res.partner`, `project.project`, `sale.order`, `account.move`
- Defines security groups and record rules for division-level access
- Provides a unified OWL dashboard with KPIs across all divisions
- Defines custom menus grouping all three divisions under one top-level app

### Models
| Model | Type | Purpose |
|-------|------|---------|
| `ma.division` | New | Division master: Service, Contracting, Trading |
| `res.partner` | Extend | Add `division_ids` (Many2many), `client_type` (service/contracting/trading/all) |
| `project.project` | Extend | Add `division_id` |
| `sale.order` | Extend | Add `division_id` |
| `account.move` | Extend | Add `division_id` (auto-set from partner or project) |

### Security Groups
```
MA / Service User          (read/write own division jobs)
MA / Service Manager       (full access to service division)
MA / Contracting User      (read/write own division projects)
MA / Contracting Manager   (full access to contracting division)
MA / Trading User          (sale/purchase/stock within trading)
MA / Trading Manager       (full access to trading division)
MA / Administrator         (full access to all divisions)
```
Record rules filter `project.project`, `sale.order`, `account.move` by `division_id` per group.

### Dashboard (OWL Component)
- Total receivables (all + per division)
- Overdue amount and count (from `account.move`)
- Pending service jobs (from `project.task` — open tasks in service projects)
- Overdue service jobs
- Ongoing contracting projects (by stage)
- Open purchase orders
- Documents expiring within 30 days (HR)
- Quick-action buttons per division

### File Structure
```
ma_base/
├── __manifest__.py
├── models/
│   ├── ma_division.py
│   ├── res_partner.py
│   ├── project_project.py
│   ├── sale_order.py
│   └── account_move.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── views/
│   ├── res_partner_views.xml
│   ├── dashboard_views.xml
│   └── menu_views.xml
├── data/
│   └── division_data.xml
└── static/src/
    ├── js/ma_dashboard.js
    └── xml/ma_dashboard.xml
```

---

## Module 2: `ma_service`

### What it does
Extends `project.task` with service-specific fields. Adds the `ma.service.contract` model for monthly PRO contracts with automated recurring invoice generation. Configures portal access for clients.

### What Odoo Already Handles (No Code)
- Task kanban by stage, list, calendar view
- Task deadline and assignee
- Chatter, activities, attachments on tasks
- Portal: clients see their tasks at `/my/tasks` (needs project set to "Allow portal users")
- Invoice creation and tracking
- Partner balance and ledger

### Extensions to `project.task`
New fields added via extension:
```
service_type_id    → Many2one to ma.service.type
govt_reference     → Char (government transaction/reference number)
job_sequence       → Char (auto-generated: JOB/2026/00001)
client_notes       → Text (visible to client on portal)
invoice_ids        → Many2many to account.move (related invoices for this job)
```

### New Models

**`ma.service.type`** — Service type master
```
name                → Char (Company Formation, PRO Support, Visa, Tourism, Document Processing, Other)
code                → Char
default_fee         → Monetary (default fee for ad-hoc billing)
description         → Text
```

**`ma.service.contract`** — Monthly PRO contracts
```
name / sequence     → Char (auto: PRO/2026/00001)
client_id           → Many2one res.partner
start_date          → Date
end_date            → Date
monthly_fee         → Monetary
billing_day         → Integer (day of month to generate invoice, e.g. 1 or 30)
state               → Selection: draft, active, expired, cancelled
contract_line_ids   → One2many to ma.service.contract.line
invoice_ids         → Many2many account.move (generated invoices)
note                → Text
```

**`ma.service.contract.line`** — Services in the contract
```
contract_id         → Many2one
service_type_id     → Many2one ma.service.type
description         → Char
quantity            → Integer (units per month)
```

### Automated Actions (Cron)
- **Daily**: Find active contracts where `billing_day == today.day` → auto-create draft invoice → post or leave for review (configurable)
- **Daily**: Find contracts expiring within 30 days → email manager alert
- **Daily**: Find tasks where `date_deadline < today` and state not done → create overdue activity

### Portal Configuration
- Service projects are set with `privacy_visibility = 'portal'`
- Clients granted portal access see only their own tasks (`partner_id` matched)
- Portal task view shows: stage, due date, `govt_reference`, `client_notes`, attachments
- No separate portal module needed — configure via project settings

### Reports
- Job list report (filterable by client, type, date, stage)
- Contract billing summary

### File Structure
```
ma_service/
├── __manifest__.py
├── models/
│   ├── ma_service_type.py
│   ├── ma_service_contract.py
│   └── project_task.py          (extend project.task)
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── views/
│   ├── project_task_views.xml   (adds service fields to task form/list)
│   ├── contract_views.xml
│   ├── service_type_views.xml
│   └── menu_views.xml
├── reports/
│   └── job_report.xml
├── data/
│   ├── sequence_data.xml
│   ├── service_type_data.xml    (seed: Company Formation, PRO, Visa, etc.)
│   ├── mail_template_data.xml
│   └── cron_data.xml
└── wizard/
    └── generate_contract_invoice_wizard.py
```

---

## Module 3: `ma_contracting`

### What it does
Extends `sale.order` (BOQ/quotation) and `project.project` (project tracking) with contracting-specific fields. Adds payment milestone model. Adds client financial summary smart button on partner.

### What Odoo Already Handles (No Code)
- `sale.order` for BOQ: item description, qty, UoM, unit price, total — all built-in
- Quotation PDF print — built-in
- Sale → Invoice flow (advance invoices, full invoice) — built-in
- `project.project` stages — configurable
- `sale_project` module links a confirmed sale order to a project automatically
- Partner ledger, SOA, aged receivables — built-in in `account`

### Extensions to `sale.order`
```
client_po_number    → Char (PO number received from client)
client_npo_number   → Char (NPO number if applicable)
project_type_id     → Many2one ma.project.type
```

### Extensions to `project.project`
```
project_type_id     → Many2one ma.project.type
client_po_number    → Char
payment_ids         → One2many to ma.project.payment
contract_value      → Monetary (related from linked sale order amount_total)
total_invoiced      → Monetary (computed: sum of posted invoices)
total_received      → Monetary (computed: sum of registered payments)
pending_balance     → Monetary (computed: total_invoiced - total_received)
profitability_pct   → Float (computed)
```

### New Models

**`ma.project.type`** — Project type master
```
name    → Char (Glass Partition, Glass Installation, Maintenance, Supply & Install, Subcontracting)
code    → Char
```

**`ma.project.payment`** — Payment milestones
```
project_id          → Many2one project.project
sequence            → Integer
name                → Char (Advance, Progress Billing 1, Retention Release, Final)
payment_type        → Selection: advance, progress, retention, final
amount              → Monetary
percentage          → Float (% of contract value, auto-computes amount)
due_date            → Date
state               → Selection: pending, invoiced, received, overdue
invoice_id          → Many2one account.move (linked invoice when created)
payment_date        → Date (when actually received)
notes               → Text
```

**Retention (confirmed requirement)**
- `retention_percentage` field on `project.project` (e.g. 10%)
- When a project is confirmed, a "Retention Release" milestone is **auto-created** = `contract_value × retention_percentage`
- Retention milestone state stays `pending` until project is `Closed` stage
- Retention amount is excluded from progress billing totals until released
- Retention release invoice generated separately when client approves final handover

### Smart Button on `res.partner`
A "Projects" smart button on the partner form opens a custom view showing:
```
Project Name | Contract Value | Invoiced | Received | Balance | Overdue Days | Stage
─────────────────────────────────────────────────────────────────────────────────────
TOTAL        | XXX,XXX        | XXX,XXX  | XXX,XXX  | XX,XXX  | —            | —
```

### Views
- Project form: new tabs for Payment Milestones, Profitability
- Sale order form: new fields for client_po_number, npo_number, project_type
- Project type configuration menu
- Client project summary view (from partner smart button)
- Payment milestone tree (editable inline)

### Reports
- BOQ / quotation print (extends sale order report template with custom header)
- Payment milestone schedule print
- Project profitability report
- Payment ageing (extends standard aged receivable, filtered by project)

### File Structure
```
ma_contracting/
├── __manifest__.py
├── models/
│   ├── ma_project_type.py
│   ├── ma_project_payment.py
│   ├── project_project.py       (extend project.project)
│   ├── sale_order.py            (extend sale.order)
│   └── res_partner.py           (add smart button computed fields)
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── views/
│   ├── project_views.xml
│   ├── payment_views.xml
│   ├── sale_order_views.xml
│   ├── project_type_views.xml
│   ├── partner_views.xml
│   └── menu_views.xml
├── reports/
│   ├── boq_report.xml
│   ├── payment_schedule_report.xml
│   └── project_profitability_report.xml
└── data/
    ├── project_type_data.xml
    └── sequence_data.xml
```

---

## Module 4: `ma_hr_ext`

### What it does
Extends `hr.employee` with fields for tracking government-issued document numbers and expiry dates. Adds a document attachment model for storing scanned copies. Provides cron-based expiry alerts.

### What Odoo Already Handles (No Code)
- Employee records, departments, job positions — `hr`
- Leave requests and approvals — `hr_holidays`
- File attachments on employee records — `mail.thread`

### Extension to `hr.employee`
New fields:
```
passport_no             → Char
passport_expiry         → Date
national_id_no          → Char   (generic: Emirates ID / QID / Iqama / etc.)
national_id_expiry      → Date
visa_no                 → Char
visa_type               → Selection: employment, residence, visit, other
visa_expiry             → Date
labour_card_no          → Char
labour_card_expiry      → Date
health_card_no          → Char
health_card_expiry      → Date
document_ids            → One2many to ma.hr.document
days_to_next_expiry     → Integer (computed: min days until any document expires)
expiry_alert_color      → Integer (kanban color: red <30d, orange 30-60d, green >60d)
```

### New Models

**`ma.hr.document`** — Document storage
```
employee_id         → Many2one hr.employee
document_type_id    → Many2one ma.hr.document.type
document_no         → Char
issue_date          → Date
expiry_date         → Date
file                → Binary (scanned copy)
file_name           → Char
state               → Selection: valid, expiring_soon, expired (computed)
notes               → Text
```

**`ma.hr.document.type`** — Document type master
```
name    → Char (Passport, National ID, Visa, Labour Card, Health Card, Employment Contract, Insurance, Other)
code    → Char
```

### Automated Actions (Cron)
- **Daily cron**: Scan all `hr.employee` and `ma.hr.document` records for expiry dates
- Alert thresholds: 60 days, 30 days, 15 days, 7 days before expiry
- Email sent to: HR Manager group + employee's direct manager
- Dashboard widget updates expiry count automatically

### Views
- Employee form: new "Documents" tab with expiry fields + document list (editable)
- Document expiry list view: all employees, color-coded status (green/orange/red)
- Employee kanban with expiry color coding
- Document type configuration

### File Structure
```
ma_hr_ext/
├── __manifest__.py
├── models/
│   ├── ma_hr_document_type.py
│   ├── ma_hr_document.py
│   └── hr_employee.py           (extend hr.employee)
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── hr_employee_views.xml
│   ├── document_views.xml
│   ├── document_type_views.xml
│   └── menu_views.xml
└── data/
    ├── document_type_data.xml   (seed: Passport, National ID, Visa, etc.)
    ├── cron_data.xml
    └── mail_template_data.xml
```

---

## Standard Odoo Modules to Install & Configure (No Custom Code)

| Module | Division | What to Configure |
|--------|----------|-------------------|
| `account` | All | Chart of accounts, currencies, tax positions, payment terms, fiscal year |
| `account_accountant` | All | Reconciliation, bank statements |
| `sale` + `sale_management` | Contracting + Trading | Pricelist, UoM, payment terms |
| `purchase` | Contracting + Trading | Vendor management, PO approval |
| `stock` | Trading | Warehouse, locations, reordering rules |
| `project` | Service + Contracting | Service stages, contracting stages, portal sharing |
| `sale_project` | Contracting | Links confirmed sale order → project automatically |
| `hr` | All | Departments, job positions |
| `hr_holidays` | All | Leave types, approval flows |
| `portal` | Service | Portal user access for PRO clients |
| `mail` | All | SMTP server, email aliases |
| `base_setup` | All | Company info, logo, currency, language |

---

## Arabic / Bilingual Support Plan

| Area | Approach |
|------|----------|
| UI menus & buttons | Install Arabic language pack via Odoo settings. All standard Odoo strings are pre-translated. |
| Custom module labels | All `string=` values wrapped with `_()` for translation; `.po` file generated per module |
| Reports | QWeb templates use `<t t-if="lang == 'ar_001'">` for Arabic sections, or bilingual layout (English left, Arabic right) |
| Portal pages | Same QWeb translation approach |
| RTL layout | Odoo 18 supports RTL automatically when Arabic is selected as user language |
| Number/date format | Handled by Odoo's locale settings per user |

---

## Implementation Sequence

| Phase | Module | Key Deliverables |
|-------|--------|-----------------|
| 1 | Setup | Odoo 18 CE install, all standard modules installed, company configured, chart of accounts, currencies |
| 2 | `ma_base` | Division model, security groups, record rules, division fields on partners/projects/invoices, main menu |
| 3 | `ma_service` | Service types, job extensions on project.task, PRO contract model, recurring invoice cron, portal config |
| 4 | `ma_contracting` | Project types, extensions to sale.order and project.project, payment milestone model, client smart button, reports |
| 5 | `ma_hr_ext` | Employee document extensions, document model, expiry cron, alert emails |
| 6 | `ma_base` (dashboard) | OWL unified dashboard wiring all KPIs together |
| 7 | Reports & Arabic | Bilingual QWeb report templates, portal template language support, final polish |

---

## What We Are NOT Building Custom (Saves Significant Time)

| Originally Planned | Why Dropped | Covered By |
|-------------------|-------------|-----------|
| `ma_portal` module | Odoo portal already works for tasks + invoices | `project` + `portal` (configure only) |
| `ma_trading` module | 100% covered by standard modules | `sale`, `purchase`, `stock` |
| Custom SOA / ledger reports | Already built into Odoo account module | `account` (Partner Ledger, Aged Receivable) |
| Custom ageing report | Already exists | `account` (Aged Receivable/Payable) |
| Custom leave management | Already exists | `hr_holidays` |
| Custom document attachments | Already on every model via chatter | `mail.thread` |
| Custom multi-user / cloud access | Core Odoo | Built-in |

---

## Open Questions / Assumptions

These can be confirmed before or during development without blocking anything:

1. **Retention %**: Standard in contracting? If yes, add a `retention_percentage` field on projects and auto-compute retention amount in payment milestones.
2. **VAT/Tax**: Odoo's tax configuration will be set up generically; actual tax % and rules configured during installation.
3. **Email server**: SMTP credentials needed at setup time for cron notifications to work.
4. **Portal users**: PRO clients will be invited via standard Odoo portal invitation (Settings → Users → Grant portal access to a contact).
5. **Data migration**: If there is existing data (clients, jobs, contracts) to import, that is a separate task using Odoo's import (CSV/XLS) feature.
