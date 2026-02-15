"""CLI interface for Social Scheduler."""
from __future__ import annotations

import asyncio
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import click
from dateutil import parser as date_parser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from social_scheduler.scheduler import SocialScheduler, PlatformConfig
from social_scheduler.post import Post, Platform


console = Console()


def get_scheduler(headless: bool = True) -> SocialScheduler:
    """Get scheduler instance."""
    return SocialScheduler(headless=headless)


@click.group()
@click.version_option(version="1.0.0", prog_name="social-scheduler")
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Social Scheduler CLI - Free social media scheduling (5 posts/week)."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
def status() -> None:
    """Show current status and usage."""
    scheduler = get_scheduler()
    usage = scheduler.usage.get_usage_info()
    
    table = Table(title="Social Scheduler Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    tier_text = "Premium" if usage['is_premium'] else "Free (5 posts/week)"
    table.add_row("Tier", tier_text)
    table.add_row("Posts This Week", str(usage['posts_this_week']))
    
    remaining_text = "Unlimited" if usage['is_premium'] else str(usage['remaining_this_week'])
    table.add_row("Remaining This Week", remaining_text)
    table.add_row("Can Post", "Yes" if usage['can_post'] else "No")
    
    if not usage['is_premium']:
        table.add_row("Reset Date", usage['week_start'][:10])
    
    console.print(table)
    
    platforms_table = Table(title="Configured Platforms")
    platforms_table.add_column("Platform", style="cyan")
    platforms_table.add_column("Status", style="green")
    platforms_table.add_column("Email", style="yellow")
    
    for platform in [Platform.TWITTER, Platform.LINKEDIN, Platform.INSTAGRAM]:
        config = scheduler.platform_configs.get(platform)
        if config and config.is_configured():
            masked_email = config.email[:3] + "***" if config.email else "N/A"
            platforms_table.add_row(
                platform.value.title(), 
                "Configured", 
                masked_email
            )
        else:
            platforms_table.add_row(platform.value.title(), "Not Configured", "-")
    
    console.print(platforms_table)


@cli.command('config')
@click.option('--platform', '-p', required=True, 
              type=click.Choice(['twitter', 'linkedin', 'instagram'], case_sensitive=False),
              help='Platform to configure')
@click.option('--email', '-e', help='Email/username for the platform')
@click.option('--password', help='Password for the platform')
@click.option('--password-input', is_flag=True, help='Prompt for password interactively')
def configure(platform: str, email: str | None, password: str | None, password_input: bool) -> None:
    """Configure credentials for a social media platform."""
    scheduler = get_scheduler()
    
    console.print(Panel(f"Configure {platform.title()}", style="blue"))
    
    if not email:
        email = Prompt.ask(f"Enter your {platform} email/username")
    
    if password_input or not password:
        import getpass
        password = getpass.getpass(f"Enter your {platform} password: ")
    
    if not password:
        console.print("[red]Password is required[/red]")
        sys.exit(1)
    
    platform_enum = Platform.from_string(platform)
    scheduler.platform_configs[platform_enum] = PlatformConfig(
        email=email,
        password=password,
        enabled=True
    )
    scheduler.save_config()
    
    console.print(f"[green]{platform.title()} configured successfully![/green]")
    console.print("[yellow]Note: Credentials are stored locally. Keep them safe![/yellow]")


async def run_post(scheduler: SocialScheduler, post_obj: Post) -> None:
    """Execute the post."""
    results = await scheduler.post(post_obj)
    await scheduler.close()
    
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    if success_count == total_count:
        console.print(f"[green]Successfully posted to {success_count}/{total_count} platforms![/green]")
    else:
        console.print(f"[yellow]Posted to {success_count}/{total_count} platforms[/yellow]")
        for platform, (success, error) in results.items():
            if not success:
                console.print(f"[red]  {platform.value}: {error}[/red]")


@cli.command('post')
@click.option('--content', '-c', required=True, help='Post content/message')
@click.option('--platforms', '-p', required=True, 
              help='Platforms to post to (comma-separated: twitter,linkedin,instagram,all)')
@click.option('--media', '-m', multiple=True, help='Media file paths')
@click.option('--hashtags', '-h', help='Hashtags (comma-separated)')
@click.option('--link', '-l', help='Link to include')
@click.option('--alt-text', help='Alt text for images')
@click.option('--schedule', '-s', help='Schedule time (e.g., "2024-01-15 14:30" or "in 2 hours")')
@click.option('--headless/--no-headless', default=True, help='Run browser headless')
def create_post(
    content: str,
    platforms: str,
    media: tuple[str, ...],
    hashtags: str | None,
    link: str | None,
    alt_text: str | None,
    schedule: str | None,
    headless: bool
) -> None:
    """Create a new social media post."""
    scheduler = get_scheduler(headless=headless)
    
    # Parse platforms
    try:
        platform_list = Post.parse_platforms(platforms)
        if not platform_list:
            raise click.BadParameter("At least one platform is required")
    except ValueError as e:
        raise click.BadParameter(str(e))
    
    # Parse scheduled time
    scheduled_time: datetime | None = None
    if schedule:
        try:
            scheduled_time = datetime.fromisoformat(schedule)
        except ValueError:
            schedule_lower = schedule.lower()
            now_time = datetime.utcnow()
            
            if schedule_lower.startswith('in '):
                parts = schedule_lower[3:].strip().split()
                if len(parts) >= 2:
                    try:
                        amount = int(parts[0])
                        unit = parts[1].lower()
                        if 'minute' in unit:
                            scheduled_time = now_time + timedelta(minutes=amount)
                        elif 'hour' in unit:
                            scheduled_time = now_time + timedelta(hours=amount)
                        elif 'day' in unit:
                            scheduled_time = now_time + timedelta(days=amount)
                        else:
                            raise click.BadParameter(f"Unknown time unit: {unit}")
                    except ValueError:
                        raise click.BadParameter(f"Invalid schedule format: {schedule}")
            else:
                try:
                    scheduled_time = date_parser.parse(schedule)
                except Exception:
                    raise click.BadParameter(f"Could not parse schedule time: {schedule}")
    
    # Parse media paths
    media_paths = [Path(m) for m in media if m]
    for path in media_paths:
        if not path.exists():
            raise click.BadParameter(f"Media file not found: {path}")
    
    # Parse hashtags
    hashtag_list = []
    if hashtags:
        hashtag_list = [h.strip() for h in hashtags.split(',') if h.strip()]
    
    # Create post object
    post_obj = Post(
        content=content,
        platforms=platform_list,
        scheduled_time=scheduled_time,
        media_paths=media_paths,
        alt_text=alt_text,
        hashtags=hashtag_list,
        link=link,
    )
    
    # Display post summary
    console.print(Panel("Post Summary", style="blue"))
    console.print(f"Content: {content[:100]}..." if len(content) > 100 else f"Content: {content}")
    console.print(f"Platforms: {', '.join(p.value for p in platform_list)}")
    if scheduled_time:
        console.print(f"Scheduled for: {scheduled_time.isoformat()}")
    if media_paths:
        console.print(f"Media: {', '.join(str(p) for p in media_paths)}")
    
    # Execute or schedule
    if scheduled_time:
        # Schedule for later
        asyncio.run(scheduler.schedule_post(post_obj))
        console.print(f"[green]Post scheduled for {scheduled_time.isoformat()}[/green]")
    else:
        # Post now
        if Confirm.ask("Confirm and post now?"):
            asyncio.run(run_post(scheduler, post_obj))
        else:
            console.print("[yellow]Post cancelled[/yellow]")


@cli.command('import')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Preview without importing')
def import_csv(csv_file: str, dry_run: bool) -> None:
    """Import posts from CSV file."""
    scheduler = get_scheduler()
    path = Path(csv_file)
    
    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            posts = list(reader)
    except Exception as e:
        console.print(f"[red]Error reading CSV: {e}[/red]")
        sys.exit(1)
    
    console.print(Panel(f"Found {len(posts)} posts in CSV", style="blue"))
    
    # Preview posts
    table = Table(title="Posts to Import")
    table.add_column("#", style="cyan")
    table.add_column("Content", style="white")
    table.add_column("Platforms", style="green")
    table.add_column("Scheduled", style="yellow")
    
    for i, row in enumerate(posts, 1):
        content = row.get('content', '')[:50] + "..." if len(row.get('content', '')) > 50 else row.get('content', '')
        platforms = row.get('platforms', 'N/A')
        scheduled = row.get('scheduled_time', 'Immediate')
        table.add_row(str(i), content, platforms, scheduled)
    
    console.print(table)
    
    if dry_run:
        console.print("[blue]Dry run - no changes made[/blue]")
        return
    
    if not Confirm.ask(f"Import {len(posts)} posts?"):
        console.print("[yellow]Import cancelled[/yellow]")
        return
    
    # Import posts
    scheduled_count = 0
    immediate_count = 0
    error_count = 0
    
    for row in posts:
        try:
            post_obj = Post.from_csv_row(row)
            if post_obj.scheduled_time and post_obj.scheduled_time > datetime.utcnow():
                asyncio.run(scheduler.schedule_post(post_obj))
                scheduled_count += 1
            else:
                # Post immediately
                asyncio.run(run_post(scheduler, post_obj))
                immediate_count += 1
        except Exception as e:
            console.print(f"[red]Error importing post: {e}[/red]")
            error_count += 1
    
    console.print(f"[green]Imported: {scheduled_count} scheduled, {immediate_count} immediate[/green]")
    if error_count:
        console.print(f"[red]Errors: {error_count}[/red]")


@cli.command()
def scheduled() -> None:
    """Show all scheduled posts."""
    scheduler = get_scheduler()
    schedule_file = scheduler.data_dir / "scheduled.json"
    
    if not schedule_file.exists():
        console.print("[yellow]No scheduled posts found[/yellow]")
        return
    
    try:
        with open(schedule_file, 'r') as f:
            posts = json.load(f)
    except (json.JSONDecodeError, IOError):
        console.print("[red]Error reading scheduled posts[/red]")
        return
    
    if not posts:
        console.print("[yellow]No scheduled posts found[/yellow]")
        return
    
    table = Table(title="Scheduled Posts")
    table.add_column("#", style="cyan")
    table.add_column("Content Preview", style="white")
    table.add_column("Platforms", style="green")
    table.add_column("Scheduled Time", style="yellow")
    
    for i, post_data in enumerate(posts, 1):
        content = post_data.get('content', '')[:40] + "..."
        platforms = post_data.get('platforms', 'N/A')
        scheduled = post_data.get('scheduled_time', 'N/A')[:16]
        table.add_row(str(i), content, platforms, scheduled)
    
    console.print(table)


@cli.command('run-scheduled')
@click.option('--headless/--no-headless', default=True)
def run_scheduled(headless: bool) -> None:
    """Run all due scheduled posts."""
    scheduler = get_scheduler(headless=headless)
    
    async def execute():
        results = await scheduler.run_scheduled()
        await scheduler.close()
        return results
    
    results = asyncio.run(execute())
    
    if not results:
        console.print("[yellow]No posts due for posting[/yellow]")
        return
    
    console.print(f"[green]Processed {len(results)} scheduled posts[/green]")
    
    for result in results:
        post_data = result['post']
        result_data = result['result']
        
        content = post_data.get('content', '')[:40]
        console.print(f"\nPost: {content}...")
        
        for platform, (success, error) in result_data.items():
            if success:
                console.print(f"  [green]  {platform.value}: Success[/green]")
            else:
                console.print(f"  [red]  {platform.value}: {error}[/red]")


@cli.command()
def upgrade() -> None:
    """Show premium upgrade information."""
    """
    console.print(Panel("Upgrade to Premium", style="gold3"))
    console.print("[bold]Current: Free Tier (5 posts/week)[/bold]")
    console.print("[bold green]Premium: Unlimited Posts + Priority Support[/bold green]")
    console.print()
    console.print("Premium Features:")
    console.print("  • Unlimited posts (no weekly limit)")
    console.print("  • Bulk scheduling via CSV")
    console.print("  • Analytics dashboard")
    console.print("  • Priority support")
    console.print()
    console.print("Upgrade here: [link=https://buy.stripe.com/example]https://buy.stripe.com/example[/link]")
    console.print(" or: [link=https://github.com/sponsors/entrebear]GitHub Sponsors[/link]")


def main() -> None:
    """Entry point."""
    cli()


if __name__ == '__main__':
    main()