# Social Scheduler CLI

**Free social media scheduler (5 posts/week) – built with Python & Playwright**

<img src="demo.gif" alt="Demo GIF" width="600"/>

---

## What does it do?

- Schedule posts to **Twitter / X**, **LinkedIn**, and **Instagram** from a simple CSV file.
- Uses Playwright to automate the web UI, so you don't need official APIs.
- Free tier allows **5 posts per week** (perfect for small creators).
- Upgrade to an **$8/mo unlimited premium** tier (no code changes required).

---

## Quick Install

```bash
# Install Playwright browsers first (only needed once)
pip install playwright
playwright install

# Install the CLI (editable mode during development)
git clone https://github.com/entrebear/social-scheduler.git
cd social-scheduler
pip install -e .
```

Now you have the `sched` (or `social-scheduler`) command available.

---

## Configuration

```bash
# Configure each platform (you’ll be prompted for email/password)
# Example for Twitter/X:
sched config twitter

# Repeat for LinkedIn and Instagram
sched config linkedin
sched config instagram
```

Credentials are stored in `~/.config/social-scheduler/config.json` (plain‑text – please consider encrypting for production).

---

## CSV Format

| column | description |
|---|---|
| **content** | Text of the post (required) |
| **platforms** | Comma‑separated list: `twitter,linkedin,instagram` or `all` |
| **scheduled_time** | ISO‑8601 datetime (e.g., `2026-02-20T14:00:00Z`). Leave empty to post now |
| **media_paths** | Comma‑separated local file paths (images) |
| **alt_text** | Alt text for images (optional) |
| **hashtags** | Comma‑separated hashtags (without `#`) |
| **link** | Optional link to append |

Create a file `posts.csv`:

```csv
content,platforms,scheduled_time,media_paths,alt_text,hashtags,link
"Hello world!",twitter,2026-02-22T10:00:00Z,,,"hello,world",
"Check out our new blog post",all,,/path/to/image.png,"A screenshot",blog,https://example.com/blog
```

---

## Posting

### Immediate posting

```bash
sched run posts.csv
```

### Schedule for later

```bash
sched run posts.csv --schedule
# Later, when you want to fire due posts:
sched run-scheduled
```

---

## Premium Upgrade

If you hit the free‑tier limit, you’ll see a prompt with a Stripe link:

```
https://buy.stripe.com/example
```

Run the following command with the API key you receive after purchase:

```bash
sched upgrade YOUR_STRIPE_API_KEY
```

---

## Demo Video

A short demo video (GIF) is included in the repository (`demo.gif`).

---

## Contributing

Feel free to open issues or PRs. This project is MIT‑licensed.

---

## License

MIT © 2026 OpenClaw
