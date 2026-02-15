# Social Scheduler Examples

This directory contains example files demonstrating how to use Social Scheduler.

## CSV Import Format

CSV files should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| content | Post text (required) | "Hello World!" |
| platforms | Comma-separated platforms (required) | twitter,linkedin,all |
| scheduled_time | When to post (optional) | 2024-03-15 09:00, "in 2 hours" |
| media_paths | Comma-separated image paths (optional) | /path/to/image.png |
| hashtags | Comma-separated hashtags without # (optional) | opensource,cli |
| link | URL to include (optional) | https://example.com |

## Example Files

- **sample-posts.csv** - Mixed examples showing various features
- **bulk-schedule.csv** - Weekly content schedule example
- **minimal.csv** - Simple version with only required fields

## Usage

```bash
# Import with preview
sched import examples/sample-posts.csv --dry-run

# Import and execute
sched import examples/sample-posts.csv

# Simple CSV (just content and platforms)
sched import examples/minimal.csv
```

## Creating Your Own CSV

1. Use your preferred spreadsheet program (Excel, Google Sheets, etc.)
2. Create columns matching the format above
3. Export as CSV
4. Validate with `sched import file.csv --dry-run`
5. Execute with `sched import file.csv`

## Tips

- **Content**: Twitter limited to 280 chars, others to 2000
- **Media**: Use absolute paths for best results
- **Schedule**: Use "in X minutes/hours/days" for relative times
- **Platforms**: Use "all" to post to every configured platform

## Sample Minimal CSV

```csv
content,platforms
"Simple post",twitter
"Another post",linkedin
```
