# 🛡️ SecureHub — Cyber Security SaaS Starter Kit

> **Full-stack SaaS app** — Security Scanner + Data Center Monitor + AI Assistant + Affiliate System + Automated Email Reports. Ready to deploy and sell.

![Vue 3](https://img.shields.io/badge/Vue_3-TypeScript-blue) ![License](https://img.shields.io/badge/license-Commercial-green) ![Deploy](https://img.shields.io/badge/Deploy-Render.com-purple)

---

## 🚀 What You Get

A complete, production-ready SaaS application:

| Feature | Description |
|---|---|
| 🔍 **Security Scanner** | Scans any website for 7 HTTP security headers, grades A+ to F |
| 🖥️ **Data Center Monitor** | Real-time CPU, RAM, Network, Disk metrics with alert system |
| 🔧 **Fix Guides** | Copy-paste code snippets for Apache, Nginx, Node.js, WordPress |
| 📧 **Weekly Email Reports** | Automated security scans with beautiful HTML emails via Nodemailer |
| 🤖 **AI Assistant** | Powered by Claude (Anthropic) or Google Gemini (free tier) |
| 💳 **Digistore24 Payments** | German payment platform — Kreditkarte, PayPal, Sofort, Klarna |
| 👥 **Affiliate System** | 30% commission, referral tracking, partner dashboard |
| 🏠 **Landing Page** | Professional marketing page with pricing, FAQ, trust badges |
| 🔐 **Auth (Supabase)** | Login/Register or demo mode — works without any setup |
| 📄 **PDF Export** | Security report export (Pro feature gate) |

---

## 💻 Tech Stack

- **Frontend:** Vue 3 + TypeScript + Vite + Pinia
- **Backend:** Node.js + Express + TypeScript
- **Auth:** Supabase (optional — demo mode works without it)
- **Payments:** Digistore24 (webhook integration)
- **Email:** Nodemailer (SMTP — Gmail, SendGrid, etc.)
- **AI:** Anthropic Claude API + Google Gemini API
- **Deploy:** Render.com (render.yaml included)

---

## ⚡ Quick Start

### 1. Install

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file:

```env
# AI — choose one or both
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...              # free tier available

# Email Reports
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=SecureHub <your@gmail.com>

# Auth (optional)
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# Payments (optional)
VITE_DS24_PRO_LINK=https://www.digistore24.com/product/YOUR_ID
VITE_DS24_BUSINESS_LINK=https://www.digistore24.com/product/YOUR_ID
```

### 3. Run Development

```bash
npm run api:dev    # backend on port 3001
npm run dev        # frontend on port 5173 (new terminal)
```

### 4. Build & Deploy

```bash
npm run build      # builds frontend to dist/
npm run start      # serves frontend + API on one port
```

---

## 🌐 Deploy to Render.com

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect repo — Render auto-detects `render.yaml`
4. Add environment variables in Render Dashboard
5. Done — free tier works for getting started

---

## 📧 Email Reports Setup

**Gmail (easiest):**
1. Enable 2-Factor Authentication
2. Google Account → Security → App Passwords → create one for "Mail"
3. Use the 16-character password as `SMTP_PASS`

**Weekly Cron (Render Free sleeps after 24h):**
1. Sign up at [cron-job.org](https://cron-job.org) — free
2. Create job: `POST https://your-app.onrender.com/api/monitor/weekly-run`
3. Schedule: every Sunday 08:00

---

## 💳 Digistore24 Setup

1. Create account at [digistore24.com](https://www.digistore24.com)
2. Create two products: **Pro (19€/month)** and **Business (49€/month)**
3. Copy product links → add to `.env`
4. In Digistore24 → IPN/Webhook → set URL: `https://your-app.onrender.com/api/ds24/webhook`

---

## 👥 Affiliate System

Users register at `/affiliate` and get:
- Unique referral code (e.g. `MAXM3375`)
- Tracking link: `https://your-app.com?ref=MAXM3375`
- 30% commission on every sale (via Digistore24 webhook)
- Dashboard at `/affiliate/portal`

Data stored in `server/affiliates.json` — no database needed.

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/security/scan` | POST | Scan URL for security headers |
| `/api/dc/metrics` | GET | Data center metrics |
| `/api/monitor/add` | POST | Add site to monitoring |
| `/api/monitor/list` | GET | List monitored sites |
| `/api/monitor/remove` | POST | Remove site |
| `/api/monitor/scan-now` | POST | Immediate scan + email |
| `/api/monitor/weekly-run` | POST | Cron trigger for weekly scans |
| `/api/ds24/webhook` | POST | Digistore24 payment webhook |
| `/api/affiliate/register` | POST | Register as affiliate |
| `/api/affiliate/click` | POST | Track referral click |
| `/api/affiliate/stats/:code` | GET | Affiliate statistics |
| `/api/assist` | POST | AI assistant (SSE streaming) |
| `/api/chat` | POST | AI chat (SSE streaming) |

---

## 📁 Project Structure

```
securehub/
├── src/
│   ├── views/
│   │   ├── Landing.vue           # Marketing landing page
│   │   ├── LoginPage.vue         # Auth (Supabase + demo mode)
│   │   ├── SecurityCenter.vue    # Scanner + Monitor + Email reports
│   │   ├── PricingPage.vue       # Plans + Digistore24 checkout
│   │   ├── AffiliatePage.vue     # Affiliate registration
│   │   └── AffiliatePortal.vue   # Affiliate dashboard
│   ├── stores/auth.ts            # Pinia auth store
│   └── router/index.ts           # Vue Router
├── server/
│   ├── index.ts                  # Express API + all endpoints
│   ├── affiliates.json           # Affiliate data (auto-created)
│   └── monitored-sites.json      # Monitoring data (auto-created)
└── render.yaml                   # Render.com deploy config
```

---

## 🛠️ Customization

**Rebrand:**
1. Find & replace `SecureHub` with your brand name
2. Update colors: `#3b82f6` → your brand color
3. Replace `🛡️` with your logo
4. Update contact email in `Landing.vue`

**Real server monitoring** (instead of simulated):
- Replace `simMetric()` in `server/index.ts` with Prometheus/Datadog/SSH calls

**Add database:**
- Replace JSON file storage (`affiliates.json`, `monitored-sites.json`) with PostgreSQL or Supabase

---

## NPM Scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Vite frontend (port 5173) |
| `npm run api:dev` | Express backend (port 3001) |
| `npm run dev:all` | Frontend + Backend parallel |
| `npm run build` | TypeCheck + production build |
| `npm run start` | Serve built app (frontend + API) |

---

## 📝 License

**Commercial License** — Use this code to build and sell your own SaaS. You may not resell or redistribute the source code itself.

---

## 🆘 Support

Questions? Open an issue or contact: **your@email.com**

> Built with Vue 3, Node.js, Anthropic Claude AI
