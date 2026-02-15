"""Command line interface for Social Scheduler.

Provides commands:
- `sched` (or `social-scheduler`) – entry point.
- `status` – show usage info.
- `config` – set platform credentials.
- `schedule` – schedule posts from CSV.
- `run-scheduled` – run due scheduled posts.
- `post` – post a single entry from CSV row (or arguments).
- `upgrade` – activate premium.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from social_scheduler import SocialScheduler, Post, Platform

console = Console()

@click.group()
@click.option("--headless/--no-headless", default=True, help="Run Playwright headless.")
@click.pass_context
def main(ctx: click.Context, headless: bool):
    """Social Scheduler CLI entry point."""
    scheduler = SocialScheduler(headless=headless)
    ctx.obj = {
        "scheduler": scheduler,
    }


@main.command()
@click.pass_context
def status(ctx: click.Context):
    """Show usage status and configuration summary."""
    scheduler: SocialScheduler = ctx.obj["scheduler"]
    usage = scheduler.usage.get_usage_info()
    table = Table(title="Social Scheduler Status")
    table.add_column("Metric")
    table.add_column("Value", style="cyan")
    table.add_row("Free tier limit", str(usage.get("limit")))
    table.add_row("Posts this week", str(usage.get("posts_this_week")))
    table.add_row("Remaining", str(usage.get("remaining_this_week")))
    table.add_row("Premium", "Yes" if usage.get("is_premium") else "No")
    console.print(table)
    
    # Show configured platforms
    config_table = Table(title="Configured Platforms")
    config_table.add_column("Platform")
    config_table.add_column("Enabled")
    config_table.add_column("Has credentials")
    for platform, cfg in scheduler.platform_configs.items():
        config_table.add_row(
            platform.value,
            "Yes" if cfg.enabled else "No",
            "Yes" if cfg.is_configured() else "No",
        )
    console.print(config_table)


@main.command()
@click.argument("platform", type=click.Choice([p.value for p in Platform if p != Platform.ALL]))
@click.option("--email", prompt=True, hide_input=False, help="Login email / username")
@click.option("--password", prompt=True, hide_input=True, help="Login password")
@click.pass_context
def config(ctx: click.Context, platform: str, email: str, password: str):
    """Configure credentials for a platform."""
    scheduler: SocialScheduler = ctx.obj["scheduler"]
    plat = Platform.from_string(platform)
    scheduler.platform_configs[plat] = scheduler.platform_configs.get(plat, PlatformConfig())
    scheduler.platform_configs[plat].email = email
    scheduler.platform_configs[plat].password = password
    scheduler.save_config()
    console.print(f"[green]✅ Configured {platform}[/green]")


@main.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--schedule", is_flag=True, help="Schedule posts instead of posting immediately")
@click.pass_context
def run(ctx: click.Context, csv_path: Path, schedule: bool):
    """Read CSV and post (or schedule) each row.
    CSV columns must match Post.from_csv_row expectations.
    """
    scheduler: SocialScheduler = ctx.obj["scheduler"]
    posts: List[Post] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                post = Post.from_csv_row(row)
                posts.append(post)
            except Exception as e:
                console.print(f"[red]⚠️  Failed to parse row: {e}[/red]")
    if not posts:
        console.print("[yellow]No valid posts found in CSV.[/yellow]")
        return
    
    async def _process():
        if schedule:
            for p in posts:
                await scheduler.schedule_post(p)
            console.print(f"[green]✅ Scheduled {len(posts)} posts.[/green]")
        else:
            for p in posts:
                result = await scheduler.post(p)
                console.print(f"Post result: {result}")
    
    import asyncio
    asyncio.run(_process())


@main.command(name="run-scheduled")
@click.pass_context
def run_scheduled(ctx: click.Context):
    """Run any posts that are scheduled and due."""
    scheduler: SocialScheduler = ctx.obj["scheduler"]
    async def _run():
        results = await scheduler.run_scheduled()
        if not results:
            console.print("[yellow]No scheduled posts due.[/yellow]")
            return
        for entry in results:
            console.print(f"[green]Posted scheduled entry:{entry['post'].get('content','')}[/green]")
    import asyncio
    asyncio.run(_run())


@main.command()
@click.argument("api_key")
@click.pass_context
def upgrade(ctx: click.Context, api_key: str):
    """Upgrade to premium tier using API key (placeholder)."""
    scheduler: SocialScheduler = ctx.obj["scheduler"]
    scheduler.usage.upgrade_to_premium(api_key)
    console.print("[green]✅ Upgraded to premium (local flag set).[/green]")


if __name__ == "__main__":
    main()
