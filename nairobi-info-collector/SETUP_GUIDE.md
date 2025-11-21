# Nairobi Information Collector - Setup Guide

Complete step-by-step guide to set up and run the Nairobi Information Collector.

## Quick Start (5 minutes)

```bash
# 1. Navigate to project
cd nairobi-info-collector

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (basic)
cp .env.example .env

# 5. Run!
python main.py --mode single
```

## Detailed Setup

### 1. System Requirements

**Minimum:**
- Python 3.8+
- 2 GB RAM
- 1 GB disk space
- Internet connection

**Recommended:**
- Python 3.11+
- 4 GB RAM
- 5 GB disk space
- Stable internet (10 Mbps+)

### 2. Python Environment Setup

#### Option A: Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using conda

```bash
# Create conda environment
conda create -n nairobi-collector python=3.11

# Activate
conda activate nairobi-collector

# Install dependencies
pip install -r requirements.txt
```

### 3. API Keys Setup

#### Twitter/X API (Optional but Recommended)

1. **Create Developer Account**
   - Go to https://developer.twitter.com
   - Sign up for developer account
   - Create a new project

2. **Generate Keys**
   - Create a new app in your project
   - Generate API Key and Secret
   - Generate Bearer Token
   - Generate Access Token and Secret

3. **Add to .env**
   ```bash
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_SECRET=your_access_secret_here
   ```

#### YouTube API (Optional)

1. **Google Cloud Console**
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable YouTube Data API v3

2. **Create API Key**
   - Go to "Credentials"
   - Create API Key
   - Restrict key (optional but recommended)

3. **Add to .env**
   ```bash
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

#### Instagram (Optional)

For Instagram, you can use either:
- Instagram Graph API (requires Facebook Developer account)
- Instagrapi library with account credentials

```bash
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

**Note:** Using account credentials may violate Instagram's ToS. Use at your own risk.

### 4. Configuration

#### Basic Configuration

Edit `config/config.yaml` to customize:

```yaml
sources:
  news:
    - name: "Nation Africa"
      url: "https://nation.africa/kenya/nairobi"
      enabled: true
      priority: high

collection:
  intervals:
    news: 15        # Collect every 15 minutes
    social_media: 10
    government: 60

  limits:
    max_items_per_source: 100
    max_age_hours: 72  # Only collect items from last 72 hours
```

#### Advanced Configuration

- **Rate Limiting**: Adjust delays to respect API limits
- **Sources**: Add or remove sources
- **Categories**: Customize category keywords
- **Output**: Change output formats and locations

### 5. Testing the Setup

#### Test 1: Basic Import

```bash
python -c "from src.orchestrator import NairobiInfoOrchestrator; print('✓ Imports working')"
```

#### Test 2: Single News Scraper

```bash
python -c "
from src.scrapers import NewsScraper
scraper = NewsScraper('Test', 'https://nation.africa/kenya/nairobi')
items = scraper.scrape()
print(f'✓ Scraped {len(items)} items')
"
```

#### Test 3: Full Collection

```bash
python main.py --mode single --formats json
```

Check `data/` directory for output files.

### 6. Running the Application

#### Single Collection

Collect once and generate reports:

```bash
python main.py --mode single
```

Output will be saved in `data/` directory.

#### Continuous Collection

Run continuously every 30 minutes:

```bash
python main.py --mode continuous --interval 30
```

Press `Ctrl+C` to stop.

#### Custom Formats

Specify output formats:

```bash
python main.py --mode single --formats json markdown
```

#### Debug Mode

Run with detailed logging:

```bash
python main.py --mode single --log-level DEBUG
```

### 7. Docker Setup (Optional)

#### Using Docker

```bash
# Build image
docker build -t nairobi-collector .

# Run container
docker run -d \
  --name nairobi-collector \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  nairobi-collector
```

#### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f nairobi-collector

# Stop services
docker-compose down
```

### 8. Scheduling (Production)

#### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add entry to run every hour
0 * * * * /path/to/venv/bin/python /path/to/main.py --mode single
```

#### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., every hour)
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\main.py --mode single`

#### Using systemd (Linux)

Create `/etc/systemd/system/nairobi-collector.service`:

```ini
[Unit]
Description=Nairobi Information Collector
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/nairobi-info-collector
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py --mode continuous --interval 30
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable nairobi-collector
sudo systemctl start nairobi-collector
sudo systemctl status nairobi-collector
```

### 9. Monitoring

#### View Logs

```bash
# Real-time logs
tail -f logs/nairobi_collector.log

# Last 100 lines
tail -n 100 logs/nairobi_collector.log

# Search for errors
grep ERROR logs/nairobi_collector.log
```

#### Check Output

```bash
# List generated reports
ls -lh data/

# View latest JSON report
cat data/nairobi_report_*.json | head -50

# View latest markdown report
cat data/nairobi_report_*.md | less
```

### 10. Troubleshooting

#### Problem: Import Errors

```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

#### Problem: API Rate Limits

```bash
# Solution: Increase intervals in config.yaml
collection:
  intervals:
    news: 30      # Increase from 15 to 30 minutes
    social_media: 20
```

#### Problem: No Social Media Data

```bash
# Solution: Check API credentials
python -c "import os; print('Twitter:', os.getenv('TWITTER_BEARER_TOKEN'))"

# Add credentials to .env file
```

#### Problem: Low Relevance Scores

```bash
# Solution: Adjust relevance threshold
# Edit src/processors/data_processor.py
min_relevance_score = 0.2  # Lower threshold
```

#### Problem: Out of Memory

```bash
# Solution: Reduce limits in config.yaml
collection:
  limits:
    max_items_per_source: 50  # Reduce from 100
```

### 11. Performance Optimization

#### Parallel Processing

Enable parallel collection (default):

```bash
python main.py --mode single --parallel
```

#### Caching (Redis)

If using Redis:

```bash
# Install Redis
sudo apt-get install redis-server

# Add to .env
REDIS_URL=redis://localhost:6379/0
```

#### Database Storage

For large-scale deployments, use PostgreSQL:

```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
createdb nairobi_db

# Add to .env
DATABASE_URL=postgresql://user:password@localhost/nairobi_db
```

### 12. Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Ensure it's in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Restrict API keys**
   - Use separate keys for dev/prod
   - Restrict by IP if possible
   - Rotate keys regularly

3. **Set file permissions**
   ```bash
   chmod 600 .env
   chmod 700 logs/
   ```

4. **Use HTTPS only**
   - All API calls use HTTPS
   - Verify SSL certificates

### 13. Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
# If using systemd:
sudo systemctl restart nairobi-collector
```

### 14. Backup

```bash
# Backup data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/ config/

# Automated backup (add to cron)
0 0 * * * tar -czf /backups/nairobi_$(date +\%Y\%m\%d).tar.gz /path/to/nairobi-info-collector/data/
```

### 15. Getting Help

- **Check logs**: `logs/nairobi_collector.log`
- **Review documentation**: `README.md`
- **Run examples**: `python example_usage.py`
- **Debug mode**: `--log-level DEBUG`

## Next Steps

1. ✅ Complete setup
2. ✅ Run test collection
3. ✅ Configure API keys
4. ✅ Set up scheduling
5. ✅ Monitor first few runs
6. ✅ Customize configuration
7. ✅ Set up backups

## Support

For issues and questions:
- Check troubleshooting section
- Review error logs
- Consult README.md
- Open GitHub issue

---

**Happy Collecting! 🇰🇪**
