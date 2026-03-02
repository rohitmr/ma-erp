# Odoo 18 CE — Requirement to Module Mapping Report

**Project**: MA ERP (Multi-Division Business)
**Target**: Odoo 18 Community Edition
**Date**: March 2026

---

## Status Key

| Status | Meaning |
|--------|---------|
| ✅ USE AS-IS | Fully covered by standard Odoo. Zero custom code. Install and configure only. |
| ⚙️ CONFIGURE | Covered by Odoo but requires setup (stages, groups, templates, etc.). No Python. |
| 🔧 PARTIAL | Odoo handles the core; a small extension (1–3 fields or a computed field) bridges the gap. |
| 🆕 CUSTOM | Not available in Odoo CE at all. Requires a new model or significant custom logic. |

---

## Division 1 — Service Sector (PRO & Company Formation)

| # | Requirement | Odoo CE Module | Status | What's Needed |
|---|-------------|----------------|--------|---------------|
| 1.1 | Job / work tracking per client request | `project` (Tasks) | ✅ USE AS-IS | Each task = one job. Kanban, list, calendar views built-in. |
| 1.2 | Job stages: New → Submitted → Under Process → Approved → Completed → Delivered | `project` (Task Stages) | ⚙️ CONFIGURE | Stages are configurable per project type. No code needed. |
| 1.3 | Due date on each job | `project` | ✅ USE AS-IS | `date_deadline` field built-in on every task. |
| 1.4 | Deadline alerts and reminders | `project` + `mail` (Activities) | ✅ USE AS-IS | Scheduled activities + automated actions. Configure in UI. |
| 1.5 | Pending / ongoing / delayed job monitoring | `project` | ✅ USE AS-IS | Kanban grouped by stage, list with filters. Built-in. |
| 1.6 | Per-job invoicing (ad-hoc billing) | `account` | ✅ USE AS-IS | Create invoice manually or via sale order linked to task. |
| 1.7 | Client-wise payment tracking and balance | `account` | ✅ USE AS-IS | Partner outstanding balance shown on partner form. |
| 1.8 | Statement of Account (SOA) | `account` | ✅ USE AS-IS | Partner Ledger report. Print or email from accounting menu. |
| 1.9 | Client Ledger | `account` | ✅ USE AS-IS | Partner Ledger report with date range filter. |
| 1.10 | Balance reminders to clients | `account` + `mail` | ✅ USE AS-IS | Follow-up actions (account_followup). Configure dunning. |
| 1.11 | Service type classification (Visa, Tourism, etc.) | None | 🆕 CUSTOM | `ma.service.type` master model. Small. ~30 lines of code. |
| 1.12 | Government / transaction reference per job | `project` | 🔧 PARTIAL | Extend `project.task`: add `govt_ref` (Char) + `service_type_id`. |
| 1.13 | Auto job sequence number (JOB/2026/00001) | None | 🔧 PARTIAL | Add `ir.sequence` and auto-assign on task creation in service projects. |
| 1.14 | Monthly PRO contract management | None | 🆕 CUSTOM | New model `ma.service.contract` with monthly fee, billing day, lines. |
| 1.15 | Recurring invoice auto-generation for PRO contracts | `account` | 🔧 PARTIAL | Odoo has recurring invoices but not contract-triggered. Custom cron links contract → invoice. |
| 1.16 | Contract expiry alerts | None | 🆕 CUSTOM | Cron: check `end_date` of active contracts, email 30 days before. |
| 1.17 | Client portal: view pending jobs and status | `project` + `portal` | ⚙️ CONFIGURE | Set project to "Portal" visibility. Clients see `/my/tasks`. No code. |
| 1.18 | Client portal: view completed jobs | `project` + `portal` | ⚙️ CONFIGURE | Same as above. Clients filter by stage. |
| 1.19 | Client portal: view invoices and outstanding balance | `account` + `portal` | ✅ USE AS-IS | `/my/invoices` page is built into Odoo portal. |
| 1.20 | Client notes visible on portal | `project` | 🔧 PARTIAL | Add `client_notes` field on task; expose in portal task template. |

**Division 1 Summary**: 11 × ✅/⚙️ (no code) · 4 × 🔧 (minor extension) · 3 × 🆕 (new models/crons)

---

## Division 2 — Contracting Division

