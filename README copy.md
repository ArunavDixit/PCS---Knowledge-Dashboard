# Regulatory Intelligence Dashboard

Private Client Solutions regulatory knowledge hub. Automated daily scraping and classification of updates from RBI, IFSCA, SEBI, CBDT, Supreme Court, and India Code.

## Features

✅ **Automated daily scraping** at 8 AM IST  
✅ **Claude AI classification** - categories, impact levels, "why it matters"  
✅ **Searchable dashboard** - filter by category, jurisdiction, impact  
✅ **Real-time deployment** - Vercel auto-redeploys on data updates  
✅ **Zero-maintenance infrastructure** - runs on GitHub Actions + Vercel free tiers  

## Dashboard

Live at: `https://regulatory-dashboard.vercel.app` (replace with your Vercel domain)

### What you see
- **Today's feed** sorted by impact level (🔥 Critical | ⚠️ Important | ℹ️ Informational)
- **Category filters** - Succession & Estate, FEMA, IFSCA/GIFT City, Cross-Border Tax, etc.
- **Jurisdiction filters** - India, Singapore, US, UAE, UK, etc.
- **Search** - find updates by keyword
- **One-line summary** - what changed
- **Why it matters** - how it affects wealth planning

## Data Sources

| Source | Content | Frequency |
|--------|---------|-----------|
| **RBI** | FEMA notifications, circulars, press releases | Daily |
| **IFSCA** | GIFT City circulars, notifications, press releases | Daily |
| **SEBI** | Circulars on AIFs, PMS, family offices | Daily |
| **CBDT** | Income tax circulars, wealth/trust taxation | Daily |
| **Supreme Court** | Judgments on succession, estate planning | Daily |
| **India Code** | Indian Succession Act, Hindu Succession Act (amendments) | Daily |

## Quick Start

**⏱️ ~30 minutes to full deployment**

### 1. Prerequisites
- GitHub account (free)
- Vercel account (free - sign up with GitHub)
- Anthropic API key ([get here](https://console.anthropic.com/account/keys))

### 2. Deploy
See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

### 3. Test
- GitHub Actions will run first time at 8 AM IST tomorrow
- Or manually trigger via GitHub Actions UI
- Dashboard loads at your Vercel URL

## Project Structure

```
.
├── scraper.py              # Pulls from 6 regulatory sources
├── classifier.py           # Claude AI classification
├── requirements.txt        # Python deps
├── package.json            # Node deps
├── pages/index.js          # Dashboard UI
├── data/updates.json       # Scraped & classified items
├── .github/workflows/      # GitHub Actions automation (8 AM IST daily)
└── DEPLOYMENT.md           # Full deployment guide
```

## How It Works

```
Every day at 8 AM IST:
1. GitHub Actions triggers the workflow
2. scraper.py pulls from RBI, IFSCA, SEBI, CBDT, SC, India Code
3. classifier.py uses Claude API to tag each item
4. updates.json is committed to GitHub
5. Vercel detects change and auto-redeploys
6. Your dashboard shows fresh data within 5 minutes
```

## Classifications

Each update is tagged with:
- **Category** (e.g., "FEMA & Foreign Exchange", "Succession & Estate Planning")
- **Jurisdiction** (e.g., "India", "Singapore", "US")
- **Impact Level** (Critical / Important / Informational)
- **One-line summary** (what changed, in <15 words)
- **Why it matters** (how it affects wealth planning)
- **Confidence score** (Claude's certainty in classification)

## Cost

| Service | Cost/Month |
|---------|-----------|
| GitHub | Free |
| Vercel | Free (hobby plan) |
| Anthropic API | ~$2-5 (at 20-40 items/day) |
| **Total** | **~$2-5/month** |

## Maintenance

### Common tasks
- **Add a source:** Create new scraper class, add to main scraper
- **Adjust classifications:** Edit prompt in `classifier.py`
- **Fix broken selectors:** Update HTML selectors in `scraper.py` if sites redesign
- **View logs:** GitHub Actions → latest workflow run

### Monitoring
Check GitHub Actions logs if:
- Scraper produces no items
- Classifier fails
- Deployment breaks

## Configuration

Edit these if needed:

### Timing
Change 8 AM IST cron time in `.github/workflows/daily-scrape.yml`:
```yaml
- cron: '30 2 * * *'  # 8 AM IST = 2:30 AM UTC
```

### API Model
Change Claude model in `classifier.py`:
```python
model="claude-haiku-4-5-20251001"  # Current setting
```

### Categories & Filters
Edit `CATEGORIES`, `JURISDICTIONS`, `IMPACT_LEVELS` in `classifier.py` to match your needs.

## Next Steps

1. **Deploy** following [DEPLOYMENT.md](./DEPLOYMENT.md)
2. **Test** by manually running GitHub Actions workflow
3. **Monitor** first week's scrapes and classifications
4. **Iterate** - adjust prompts, add sources, refine categories

## License

Private use only.

---

Built for the Private Client Solutions desk. Questions? Check [DEPLOYMENT.md](./DEPLOYMENT.md).
