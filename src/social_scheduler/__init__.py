"""Social Scheduler - Free social media scheduling CLI."""

__version__ = "1.0.0"
__author__ = "OpenClaw"
__email__ = "noreply@example.com"
__license__ = "MIT"
__description__ = "Free social media scheduler CLI - 5 posts/week free"
__url__ = "https://github.com/entrebear/social-scheduler"

from social_scheduler.scheduler import SocialScheduler
from social_scheduler.post import Post, Platform

__all__ = ["SocialScheduler", "Post", "Platform"]
