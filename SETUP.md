# MA ERP — Setup & Deployment Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | Latest | https://www.docker.com/products/docker-desktop |
| Docker Compose | v2+ | Included with Docker Desktop |
| Git | Any | Pre-installed on Mac/Linux |

---

## Local Development Setup

### Step 1 — Clone the repository

```bash
git clone <your-github-repo-url>
cd MA-NewERPproject
```

### Step 2 — Start the containers

```bash
docker compose up -d
```

This starts:
- **PostgreSQL 15** on internal port 5432
- **Odoo 18** on port **8069**

First start takes 2–3 minutes to pull images.

### Step 3 — Create the database

1. Open **http://localhost:8069**
2. You will see the Odoo database creation screen
3. Fill in:
   - **Database Name**: `ma_erp`
   - **Email**: your admin email
   - **Password**: your admin password
   - **Language**: English
   - **Country**: (your country — affects currency and tax defaults)
   - **Demo Data**: ❌ **Leave unchecked**
4. Click **Create Database**

### Step 4 — Install standard modules

Go to **Apps** → Remove the "Apps" filter → search and install in this order:

1. `Accounting` (account)
2. `Sales` (sale_management)
3. `Purchase` (purchase)
4. `Inventory` (stock)
5. `Project` (project)
6. `Employees` (hr)
7. `Time Off` (hr_holidays)
8. `Portal` (portal)
9. `Sales Margin` (sale_margin) — for profit tracking on trading

### Step 5 — Install custom MA modules

Still in **Apps**, search for `MA` and install in this order:

1. **MA ERP Base** (`ma_base`)
2. **MA Service** (`ma_service`)
3. **MA Contracting** (`ma_contracting`)
4. **MA HR Extensions** (`ma_hr_ext`)

> If a module doesn't appear, go to **Settings → Activate developer mode**, then **Apps → Update Apps List**.

---

## Post-Installation Configuration

### 1. Company Settings
**Settings → Companies → Your Company**
- Set company name, logo, address
- Set currency (AED / QAR / SAR)
- Set fiscal year

### 2. Chart of Accounts
**Accounting → Configuration → Chart of Accounts**
- Select a localised chart of accounts (e.g. UAE or generic)
- Or import your own

### 3. Tax Configuration
**Accounting → Configuration → Taxes**
- Set up VAT or applicable taxes for your country
- Assign to product categories

### 4. Service Division Projects
**Project → Configuration → Projects → New**
- Create a project for each service category (e.g. "PRO Services 2026")
- Set Division = `Service`
- Set Privacy/Visibility = `Portal` (so clients can log in and see their jobs)
- Set Stages: New, Submitted, Under Process, Approved, Completed, Delivered

### 5. Contracting Division
**Project → Configuration → Projects → New**
- Create projects here as contracts are won
- Division = `Contracting`

### 6. Portal Access for PRO Clients
**Contacts → Open client record → Action → Grant Portal Access**
- Enter client's email
- Client receives invitation email to set up their login
- They can then view jobs at `/my/tasks` and invoices at `/my/invoices`

### 7. SMTP Email (for cron notifications)
**Settings → Technical → Email → Outgoing Mail Servers**
- Add your SMTP server credentials
- Test the connection

### 8. Arabic Language
**Settings → Translations → Languages → Activate Arabic**
- Install the Arabic language pack
- Users can switch language in their profile

---

## AWS Deployment

### Recommended Architecture

```
Internet
    │
    ▼
AWS EC2 (t3.medium or larger)
    ├── Docker: Odoo 18
    ├── Docker: PostgreSQL 15
    └── Nginx (reverse proxy + SSL)
```

### Step 1 — Launch EC2 Instance

- **AMI**: Ubuntu 22.04 LTS
- **Instance type**: `t3.medium` (2 vCPU, 4GB RAM) minimum; `t3.large` recommended
- **Storage**: 30GB gp3 root volume + 50GB additional EBS for Odoo data
- **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### Step 2 — Connect and install Docker

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose plugin
sudo apt-get install docker-compose-plugin -y
```

### Step 3 — Clone the repository on the server

```bash
git clone <your-github-repo-url> /opt/ma_erp
cd /opt/ma_erp
```

### Step 4 — Update odoo.conf for production

Edit `/opt/ma_erp/docker/odoo.conf`:

```ini
admin_passwd = CHANGE_THIS_TO_A_STRONG_RANDOM_PASSWORD
workers = 4          # 2x CPU cores
max_cron_threads = 2
```

### Step 5 — Start the application

```bash
cd /opt/ma_erp
docker compose up -d
```

### Step 6 — Install Nginx and SSL (optional but recommended)

```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/ma_erp
```

Paste this config (replace `your-domain.com`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 720s;
        proxy_connect_timeout 720s;
    }

    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ma_erp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Step 7 — Set up automatic backups

```bash
# Create backup script
sudo nano /opt/ma_erp/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/ma_erp_backups

mkdir -p $BACKUP_DIR

# Backup database
docker exec ma_erp_db pg_dump -U odoo ma_erp | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup filestore
docker cp ma_erp_odoo:/var/lib/odoo/filestore $BACKUP_DIR/filestore_$DATE

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /opt/ma_erp/backup.sh

# Schedule daily backup at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ma_erp/backup.sh >> /var/log/ma_erp_backup.log 2>&1") | crontab -
```

---

## Useful Docker Commands

```bash
# View logs
docker compose logs -f odoo

# Restart Odoo only
docker compose restart odoo

# Stop everything
docker compose down

# Update custom modules after code changes
docker compose restart odoo
# Then in Odoo: Settings → Activate developer mode → Apps → Upgrade module

# Connect to database
docker exec -it ma_erp_db psql -U odoo ma_erp

# Shell into Odoo container
docker exec -it ma_erp_odoo bash
```

---

## Module Installation Order (Reference)

```
1. ma_base          → Foundation (must be first)
2. ma_service       → Requires ma_base
3. ma_contracting   → Requires ma_base
4. ma_hr_ext        → Requires ma_base
```

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Module not visible in Apps | Settings → Activate Developer Mode → Apps → Update Apps List |
| Dashboard shows zeros | Ensure divisions are seeded (Settings → Technical → ma.division) |
| Portal client cannot see jobs | Check project Privacy = Portal, and client has portal access granted |
| Cron not running | Settings → Technical → Automation → Scheduled Actions → check each MA cron is Active |
| Emails not sending | Settings → Technical → Email → Outgoing Mail Servers → configure and test |
