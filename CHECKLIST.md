# Pre-Deployment Checklist

Complete these steps in order before expecting the system to work.

## Phase 1: Accounts & Keys (5 min)

- [ ] GitHub account created (github.com)
- [ ] Vercel account created (vercel.com - sign in with GitHub)
- [ ] Anthropic API key generated (console.anthropic.com)
- [ ] Anthropic API key **copied and saved** somewhere safe

## Phase 2: GitHub Repository Setup (10 min)

- [ ] New GitHub repo created: `regulatory-dashboard`
- [ ] Repository set to **Private**
- [ ] All project files downloaded/copied locally
- [ ] Folder structure created:
  ```
  regulatory-dashboard/
  ├── pages/index.js
  ├── .github/workflows/daily-scrape.yml
  ├── data/updates.json (from sample-updates.json)
  ├── styles/globals.css
  └── (all .py, .js, .json files in root)
  ```
- [ ] `.gitignore` file created in repo root
- [ ] All files pushed to GitHub (via GitHub Desktop or git CLI)
- [ ] Verify on github.com that files appear in repo

## Phase 3: GitHub Secrets (3 min)

- [ ] Go to: `github.com/YOUR_USERNAME/regulatory-dashboard`
- [ ] Click **Settings** → **Secrets and variables** → **Actions**
- [ ] Create new secret:
  - Name: `ANTHROPIC_API_KEY`
  - Value: (your API key from Phase 1)
- [ ] Secret appears in list (value hidden)

## Phase 4: Vercel Deployment (5 min)

- [ ] Go to vercel.com
- [ ] Click **Add New** → **Project**
- [ ] Import your `regulatory-dashboard` repo from GitHub
- [ ] Project imported successfully
- [ ] First deployment completes (watch console)
- [ ] Get Vercel URL (like `https://regulatory-dashboard.vercel.app`)

## Phase 5: Configure Dashboard (2 min)

- [ ] Open `pages/index.js` in editor
- [ ] Find line ~50: `const githubUser = 'YOUR_GITHUB_USERNAME';`
- [ ] Replace with your actual GitHub username
- [ ] Save file
- [ ] Commit and push to GitHub:
  ```bash
  git add pages/index.js
  git commit -m "Update GitHub username"
  git push
  ```
- [ ] Vercel auto-redeploys (check vercel.com)
- [ ] Dashboard is now live at your Vercel URL

## Phase 6: Test the Scraper (5 min)

### Option A: Manual Local Test (optional)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-xxx...

# Run scraper
python scraper.py

# Run classifier
python classifier.py

# Check data/updates.json for results
```

### Option B: GitHub Actions Test (recommended)
- [ ] Go to GitHub repo → **Actions**
- [ ] Click **Daily Regulatory Scrape & Classify** workflow
- [ ] Click **Run workflow** → **Run workflow** (green button)
- [ ] Wait 2-3 minutes
- [ ] Job completes (check logs if it fails)
- [ ] Commits to `main` branch show new data
- [ ] Vercel auto-deploys (watch notification)

## Phase 7: View Results (1 min)

- [ ] Go to your Vercel URL: `https://your-domain.vercel.app`
- [ ] Dashboard loads with data
- [ ] Try searching/filtering
- [ ] Click a "View Source" link to verify it works

## Automatic Daily Runs

- [ ] GitHub Actions workflow scheduled to run daily at 8 AM IST
- [ ] First automatic run happens tomorrow at 8 AM IST
- [ ] Dashboard auto-refreshes ~5 min after scrape completes
- [ ] No manual intervention needed

---

## Verification Checklist

After deployment, verify these work:

| Item | How to Test | Expected Result |
|------|-------------|-----------------|
| Scraper | GitHub Actions logs | No errors, items scraped |
| Classifier | GitHub Actions logs | Items classified with tags |
| Data file | Check `data/updates.json` | JSON with classified items |
| Dashboard | Visit Vercel URL | Page loads, shows data |
| Search | Type in search box | Results filter in real-time |
| Filters | Change category filter | Results update instantly |
| Auto-refresh | Wait 30 min, refresh | New data appears (if available) |
| GitHub Actions | Check Actions tab | Daily workflow runs at 8 AM IST |

---

## Common Issues & Fixes

### "Error loading data" on dashboard
**Cause:** GitHub username not updated in code  
**Fix:** See Phase 5 - replace `YOUR_GITHUB_USERNAME` with your actual username

### No items appear in dashboard
**Cause:** Scraper hasn't run yet OR API key not set  
**Fix:** 
1. Check GitHub Actions logs for errors
2. Verify `ANTHROPIC_API_KEY` secret was set (Phase 3)
3. Manually trigger workflow to test

### "ANTHROPIC_API_KEY" not found error
**Cause:** Secret wasn't created or name is wrong  
**Fix:** Go to GitHub Settings → Secrets, verify secret name is exactly `ANTHROPIC_API_KEY`

### Workflow keeps failing
**Cause:** Usually scraper selectors broke (sites redesigned)  
**Fix:** Check GitHub Actions logs for specific error, update selectors in `scraper.py`

### Dashboard shows old data
**Cause:** Vercel cache not cleared  
**Fix:** Hard refresh (Ctrl+Shift+R or Cmd+Shift+R), wait 5 min

---

## Next Steps After Deployment

1. **Monitor first week** - check GitHub Actions logs for any failures
2. **Review classifications** - adjust Claude prompts if needed
3. **Add sources** - consider adding law firm commentary as Tier 2
4. **Build knowledge graph** (optional) - link related regulatory changes
5. **Set up alerts** (future) - email/WhatsApp notifications for Critical items

---

## Support

If you're stuck:
1. Check this checklist for where you are
2. Read DEPLOYMENT.md for detailed step-by-step
3. Check GitHub Actions logs for actual error messages
4. Verify all secrets and configurations match this checklist

**You've got this.** ✨
