# Social Scheduler CLI 📱

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Free social media scheduling from your terminal. Post to Twitter, LinkedIn, and Instagram with simple commands.

## Features

- ✨ **Free Tier**: 5 posts per week at no cost
- 🚀 **Premium**: Unlimited posts for just $8/month
- 🐦 **Twitter/X**: Automated posting with image support
- 💼 **LinkedIn**: Professional network posting
- 📸 **Instagram**: Photo and caption scheduling
- 📅 **Scheduling**: Queue posts for future dates
- 📄 **CSV Import**: Bulk schedule from spreadsheets
- 🖥️ **Terminal-first**: Perfect for developers and power users

## Installation

```bash
# Install from PyPI (when published)
pip install social-scheduler

# Or install from source
git clone https://github.com/entrebear/social-scheduler.git
cd social-scheduler
pip install -e .
```

### Prerequisites

- Python 3.9 or higher
- Playwright browsers (will be installed automatically)
- Social media accounts for platforms you want to use

## Quick Start

```bash
# Check status
sched status

# Configure Twitter
sched config --platform twitter --email your@email.com --password-input

# Post now
sched post --content "Hello from Social Scheduler!" --platforms twitter --now

# Schedule for later
sched post \
  --content "Scheduled post example" \
  --platforms twitter,linkedin \
  --schedule "2024-12-25 09:00"

# Import from CSV
sched import posts.csv
```

## Configuration

Social Scheduler stores credentials locally in your config directory:

| Platform  | Config Command                                      |
|-----------|-----------------------------------------------------|
| Twitter   | `sched config --platform twitter -e email -p pass` |
| LinkedIn  | `sched config --platform linkedin -e email -p pass`|
| Instagram | `sched config --platform instagram -e user -p pass`|

> ⚠️ Credentials are stored locally. Keep them secure!

## Usage Examples

### Post with Media
```bash
sched post \
  --content "Check out my new project!" \
  --platforms twitter,linkedin \
  --media ./screenshot.png \
  --hashtags "opensource,python,cli"
```

### Schedule Natural Language
```bash
# Schedule 2 hours from now
sched post \
  --content "Reminder!" \
  --platforms all \
  --schedule "in 2 hours"

# Schedule specific date/time
sched post \
  --content "Weekly update" \
  --platforms linkedin \
  --schedule "2024-06-15 14:30"
```

### View Scheduled Posts
```bash
sched scheduled
```

### Run Due Posts
```bash
# In a cron job or manually
sched run-scheduled
```

## CSV Import Format

Create a CSV file with your posts:

```csv
content,platforms,scheduled_time,media_paths,hashtags,link
"Hello World!",twitter,2024-06-15 09:00,,"greeting,hello",
"Project launch",linkedin,2024-06-16 10:00,./image.png,"launch,beta",https://example.com
"Photo post",instagram,in 1 hour,./photo.jpg,"photo,daily",
```

| Column         | Description                                           |
|----------------|-------------------------------------------------------|
| content        | Post text content                                     |
| platforms      | Comma-separated: twitter, linkedin, instagram, all    |
| scheduled_time | ISO format, natural language, or empty for immediate |
| media_paths    | Comma-separated file paths (optional)                 |
| hashtags       | Comma-separated without # (optional)                  |
| link           | URL to include (optional)                             |

See [examples/sample-posts.csv](examples/sample-posts.csv) for a full example.

## Platform Limits

| Platform  | Max Characters | Max Images |
|-----------|---------------|------------|
| Twitter   | 280           | 4          |
| LinkedIn  | 3,000         | 9          |
| Instagram | 2,200         | 10         |

## Pricing

### Free Tier
- ✅ 5 posts per week
- ✅ All platforms
- ✅ Basic scheduling
- ✅ CSV import
- ✅ Community support

### Premium ($8/month)
- 🚀 Unlimited posts
- 🚀 Bulk operations
- 🚀 Priority support
- 🚀 Analytics dashboard
- 🚀 API access (coming soon)

[Upgrade to Premium](https://buy.stripe.com/example) | [GitHub Sponsors](https://github.com/sponsors/entrebear)

## Running Scheduled Posts

Add to your crontab for automatic posting:

```bash
# Check every 15 minutes
*/15 * * * * /usr/bin/sched run-scheduled

# Or use with Poetry/pipx
*/15 * * * * /home/user/.local/bin/pipx run sched run-scheduled
```

## Development

```bash
# Clone repo
git clone https://github.com/entrebear/social-scheduler.git
cd social-scheduler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"

# Install playwright browsers
playwright install chromium

# Run tests
pytest tests/

# Format code
black src/ tests/
ruff check src/ tests/

# Type check
mypy src/
```

## Troubleshooting

### Login Issues
- Ensure 2FA is disabled for the accounts you want to automate
- Check that credentials are correct with `sched config`
- Try running with `--no-headless` to see the browser

### Rate Limits
Social Scheduler respects platform rate limits. If you hit limits:
- Wait a few minutes between posts
- Upgrade to Premium for better scheduling
- Use the `--headless` flag to reduce detection

### Media Upload Failures
- Ensure images are under platform size limits
- Supported formats: JPG, PNG, GIF (platform-dependent)
- Check file paths are correct and files exist

## Security

- Credentials stored in `~/.config/social-scheduler/` (Linux/Mac) or `%APPDATA%\social-scheduler` (Windows)
- No data sent to external servers except to social media platforms
- Open source - audit the code yourself!

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Roadmap

- [x] Twitter/X support
- [x] LinkedIn support
- [x] Instagram support
- [x] CSV import
- [x] Scheduling
- [ ] Analytics dashboard
- [ ] Webhook notifications
- [ ] Mastodon support
- [ ] TikTok support
- [ ] REST API

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- 💖 [GitHub Sponsors](https://github.com/sponsors/entrebear)
- ☕ [Buy Me a Coffee](https://www.buymeacoffee.com/entrebear)
- 📧 [Open an issue](https://github.com/entrebear/social-scheduler/issues)

---

Made with ❤️ by [OpenClaw](https://github.com/entrebear)