| # | Requirement | Odoo CE Module | Status | What's Needed |
|---|-------------|----------------|--------|---------------|
| 2.1 | BOQ-based quotation | `sale` | ✅ USE AS-IS | Sale Order = quotation. Order lines = BOQ items. Item, description, qty, UoM, unit price, total. All built-in. |
| 2.2 | Unit of Measure on BOQ lines (m², m, pcs, lot) | `sale` + `uom` | ⚙️ CONFIGURE | Enable UoM in sale settings. Configure units. |
| 2.3 | Quotation PDF / print | `sale` | ✅ USE AS-IS | Built-in quotation report. Customise header/footer as needed. |
| 2.4 | Quotation stages (Draft → Sent → Confirmed) | `sale` | ✅ USE AS-IS | Built-in sale order states. |
| 2.5 | Client PO number and NPO number | `sale` | 🔧 PARTIAL | Extend `sale.order`: add `client_po_number` (Char) + `client_npo_number` (Char). |
| 2.6 | Contract value tracking | `sale` | ✅ USE AS-IS | `amount_total` on confirmed sale order = contract value. |
| 2.7 | Sale order → Project auto-link | `sale_project` | ✅ USE AS-IS | `sale_project` module (included in CE) links confirmed SO → project automatically. |
| 2.8 | Project stages (PO Received → In Progress → Completed → Closed) | `project` | ⚙️ CONFIGURE | Configurable project stages. No code. |
| 2.9 | Project progress monitoring | `project` | ✅ USE AS-IS | Task completion % + project stage built-in. |
| 2.10 | Project type (Glass Partition, Installation, Maintenance, etc.) | None | 🆕 CUSTOM | `ma.project.type` master model. Small. ~25 lines. |
| 2.11 | Link project type to sale order and project | `sale` + `project` | 🔧 PARTIAL | Add `project_type_id` field to both `sale.order` and `project.project`. |
| 2.12 | Advance invoice from sale order | `sale` + `account` | ✅ USE AS-IS | Built-in "Create Invoice → Down payment" on sale order. |
| 2.13 | Payment milestone schedule (advance / progress / retention / final) | None | 🆕 CUSTOM | New model `ma.project.payment` with type, amount, %, due date, status, linked invoice. Retention % field on project auto-creates retention milestone on project confirmation. |
| 2.14 | Link milestones to actual invoices and payments | `account` | 🔧 PARTIAL | Store `invoice_id` on each milestone; computed `state` from invoice payment status. |
| 2.15 | Total invoiced amount per project | `account` + `project` | 🔧 PARTIAL | Computed field on `project.project`: sum posted invoices for the partner+project. |
| 2.16 | Total received amount per project | `account` + `project` | 🔧 PARTIAL | Computed field: sum registered payments linked to project invoices. |
| 2.17 | Pending balance per project | Computed | 🔧 PARTIAL | `pending_balance = total_invoiced - total_received`. One computed field. |
| 2.18 | Overdue days per project | `account` | 🔧 PARTIAL | Compute from oldest unpaid invoice due date. |
| 2.19 | One-click client summary (value / invoiced / received / balance / overdue) | None | 🆕 CUSTOM | Smart button on `res.partner` → custom list view across all client projects with totals. |
| 2.20 | Project profitability tracking | `project` + `account` | 🔧 PARTIAL | Computed: `(contract_value - total_costs) / contract_value`. Costs from vendor bills. |
| 2.21 | Client ledger / SOA | `account` | ✅ USE AS-IS | Partner Ledger report. Filter by partner. |
| 2.22 | Payment ageing report | `account` | ✅ USE AS-IS | Aged Receivable report. Built-in with 30/60/90/120+ day buckets. |
| 2.23 | BOQ print report | `sale` | ⚙️ CONFIGURE | Customise sale order report header/footer for contracting look and feel. |
| 2.24 | Subcontracting: vendor / purchase order management | `purchase` | ✅ USE AS-IS | Purchase orders for subcontractors. Link to project via analytic accounts. |

**Division 2 Summary**: 9 × ✅/⚙️ (no code) · 9 × 🔧 (minor extension) · 3 × 🆕 (new models)

---

## Division 3 — Trading Division

