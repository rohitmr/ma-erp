# MA ERP — Odoo 18 Community Edition

Custom ERP system built on Odoo 18 CE covering three business divisions:
- **Service** — PRO support, company formation, visa, tourism, document services
- **Contracting** — Glass installation, partitions, maintenance, supply & install
- **Trading** — General trading with inventory, purchase, and sales

## Custom Modules

| Module | Purpose |
|--------|---------|
| `ma_base` | Division master, security groups, unified dashboard |
| `ma_service` | Service job tracking, PRO contracts, recurring billing |
| `ma_contracting` | Project management, BOQ, payment milestones, retention |
| `ma_hr_ext` | Employee document & expiry tracking |

## Quick Start (Local Development)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd MA-NewERPproject

# 2. Start Odoo + PostgreSQL
docker compose up -d

# 3. Open browser
open http://localhost:8069
```

On first launch, create a new database named `ma_erp` with demo data off.

Then install modules in order:
1. `ma_base`
2. `ma_service`
3. `ma_contracting`
4. `ma_hr_ext`

See [SETUP.md](SETUP.md) for full installation and configuration guide.

## Project Structure

```
MA-NewERPproject/
├── docker-compose.yml
├── docker/
│   └── odoo.conf
├── addons/
│   ├── ma_base/
│   ├── ma_service/
│   ├── ma_contracting/
│   └── ma_hr_ext/
├── SETUP.md
├── PLAN.md
└── MODULE_MAPPING_REPORT.md
```
