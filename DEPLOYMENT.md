# Regulatory Intelligence Dashboard - Deployment Guide

## Overview

This is a full-stack regulatory intelligence system that:
- Scrapes official sources daily (RBI, IFSCA, SEBI, CBDT, Supreme Court, India Code)
- Classifies updates using Claude AI
- Displays results on a searchable, filterable dashboard
- Auto-deploys dashboard updates to Vercel

## Architecture

```
GitHub Repository (houses code + data)
  ├── Python Scraper (scraper.py)
  ├── Claude Classifier (classifier.py)
  ├── GitHub Actions Workflow (daily 8 AM IST)
  ├── Next.js Dashboard (pages/index.js)
  └── updates.json (data file)
     ↓
GitHub Actions (daily 8 AM IST)
  ├── Runs scraper.py
  ├── Runs classifier.py
  └── Commits updates.json to repo
     ↓
Vercel (auto-redeploys)
  ├── Fetches latest updates.json from GitHub
  └── Displays on dashboard (your-domain.vercel.app)
```

## Prerequisites

You'll need:
1. **GitHub Account** (free) - [Sign up here](https://github.com)
2. **Vercel Account** (free) - [Sign up here](https://vercel.com) - use GitHub to sign up
3. **Anthropic API Key** - [Get here](https://console.anthropic.com/account/keys)

**Time to set up:** ~30 minutes

---

## Step 1: Create GitHub Repository

### 1a. Create a new repository
1. Go to [github.com/new](https://github.com/new)
2. Name it: `regulatory-dashboard`
3. Make it **Private** (only you can see it)
4. Click **Create repository**

### 1b. Download this project to your computer
1. Create a folder called `regulatory-dashboard` somewhere convenient
2. Copy all these files into that folder:
   - `scraper.py`
   - `classifier.py`
   - `requirements.txt`
   - `package.json`
   - `next.config.js`
   - `tailwind.config.js`
   - `postcss.config.js`
   - `pages/index.js`
   - `.github/workflows/daily-scrape.yml`
   - `sample-updates.json` (rename to `updates.json` later)

### 1c. Create folder structure
Inside your local `regulatory-dashboard` folder, create these directories:
```
regulatory-dashboard/
├── pages/
├── data/
├── .github/
│   └── workflows/
└── (all the .py, .json, .js files from above)
```

Move the files to the right places:
- `pages/index.js` → `pages/` folder
- `daily-scrape.yml` → `.github/workflows/` folder
- `sample-updates.json` → `data/updates.json` (rename it)

### 1d. Push code to GitHub
1. Install [GitHub Desktop](https://desktop.github.com) (easiest option)
2. Open GitHub Desktop
3. Click **File → Clone Repository**
4. Find your `regulatory-dashboard` repo
5. Clone it to your computer
6. Drag all your local files into the cloned folder
7. In GitHub Desktop: **Publish branch** → push to GitHub

**Alternative (command line):**
```bash
cd regulatory-dashboard
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/regulatory-dashboard.git
git push -u origin main
```

---

## Step 2: Set Up GitHub Actions Secrets

GitHub Actions needs your Anthropic API key to run the classifier. This must be stored as a secret.

### 2a. Get your API key
1. Go to [console.anthropic.com/account/keys](https://console.anthropic.com/account/keys)
2. Click **Create Key**
3. Copy the key (you'll only see it once)

### 2b. Add it to GitHub
1. Go to your GitHub repo: `github.com/YOUR_USERNAME/regulatory-dashboard`
2. Click **Settings** (top right)
3. Click **Secrets and variables → Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: Paste your API key
7. Click **Add secret**

---

## Step 3: Create `.gitignore` File

This prevents sensitive files from being pushed to GitHub.

Create a file called `.gitignore` in your repo root with:
```
__pycache__/
*.pyc
.env
.env.local
node_modules/
.next/
.vercel/
dist/
.DS_Store
```

---

## Step 4: Deploy Dashboard to Vercel

### 4a. Connect GitHub to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **Sign Up**
3. Choose **Continue with GitHub**
4. Authorize Vercel to access your GitHub account
5. Click **Import Project**
6. Find `regulatory-dashboard` → Click **Import**

### 4b. Configure Vercel deployment
1. **Project name:** `regulatory-dashboard` (or whatever you want)
2. **Framework:** Next.js
3. **Root Directory:** ./
4. **Build Command:** `npm run build`
5. **Output Directory:** `.next`
6. Click **Deploy**

Vercel will deploy the dashboard. This takes ~2-3 minutes. Once done, you'll get a URL like `https://regulatory-dashboard.vercel.app`

### 4c. Important: Update the dashboard code with your GitHub username

Open `pages/index.js` in your editor and find this line (around line 50):
```javascript
const githubUser = 'YOUR_GITHUB_USERNAME';
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username, then:
1. Save the file
2. Push to GitHub (`git add . → git commit → git push`)
3. Vercel will auto-redeploy (watch for the deployment notification)

---

## Step 5: Test the System

### 5a. Manually run the scraper (optional)
You can test locally before relying on GitHub Actions:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Run scraper (creates data/updates.json with raw items)
python scraper.py

# Run classifier (adds Claude classification to each item)
python classifier.py
```

### 5b. Check GitHub Actions
1. Go to your repo on GitHub
2. Click **Actions** (top menu)
3. You should see the workflow: **Daily Regulatory Scrape & Classify**
4. If it hasn't run yet, click **Run workflow** (right side) to trigger it manually
5. Watch the logs to see if it succeeds

### 5c. View your dashboard
1. Go to your Vercel URL: `https://regulatory-dashboard.vercel.app`
2. You should see the dashboard (initially empty or with sample data)
3. Once GitHub Actions runs, the dashboard auto-refreshes and shows real data

---

## Step 6: Automated Daily Runs

The system is configured to run automatically every day at **8 AM IST** (2:30 AM UTC).

**How it works:**
1. GitHub Actions scheduler triggers the workflow at 8 AM IST
2. `scraper.py` pulls from all sources
3. `classifier.py` uses Claude to classify each item
4. Results are committed back to `updates.json` in GitHub
5. Vercel detects the change and auto-redeploys
6. Your dashboard shows fresh data within 5 minutes

**To manually trigger a run:**
1. Go to your GitHub repo
2. Click **Actions**
3. Click **Daily Regulatory Scrape & Classify**
4. Click **Run workflow** → **Run workflow** (green button)
5. Wait 2-3 minutes for results

---

## Monitoring & Troubleshooting

### Check if scraper ran successfully
1. Go to your GitHub repo → **Actions**
2. Click the latest workflow run
3. Click **scrape-and-classify** job
4. Read the logs

**Common issues:**

| Issue | Solution |
|-------|----------|
| "ANTHROPIC_API_KEY not found" | Check Step 2b - API key secret was set correctly |
| "No changes to commit" | No new items were scraped. Check if source URLs are still valid. |
| Dashboard shows "Error loading data" | Update `YOUR_GITHUB_USERNAME` in `pages/index.js` |
| Very few items scraped | Some government sites may require updates to selectors. See "Maintenance" below |

---

## Maintenance

### Updating source selectors
If a government site redesigns and stops showing items, you need to update the HTML selectors in `scraper.py`.

**Example:** If RBI notifications selector breaks:
1. Open RBI Press Releases in your browser
2. Right-click on a notification link → **Inspect** (F12)
3. Find the HTML selector pattern
4. Update the selector in `scraper.py` (line that says `'table tr td a'`, etc.)
5. Push to GitHub
6. Manually trigger GitHub Actions to test

### Adjusting classification prompts
If classifications aren't matching your needs:
1. Open `classifier.py`
2. Edit the `prompt` variable in the `classify_item()` function
3. Push to GitHub
4. Next daily run will use new logic

### Adding new sources
To add a new regulatory source (e.g., Ministry of Finance circulars):
1. Create a new scraper class in `scraper.py` (following the pattern of `RBIScraper`, etc.)
2. Add it to the `scrapers` list in `scrape_all_sources()`
3. Push to GitHub

---

## Dashboard Features

### Search & Filter
- **Search box:** Find updates by keyword, source, or topic
- **Category filter:** Narrow by regulatory category (FEMA, IFSCA, Succession, etc.)
- **Jurisdiction filter:** Show only India, Singapore, US, etc.
- **Impact level:** See only Critical, Important, or Informational
- **Sort:** By date (newest/oldest) or by impact level

### Information Display
Each update shows:
- **Title & Source:** What it is and where it came from
- **Impact Badge:** 🔥 Critical | ⚠️ Important | ℹ️ Informational
- **Category & Jurisdiction:** For quick filtering
- **One-line Summary:** What changed (in <15 words)
- **Why It Matters:** How it affects wealth planning and which clients it impacts
- **Source Link:** Click to read the full regulatory document
- **Confidence Score:** How confident Claude was in the classification (0-100%)

### Auto-Refresh
- Dashboard checks for new data every 30 minutes
- No need to refresh manually

---

## Cost Estimation

| Service | Cost/Month |
|---------|-----------|
| GitHub (public/private repos) | Free |
| Vercel (hobby plan) | Free |
| Anthropic API (at 20-40 items/day) | ~$2-5 |
| **Total** | **~$2-5/month** |

---

## File Structure Reference

```
regulatory-dashboard/
├── scraper.py                          # Pulls from RBI, IFSCA, SEBI, CBDT, etc.
├── classifier.py                       # Claude AI classification engine
├── requirements.txt                    # Python dependencies
├── package.json                        # Node.js dependencies
├── next.config.js                      # Next.js config
├── tailwind.config.js                  # Tailwind CSS (styling)
├── postcss.config.js                   # PostCSS config
├── .gitignore                          # Tells Git what to ignore
├── DEPLOYMENT.md                       # This file
├── pages/
│   └── index.js                        # Dashboard UI component
├── data/
│   └── updates.json                    # Scraped & classified data
├── .github/
│   └── workflows/
│       └── daily-scrape.yml            # GitHub Actions automation
└── node_modules/                       # Installed after `npm install`
```

---

## Next Steps

### Short term (Day 1-7)
- Deploy and test the system
- Run manual scrapes to verify data quality
- Fine-tune the dashboard filters based on your needs

### Medium term (Week 2-4)
- Monitor GitHub Actions logs for any scraper failures
- Adjust classification prompts if needed
- Add any new regulatory sources

### Long term (Month 2+)
- Build a knowledge graph (optional) - linking related updates
- Add email alerts for Critical updates
- Expand to secondary sources (law firm commentary, expert analysis)
- Create scenario cards based on trending regulatory changes

---

## Support & Questions

If something breaks:
1. Check GitHub Actions logs (most common issue)
2. Verify Anthropic API key is set as secret
3. Ensure `YOUR_GITHUB_USERNAME` is updated in `pages/index.js`
4. Try manually triggering the workflow to get error messages

---

**You're all set! Your regulatory intelligence system is now live.** 🎉