| # | Requirement | Odoo CE Module | Status | What's Needed |
|---|-------------|----------------|--------|---------------|
| 3.1 | Inventory management | `stock` | ✅ USE AS-IS | Full warehouse and stock management built-in. |
| 3.2 | Multi-location stock tracking | `stock` | ✅ USE AS-IS | Multiple warehouses and locations supported. |
| 3.3 | Purchase orders and supplier invoices | `purchase` + `account` | ✅ USE AS-IS | Full PO → receipt → vendor bill flow built-in. |
| 3.4 | Sales orders and customer invoices | `sale` + `account` | ✅ USE AS-IS | Full quotation → SO → delivery → invoice flow built-in. |
| 3.5 | Stock tracking (lot / serial / FIFO / AVCO) | `stock` | ⚙️ CONFIGURE | Enable costing method and lot tracking in settings. |
| 3.6 | Customer ledger | `account` | ✅ USE AS-IS | Partner Ledger (receivable). Built-in. |
| 3.7 | Supplier ledger | `account` | ✅ USE AS-IS | Partner Ledger (payable). Built-in. |
| 3.8 | Profit tracking per sale | `sale` (margin) | ✅ USE AS-IS | `sale_management` includes margin on each order line. Profit = sale price − cost. |
| 3.9 | Reordering rules / min-max stock | `stock` | ⚙️ CONFIGURE | Reorder rules are built-in. Set min/max quantities per product. |
| 3.10 | Future retail / wholesale / e-commerce | `website_sale` | ✅ USE AS-IS | Standard Odoo e-commerce. Install when ready. |

**Division 3 Summary**: 8 × ✅/⚙️ (no code) · 0 × 🔧 · 0 × 🆕  — **No custom code required for Trading.**

---

## Common / Cross-Division Requirements

| # | Requirement | Odoo CE Module | Status | What's Needed |
|---|-------------|----------------|--------|---------------|
| C.1 | Full double-entry accounting | `account` | ✅ USE AS-IS | Full chart of accounts, journals, reconciliation. |
| C.2 | Customer invoices and receipts | `account` | ✅ USE AS-IS | Built-in. |
| C.3 | Supplier bills and payments | `account` + `purchase` | ✅ USE AS-IS | Built-in. |
| C.4 | Expense management | `hr_expense` | ✅ USE AS-IS | Employee expense reports, approval, reimbursement. |
| C.5 | Journal entries and adjustments | `account` | ✅ USE AS-IS | Manual journal entries built-in. |
| C.6 | Statement of Account (SOA) | `account` | ✅ USE AS-IS | Partner Ledger report. |
| C.7 | Client and supplier ledger | `account` | ✅ USE AS-IS | Partner Ledger (filter by receivable/payable). |
| C.8 | Payment ageing report | `account` | ✅ USE AS-IS | Aged Receivable + Aged Payable reports. |
| C.9 | Division tagging on invoices / orders / projects | None | 🔧 PARTIAL | Add `division_id` field (Many2one `ma.division`) to key models. |
| C.10 | Unified cross-division dashboard | None | 🆕 CUSTOM | OWL dashboard component in `ma_base`. KPIs from all divisions. |
| C.11 | Role-based access per division | Odoo core | ⚙️ CONFIGURE | Create security groups per division + record rules. Configured in XML. |
| C.12 | Employee records | `hr` | ✅ USE AS-IS | Departments, job positions, contracts. |
| C.13 | Leave / time-off management | `hr_holidays` | ✅ USE AS-IS | Leave types, requests, approval, calendar. |
| C.14 | Passport and National ID expiry tracking | `hr` | 🔧 PARTIAL | Extend `hr.employee` with expiry date fields. |
| C.15 | Visa / Labour Card / Health Card expiry | `hr` | 🔧 PARTIAL | Additional expiry fields on `hr.employee`. |
| C.16 | Employee document storage (scanned files) | None | 🆕 CUSTOM | `ma.hr.document` model with file binary, type, expiry. |
| C.17 | Document expiry alerts (30/15/7 day warnings) | None | 🆕 CUSTOM | Cron job scanning expiry dates → email HR manager. |
| C.18 | Document upload on any record | `mail` (Chatter) | ✅ USE AS-IS | Every model with `mail.thread` supports file attachments. |
| C.19 | Email notifications and reminders | `mail` + automated actions | ✅ USE AS-IS | Configure automated actions and email templates in UI. |
| C.20 | Multi-user login | Odoo core | ✅ USE AS-IS | Built-in. Unlimited users in CE. |
| C.21 | Cloud / browser access | Odoo core | ✅ USE AS-IS | Odoo is a web app. Deploy on any server or cloud. |
| C.22 | Arabic language (UI menus, forms) | `base` (i18n) | ⚙️ CONFIGURE | Install Arabic language pack from Settings → Languages. |
| C.23 | Arabic in custom reports and portal | Custom QWeb | 🔧 PARTIAL | Custom QWeb templates support both languages via translation strings. |
| C.24 | Multi-currency support | `account` | ⚙️ CONFIGURE | Enable multi-currency in accounting settings. Set rates. |

