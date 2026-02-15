"""Main scheduler class with Playwright automation."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import appdirs
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from social_scheduler.post import Post, Platform

console = Console()


@dataclass
class PlatformConfig:
    """Configuration for a social media platform."""
    
    email: str | None = None
    password: str | None = None
    cookies_file: Path | None = None
    enabled: bool = True
    
    def is_configured(self) -> bool:
        """Check if the platform has required credentials."""
        return self.email is not None and self.password is not None


class UsageTracker:
    """Track free tier usage (5 posts/week)."""
    
    FREE_TIER_LIMIT = 5
    WEEK_IN_SECONDS = 7 * 24 * 60 * 60
    
    def __init__(self, data_dir: Path | None = None):
        """Initialize usage tracker."""
        self.data_dir = data_dir or Path(appdirs.user_data_dir("social-scheduler", "openclaw"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "usage.json"
        self._usage = self._load_usage()
    
    def _load_usage(self) -> dict[str, Any]:
        """Load usage data from file."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"posts_this_week": 0, "week_start": datetime.utcnow().isoformat(), "is_premium": False}
    
    def _save_usage(self) -> None:
        """Save usage data to file."""
        with open(self.usage_file, "w") as f:
            json.dump(self._usage, f, indent=2)
    
    def _is_new_week(self) -> bool:
        """Check if we need to reset the weekly counter."""
        week_start = datetime.fromisoformat(self._usage.get("week_start", "1970-01-01"))
        return (datetime.utcnow() - week_start).total_seconds() > self.WEEK_IN_SECONDS
    
    def can_post(self) -> tuple[bool, int]:
        """Check if user can post (returns can_post, remaining)."""
        if self._usage.get("is_premium", False):
            return True, float("inf")
        
        if self._is_new_week():
            self._usage["posts_this_week"] = 0
            self._usage["week_start"] = datetime.utcnow().isoformat()
        
        posts_this_week = self._usage.get("posts_this_week", 0)
        remaining = self.FREE_TIER_LIMIT - posts_this_week
        return remaining > 0, remaining
    
    def record_post(self, platform_count: int = 1) -> bool:
        """Record that a post was made."""
        if self._usage.get("is_premium", False):
            return True
        
        can_post, remaining = self.can_post()
        if not can_post:
            return False
        
        self._usage["posts_this_week"] = self._usage.get("posts_this_week", 0) + platform_count
        self._save_usage()
        return True
    
    def get_usage_info(self) -> dict[str, Any]:
        """Get current usage info for display."""
        can_post, remaining = self.can_post()
        return {
            "can_post": can_post,
            "posts_this_week": self._usage.get("posts_this_week", 0),
            "remaining_this_week": remaining,
            "limit": self.FREE_TIER_LIMIT,
            "is_premium": self._usage.get("is_premium", False),
            "week_start": self._usage.get("week_start", ""),
        }
    
    def upgrade_to_premium(self, api_key: str | None = None) -> bool:
        """Upgrade to premium tier."""
        # In real implementation, verify API key with server
        self._usage["is_premium"] = True
        self._save_usage()
        return True


