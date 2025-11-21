# Nairobi Information Collector

**Advanced Intelligence Retrieval Agent for Nairobi, Kenya**

A comprehensive, production-ready application that continuously collects, verifies, and synthesizes information about Nairobi from multiple reliable sources including news sites, government portals, social media platforms, and tourism networks.

## Features

### Multi-Source Data Collection

- **News Sources**: Nation Africa, Standard Media, Citizen Digital, Business Daily
- **Government & Public Services**: Nairobi City County, Kenya Open Data Portal
- **Tourism Platforms**: TripAdvisor, Lonely Planet, Google Maps
- **Social Media**: Twitter/X, Instagram, YouTube, TikTok, Facebook
- **Business & Tech**: TechCabal, CIO Africa, Startup Kenya

### Intelligent Processing

- **Relevance Scoring**: Automatically scores content based on Nairobi-related keywords
- **Sentiment Analysis**: Analyzes the sentiment of collected information
- **Deduplication**: Removes duplicate content from different sources
- **Verification**: Assigns reliability levels to sources
- **Categorization**: Organizes information into categories:
  - Breaking Updates
  - City Life & Alerts
  - Culture & Events
  - Business & Economy
  - Food & Nightlife
  - Transportation
  - Social Media Trends
  - Tourism & Experience
  - Governance & Public Services
  - Community Stories

### Report Generation

Generate comprehensive intelligence briefs in multiple formats:
- **JSON**: Structured data for API integration
- **Markdown**: Human-readable documentation
- **HTML**: Beautiful web-ready reports with styling

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**

```bash
cd nairobi-info-collector
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

```bash
# Social Media API Keys
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

YOUTUBE_API_KEY=your_youtube_api_key

# Optional: Database URLs
DATABASE_URL=postgresql://user:password@localhost:5432/nairobi_db
REDIS_URL=redis://localhost:6379/0
```

## Usage

### Single Collection Run

Collect information once and generate reports:

```bash
python main.py --mode single
```

### Continuous Collection

Run continuous collection at specified intervals:

```bash
python main.py --mode continuous --interval 30
```

### Custom Configuration

Use a custom configuration file:

```bash
python main.py --config config/custom_config.yaml
```

### Specify Output Formats

Choose output formats for reports:

```bash
python main.py --formats json markdown html
```

### Command Line Options

```
usage: main.py [-h] [--mode {single,continuous}] [--interval INTERVAL]
               [--config CONFIG] [--formats {json,markdown,html} [{json,markdown,html} ...]]
               [--log-level {DEBUG,INFO,WARNING,ERROR}] [--parallel]

options:
  --mode {single,continuous}
                        Collection mode: single run or continuous
  --interval INTERVAL   Interval in minutes for continuous mode (default: 30)
  --config CONFIG       Path to configuration file
  --formats {json,markdown,html} [{json,markdown,html} ...]
                        Output formats for reports
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level
  --parallel            Run collections in parallel (default: True)
```

## Project Structure

```
nairobi-info-collector/
├── config/                  # Configuration files
│   └── config.yaml         # Main configuration
├── data/                   # Output data and reports
├── logs/                   # Application logs
├── src/                    # Source code
│   ├── collectors/         # Social media API collectors
│   │   ├── twitter_collector.py
│   │   ├── instagram_collector.py
│   │   └── youtube_collector.py
│   ├── scrapers/           # Web scrapers
│   │   ├── news_scraper.py
│   │   ├── government_scraper.py
│   │   └── tourism_scraper.py
│   ├── processors/         # Data processing
│   │   ├── data_processor.py
│   │   └── report_generator.py
│   ├── models/             # Data models
│   │   ├── information_item.py
│   │   └── report.py
│   ├── utils/              # Utilities
│   │   ├── config_loader.py
│   │   ├── logger.py
│   │   └── text_processor.py
│   └── orchestrator.py     # Main orchestrator
├── tests/                  # Unit tests
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
└── README.md              # This file
```

## Configuration

### Main Configuration (config/config.yaml)

Customize data sources, collection intervals, and output settings:

```yaml
sources:
  news:
    - name: "Nation Africa"
      url: "https://nation.africa/kenya/nairobi"
      enabled: true
      priority: high

collection:
  intervals:
    news: 15        # minutes
    social_media: 10
    government: 60

  limits:
    max_items_per_source: 100
    max_age_hours: 72

output:
  formats:
    - json
    - markdown
    - html
```

## Output Examples

### JSON Report

```json
{
  "title": "Nairobi Intelligence Brief",
  "generated_at": "2025-01-21T10:00:00Z",
  "total_items": 150,
  "sections": [
    {
      "title": "Breaking Updates",
      "category": "breaking_updates",
      "items": [...]
    }
  ]
}
```

### Markdown Report

```markdown
# Nairobi Intelligence Brief

**Generated:** 2025-01-21 10:00:00 UTC
**Total Items:** 150

## Breaking Updates

### Traffic Alert: Thika Road Accident
**Summary:** Multiple vehicle collision on Thika Superhighway...
- **Source:** Nation Africa
- **Reliability:** High
- **Published:** 2025-01-21 09:30
```

## API Integration

### Programmatic Usage

```python
from src.orchestrator import NairobiInfoOrchestrator

# Initialize
orchestrator = NairobiInfoOrchestrator()

# Collect data
items = orchestrator.collect_all(parallel=True)

# Process and generate reports
output_files = orchestrator.process_and_generate_report(
    items,
    output_formats=['json', 'markdown', 'html']
)

print(f"Generated reports: {output_files}")
```

## Social Media APIs

### Twitter/X API

1. Apply for Twitter Developer Account: https://developer.twitter.com
2. Create a new project and app
3. Generate API keys and tokens
4. Add to `.env` file

### Instagram API

1. Instagram Graph API or use instagrapi library
2. Add credentials to `.env` file

### YouTube API

1. Create project in Google Cloud Console
2. Enable YouTube Data API v3
3. Create API key
4. Add to `.env` file

## Data Privacy & Ethics

- Only collect publicly available information
- Respect robots.txt and rate limits
- Follow each platform's Terms of Service
- Do not store personal data
- Implement proper data retention policies

## Performance

- **Parallel Processing**: Collections run concurrently
- **Rate Limiting**: Built-in delays to respect source limits
- **Caching**: Redis support for caching results
- **Efficient**: Processes 1000+ items in under 60 seconds

## Monitoring

- **Logging**: Comprehensive logging with loguru
- **Metrics**: Prometheus-compatible metrics (optional)
- **Error Tracking**: Sentry integration (optional)

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Troubleshooting

### API Rate Limits

If you encounter rate limit errors:
- Increase intervals in `config.yaml`
- Reduce `max_items_per_source`
- Use API keys with higher rate limits

### Missing Dependencies

Install additional dependencies:

```bash
pip install -r requirements.txt --upgrade
```

### Log Files

Check logs for errors:

```bash
tail -f logs/nairobi_collector.log
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review logs for error details

## Roadmap

- [ ] Add more social media platforms (TikTok, Facebook)
- [ ] Implement machine learning for better categorization
- [ ] Add real-time alerting system
- [ ] Create web dashboard for visualization
- [ ] Add database storage (PostgreSQL/MongoDB)
- [ ] Implement user authentication
- [ ] Add API endpoints for programmatic access
- [ ] Mobile app integration

## Acknowledgments

Built with:
- Beautiful Soup - Web scraping
- Scrapy - Advanced scraping framework
- Tweepy - Twitter API
- FastAPI - Web framework
- Pydantic - Data validation
- Loguru - Logging

---

**Made with ❤️ for Nairobi, Kenya**