**Common Summary**: 14 × ✅/⚙️ (no code) · 5 × 🔧 (minor extension) · 3 × 🆕 (new logic/models)

---

## Consolidated Custom Build Summary

### New Models Required (🆕 CUSTOM)

| Model | Module | Purpose |
|-------|--------|---------|
| `ma.division` | `ma_base` | Division master data |
| `ma.service.type` | `ma_service` | Service category (Visa, PRO, Tourism, etc.) |
| `ma.service.contract` | `ma_service` | Monthly PRO contracts |
| `ma.service.contract.line` | `ma_service` | Services included per contract |
| `ma.project.type` | `ma_contracting` | Contracting project type |
| `ma.project.payment` | `ma_contracting` | Payment milestone schedule |
| `ma.hr.document` | `ma_hr_ext` | Employee document storage |
| `ma.hr.document.type` | `ma_hr_ext` | Document type master |

### Extensions to Existing Models (🔧 PARTIAL)

| Model Extended | Module | Fields / Logic Added |
|----------------|--------|---------------------|
| `project.task` | `ma_service` | `service_type_id`, `govt_ref`, `job_sequence`, `client_notes` |
| `project.project` | `ma_base` + `ma_contracting` | `division_id`, `project_type_id`, `client_po_number`, profitability computed fields |
| `sale.order` | `ma_base` + `ma_contracting` | `division_id`, `client_po_number`, `client_npo_number`, `project_type_id` |
| `account.move` | `ma_base` | `division_id` |
| `res.partner` | `ma_base` + `ma_contracting` | `division_ids`, `client_type`, project summary smart button |
| `hr.employee` | `ma_hr_ext` | Passport, National ID, Visa, Labour Card, Health Card fields |

### Cron Jobs Required

| Cron | Module | Frequency | Action |
|------|--------|-----------|--------|
| PRO contract monthly billing | `ma_service` | Daily | Generate invoice when billing_day == today |
| Contract expiry alert | `ma_service` | Daily | Email if contract ends within 30 days |
| Job overdue alert | `ma_service` | Daily | Flag/alert tasks past deadline with no completion |
| Document expiry alert | `ma_hr_ext` | Daily | Email HR at 60/30/15/7 days before any document expires |

---

## What Is NOT Required (Removed from Scope)

| Originally Considered | Reason Not Needed |
|-----------------------|-------------------|
| Custom portal module | Standard Odoo portal handles tasks (`/my/tasks`) and invoices (`/my/invoices`) out of the box |
| Custom trading module | 100% covered by `sale`, `purchase`, `stock`, `sale_management` |
| Custom SOA / ledger report | Already exists in `account` as Partner Ledger |
| Custom ageing report | Already exists as Aged Receivable / Aged Payable |
| Custom leave management | `hr_holidays` covers this completely |
| Custom email/notification system | `mail` + automated actions handles all notifications |
| Custom multi-user / access system | Odoo core groups and record rules handle this |
| Custom document attachment system | Chatter attachments available on every model |

---

## Effort Estimate by Module

| Module | Type | Estimated Files | Complexity |
|--------|------|----------------|------------|
| `ma_base` | Custom | ~15 files | Medium (OWL dashboard is the complex part) |
| `ma_service` | Custom + Extensions | ~18 files | Medium-High (contract model + crons + portal config) |
| `ma_contracting` | Custom + Extensions | ~20 files | High (payment milestones + profitability + smart button) |
| `ma_hr_ext` | Custom + Extensions | ~12 files | Low-Medium (mostly field extensions + cron) |
| Odoo standard setup | Config only | 0 files | Low (install + configure in UI) |

**Total custom files to build: ~65 files across 4 modules.**

---

*Generated: March 2026 | Odoo 18 Community Edition*
