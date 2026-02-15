---
title: "Social Scheduler CLI: Schedule Social Media Posts from Your Terminal"
published: false
description: "Introducing Social Scheduler CLI - a free, open-source tool for developers to schedule and automate social media posts from the command line."
tags: python, cli, opensource, socialmedia, automation
cover_image: https://raw.githubusercontent.com/entrebear/social-scheduler/main/assets/social-scheduler-banner.png
series:
---

# Social Scheduler CLI: Schedule Social Media Posts from Your Terminal 📱

As developers, we spend most of our time in the terminal. Why should social media management be any different? Today I'm excited to introduce **Social Scheduler CLI** - a free, open-source tool that lets you schedule and automate social media posts directly from your command line.

## Why I Built This

I was tired of complex social media management tools that:
- Required browser tabs to stay open
- Charged $50+ per month for basic scheduling
- Made simple tasks complicated
- Tracked more data than necessary

As a developer, I wanted something simple: **write my post, run a command, done.**

## Features

Social Scheduler CLI supports:

- 🐦 **Twitter/X** - Post with images, hashtags, links
- 💼 **LinkedIn** - Professional network posting
- 📸 **Instagram** - Photo and caption scheduling
- 📅 **Smart Scheduling** - Natural language ("in 2 hours", "tomorrow at 9am")
- 📄 **CSV Import** - Bulk schedule entire weeks of content
- 🆓 **Free Tier** - 5 posts per week at no cost

## Quick Start

### Installation

```bash
pip install social-scheduler

# Or with pipx for isolated installs
pipx install social-scheduler
```

### Configure Your Accounts

```bash
# Set up Twitter
sched config --platform twitter -e your@email.com --password-input

# Set up LinkedIn
sched config --platform linkedin -e your@email.com --password-input

# Set up Instagram
sched config --platform instagram -e username --password-input
```

### Post Now

```bash
sched post \
  --content "Just shipped a new feature! 🚀" \
  --platforms twitter \
  --hashtags "opensource,producthunt"
```

### Schedule for Later

```bash
sched post \
  --content "Weekly update thread dropping in 1 hour" \
  --platforms twitter,linkedin \
  --schedule "in 1 hour"
```

### Import from CSV

```csv
content,platforms,scheduled_time,hashtags
"Monday motivation post",twitter,2024-03-18 08:00,motivation
"LinkedIn thought leadership",linkedin,2024-03-18 09:00,leadership
"Instagram photo",instagram,in 2 hours,photography
```

```bash
sched import posts.csv
```

## My Favorite Feature: Natural Language Scheduling

The scheduling syntax uses human-friendly expressions:

```bash
sched post -c "Launch day!" -p twitter -s "tomorrow at 9am"
sched post -c "Weekend post" -p all -s "in 3 days"
sched post -c "Quick update" -p linkedin -s "2024-12-25 14:30"
```

No need to remember ISO formats or timestamps!

## Pricing

I believe in sustainable open source:

**Free Tier** (no credit card required):
- 5 posts per week
- All platforms
- Basic scheduling
- CSV imports
- Community support

**Premium** ($8/month):
- Unlimited posts
- Bulk operations
- Priority support
- Analytics (coming soon)

The free tier covers most solo developers and indie hackers. Premium helps fund development.

## How It Works

Under the hood, Social Scheduler uses:
- **Playwright** for browser automation
- **Click** for CLI interface
- **Pydantic** for data validation
- **Rich** for beautiful terminal output

All authentication is local - no OAuth tokens stored on remote servers, no tracking, no analytics.

## Open Source

The entire codebase is open source:

```bash
git clone https://github.com/entrebear/social-scheduler.git
```

- MIT Licensed
- Contributions welcome
- Security audited
- Docker support coming

## Real-World Use Cases

**Developer Advocates:** Schedule weekly content across platforms

**Indie Hackers:** Batch-create a month's worth of product updates

**Open Source Maintainers:** Announce releases across Twitter and LinkedIn

**Content Creators:** Queue up your weekly newsletter promotions

## Roadmap

- [ ] Analytics dashboard
- [ ] Webhook notifications
- [ ] Mastodon support
- [ ] REST API
- [ ] Docker image
- [ ] GitHub Actions integration

## Try It Out

```bash
pip install social-scheduler
sched status
```

Or star the repo to stay updated: [github.com/entrebear/social-scheduler](https://github.com/entrebear/social-scheduler)

---

Questions? Drop them in the comments! 👇

#opensource #cli #python #productivity
