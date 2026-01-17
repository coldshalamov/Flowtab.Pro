# Deployment Guide

## 1. Backend (Render.com)
We use a **Render Blueprint** to automate the entire backend setup (API + Database).

1. Push your latest code to GitHub.
2. Log in to [dashboard.render.com](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your `Flowtab.Pro` repository.
5. Render will automatically detect `render.yaml`.
6. Click **Apply**.
   - It will create a **PostgreSQL Database** (Free Tier).
   - It will create a **Web Service** (Python).
   - It will automatically link them and run migrations.

### Copy your Backend URL
Once deployed, copy your API URL (e.g., `https://flowtab-api.onrender.com`). You will need this for the frontend.

---

## 2. Frontend (Vercel)
We deploy the Next.js app to Vercel.

1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import `Flowtab.Pro` from GitHub.
4. **Important Configuration**:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click `Edit` and select `apps/web`.
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_BASE`: Paste your Render API URL (e.g., `https://flowtab-api.onrender.com`).
     - `NEXT_PUBLIC_ADMIN_KEY`: Copy the `ADMIN_KEY` from your Render Dashboard (Environment tab) if you want to enable submitting.

5. Click **Deploy**.

---

## 3. Domain Setup (GoDaddy)
You have `flowtab.pro`.

1. Go to your Vercel Project -> **Settings** -> **Domains**.
2. Add `flowtab.pro`.
3. Vercel will give you DNS records (A Record `76.76.21.21` or CNAME `cname.vercel-dns.com`).
4. Log in to **GoDaddy** -> DNS Management for `flowtab.pro`.
5. Update the records to match Vercel's instructions.
   - **Type A**: Name `@`, Value `76.76.21.21` (or whatever Vercel says).
   - **Type CNAME**: Name `www`, Value `cname.vercel-dns.com`.

### Optional: Custom API Domain
If you want `api.flowtab.pro`:
1. Go to Render -> Web Service -> Settings -> Custom Domains.
2. Add `api.flowtab.pro`.
3. Add the CNAME record in GoDaddy (Name `api`, Value `flowtab-api.onrender.com`).