class SocialScheduler:
    """Main scheduler class for social media posting."""
    
    def __init__(self, config_dir: Path | None = None, headless: bool = True):
        """Initialize the scheduler."""
        self.config_dir = config_dir or Path(appdirs.user_config_dir("social-scheduler", "openclaw"))
        self.data_dir = Path(appdirs.user_data_dir("social-scheduler", "openclaw"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.platform_configs: dict[Platform, PlatformConfig] = {}
        self.usage = UsageTracker(self.data_dir)
        self.headless = headless
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load platform configurations."""
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                
                for platform_name, config_data in data.get("platforms", {}).items():
                    try:
                        platform = Platform.from_string(platform_name)
                        self.platform_configs[platform] = PlatformConfig(
                            email=config_data.get("email"),
                            password=config_data.get("password"),
                            cookies_file=Path(config_data["cookies_file"]) if config_data.get("cookies_file") else None,
                            enabled=config_data.get("enabled", True),
                        )
                    except ValueError:
                        continue
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_config(self) -> None:
        """Save platform configurations."""
        config_file = self.config_dir / "config.json"
        data = {"platforms": {}}
        
        for platform, config in self.platform_configs.items():
            data["platforms"][platform.value] = {
                "email": config.email,
                "password": config.password,  # In production, encrypt this!
                "cookies_file": str(config.cookies_file) if config.cookies_file else None,
                "enabled": config.enabled,
            }
        
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2)
    
    async def _init_browser(self) -> None:
        """Initialize Playwright browser."""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self.headless)
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
    
    async def _close_browser(self) -> None:
        """Close Playwright browser."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if hasattr(self, "_playwright"):
            await self._playwright.stop()
        self._browser = None
        self._context = None
    
    async def _post_to_twitter(self, post: Post, page: Page) -> tuple[bool, str | None]:
        """Post to Twitter/X using Playwright."""
        try:
            config = self.platform_configs.get(Platform.TWITTER)
            if not config or not config.is_configured():
                return False, "Twitter not configured. Run: sched config --platform twitter"
            
            await page.goto("https://twitter.com/login", wait_until="networkidle")
            
            # Check if already logged in
            if "home" in page.url or "twitter.com/compose" in page.url:
                pass  # Already logged in
            else:
                # Login
                await page.fill('input[name="text"]', config.email)
                await page.click('text=Next / >>')
                await asyncio.sleep(1)
                await page.fill('input[name="password"]', config.password)
                await page.click('text=Log in / >>')
                await asyncio.sleep(3)
            
            # Navigate to compose tweet
            await page.goto("https://twitter.com/compose/tweet", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Fill tweet content
            content = post.get_full_content(max_length=280)
            await page.fill('[data-testid="tweetTextarea_0"]', content)
            await asyncio.sleep(1)
            
            # Upload media if any
            for media_path in post.media_paths[:4]:  # Twitter allows max 4 images
                if media_path.exists():
                    await page.set_input_files('input[type="file"]', str(media_path))
                    await asyncio.sleep(1)
            
            # Post tweet
            await page.click('[data-testid="tweetButton"]')
            await asyncio.sleep(3)
            
            return True, None
            
        except Exception as e:
            return False, f"Twitter error: {str(e)}"
    
    async def _post_to_linkedin(self, post: Post, page: Page) -> tuple[bool, str | None]:
        """Post to LinkedIn using Playwright."""
        try:
            config = self.platform_configs.get(Platform.LINKEDIN)
            if not config or not config.is_configured():
                return False, "LinkedIn not configured. Run: sched config --platform linkedin"
            
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Check if already logged in
            if "feed" in page.url:
                pass  # Already logged in
            else:
                # Login
                await page.fill('#username', config.email)
                await page.fill('#password', config.password)
                await page.click('button[type="submit"]')
                await asyncio.sleep(3)
            
            # Click start post button
            await page.click('button[data-control-name="share.post"], button:has-text("Start a post")')
            await asyncio.sleep(1)
            
            # Find the text editor and fill it
            content = post.get_full_content()
            await page.fill('.ql-editor[contenteditable="true"]', content)
            await asyncio.sleep(1)
            
            # Upload media if any
            for media_path in post.media_paths[:9]:  # LinkedIn allows max 9 images
                if media_path.exists():
                    await page.set_input_files('input[type="file"]', str(media_path))
                    await asyncio.sleep(2)
            
            # Click post button
            await page.click('button[aria-label="Post"]')
            await asyncio.sleep(3)
            
            return True, None
            
        except Exception as e:
            return False, f"LinkedIn error: {str(e)}"
    
    async def _post_to_instagram(self, post: Post, page: Page) -> tuple[bool, str | None]:
        """Post to Instagram using Playwright (via web)."""
        try:
            config = self.platform_configs.get(Platform.INSTAGRAM)
            if not config or not config.is_configured():
                return False, "Instagram not configured. Run: sched config --platform instagram"
            
            # Instagram web posting requires Creator Studio or developer API
            # For this CLI, we'll use a simplified web approach via instagram.com
            await page.goto("https://www.instagram.com/", wait_until="networkidle")
            
            # Check if already logged in
            try:
                await page.wait_for_selector('[aria-label="New post"]', timeout=5000)
            except:
                # Need to login
                await page.fill('input[name="username"]', config.email)
                await page.fill('input[name="password"]', config.password)
                await page.click('button[type="submit"]')
                await asyncio.sleep(4)
                await page.wait_for_selector('[aria-label="New post"]', timeout=10000)
            
            # Click new post
            await page.click('[aria-label="New post"]')
            await asyncio.sleep(1)
            
            # Select from computer
            if post.media_paths:
                await page.set_input_files('input[type="file"]', str(post.media_paths[0]))
            else:
                return False, "Instagram requires at least one image"
            
            await asyncio.sleep(2)
            await page.click('text=Next')
            await asyncio.sleep(1)
            await page.click('text=Next')
            await asyncio.sleep(1)
            
            # Write caption
            content = post.get_full_content()
            await page.fill('textarea[aria-label="Write a caption..."]', content)
            await asyncio.sleep(1)
            
            # Share
            await page.click('text=Share')
            await asyncio.sleep(5)
            
            return True, None
            
        except Exception as e:
            return False, f"Instagram error: {str(e)}. Note: Instagram web posting may require Creator Studio."
    
    async def post(self, post: Post) -> dict[Platform, tuple[bool, str | None]]:
        """Post to all configured platforms."""
        await self._init_browser()
        results = {}
        
        # Check free tier limit
        can_post, remaining = self.usage.can_post()
        is_premium = self.usage._usage.get("is_premium", False)
        
        if not can_post:
            console.print("[red]❌ Free tier limit reached! (5 posts/week)[/red]")
            console.print("[yellow]   Upgrade to premium for unlimited posts:[/yellow]")
            console.print("   https://buy.stripe.com/example")
            console.print("   or run: sched upgrade")
            return {}
        
        platforms = post.platforms
        if Platform.ALL in platforms:
            platforms = [Platform.TWITTER, Platform.LINKEDIN, Platform.INSTAGRAM]
        
        # Check if we have enough quota
        if not is_premium and len(platforms) > remaining:
            console.print(f"[yellow]⚠️  Only {remaining} posts remaining this week[/yellow]")
            platforms = platforms[:remaining]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for platform in platforms:
                if platform == Platform.ALL:
                    continue
                
                task = progress.add_task(f"Posting to {platform.value}...", total=None)
                page = await self._context.new_page()
                
                try:
                    if platform == Platform.TWITTER:
                        success, error = await self._post_to_twitter(post, page)
                    elif platform == Platform.LINKEDIN:
                        success, error = await self._post_to_linkedin(post, page)
                    elif platform == Platform.INSTAGRAM:
                        success, error = await self._post_to_instagram(post, page)
                    else:
                        success, error = False, f"Platform {platform} not implemented yet"
                    
                    results[platform] = (success, error)
                    
                    if success:
                        progress.update(task, description=f"[green]✓ Posted to {platform.value}[/green]")
                    else:
                        progress.update(task, description=f"[red]✗ Failed on {platform.value}: {error}[/red]")
                    
                    await page.close()
                    
                except Exception as e:
                    results[platform] = (False, str(e))
                    progress.update(task, description=f"[red]✗ Error on {platform.value}: {str(e)}[/red]")
                    await page.close()
        
        # Record successful posts
        successful_count = sum(1 for success, _ in results.values() if success)
        if successful_count > 0:
            self.usage.record_post(successful_count)
        
        return results
    
    async def schedule_post(self, post: Post) -> bool:
        """Schedule a post for future posting."""
        schedule_file = self.data_dir / "scheduled.json"
        
        scheduled_posts = []
        if schedule_file.exists():
            try:
                with open(schedule_file, "r") as f:
                    scheduled_posts = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Generate ID
        post.id = f"post_{datetime.utcnow().timestamp()}"
        
        scheduled_posts.append(post.to_csv_row())
        
        with open(schedule_file, "w") as f:
            json.dump(scheduled_posts, f, indent=2)
        
        return True
    
    async def run_scheduled(self) -> list[dict[str, Any]]:
        """Run all scheduled posts that are due."""
        schedule_file = self.data_dir / "scheduled.json"
        
        if not schedule_file.exists():
            return []
        
        try:
            with open(schedule_file, "r") as f:
                scheduled_posts = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
        
        now = datetime.utcnow()
        due_posts = []
        remaining_posts = []
        
        for post_data in scheduled_posts:
            try:
                scheduled_time = datetime.fromisoformat(post_data.get("scheduled_time", ""))
                if scheduled_time and scheduled_time <= now:
                    due_posts.append(post_data)
                else:
                    remaining_posts.append(post_data)
            except (ValueError, TypeError):
                remaining_posts.append(post_data)
        
        # Save remaining posts back
        with open(schedule_file, "w") as f:
            json.dump(remaining_posts, f, indent=2)
        
        # Post due posts
        results = []
        for post_data in due_posts:
            post = Post.from_csv_row(post_data)
            result = await self.post(post)
            results.append({
                "post": post_data,
                "result": result,
            })
        
        return results
    
    async def close(self) -> None:
        """Close the scheduler and clean up."""
        await self._close_browser()
