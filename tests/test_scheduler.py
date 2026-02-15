"""Tests for SocialScheduler."""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta

from social_scheduler.scheduler import SocialScheduler, UsageTracker, PlatformConfig
from social_scheduler.post import Post, Platform


class TestUsageTracker:
    """Test UsageTracker functionality."""
    
    def test_free_tier_limits(self, tmp_path):
        """Test free tier limits are enforced."""
        tracker = UsageTracker(data_dir=tmp_path)
        
        # Should allow 5 posts
        for i in range(5):
            can_post, remaining = tracker.can_post()
            assert can_post is True
            assert remaining == 5 - i
            tracker.record_post()
        
        # 6th post should fail
        can_post, remaining = tracker.can_post()
        assert can_post is False
        assert remaining == 0
    
    def test_premium_unlimited(self, tmp_path):
        """Test premium has unlimited posts."""
        tracker = UsageTracker(data_dir=tmp_path)
        tracker.upgrade_to_premium("test_key")
        
        can_post, _ = tracker.can_post()
        assert can_post is True
    
    def test_usage_info(self, tmp_path):
        """Test getting usage info."""
        tracker = UsageTracker(data_dir=tmp_path)
        
        info = tracker.get_usage_info()
        
        assert "can_post" in info
        assert "posts_this_week" in info
        assert "remaining_this_week" in info
        assert "is_premium" in info


class TestPlatformConfig:
    """Test PlatformConfig functionality."""
    
    def test_is_configured_with_both(self):
        """Test config is configured with email and password."""
        config = PlatformConfig(email="test@test.com", password="secret")
        assert config.is_configured() is True
    
    def test_is_configured_missing_email(self):
        """Test config not configured without email."""
        config = PlatformConfig(password="secret")
        assert config.is_configured() is False
    
    def test_is_configured_missing_password(self):
        """Test config not configured without password."""
        config = PlatformConfig(email="test@test.com")
        assert config.is_configured() is False


class TestSocialSchedulerInit:
    """Test SocialScheduler initialization."""
    
    def test_scheduler_creates_directories(self, tmp_path):
        """Test scheduler creates config and data directories."""
        config_dir = tmp_path / "config"
        data_dir = tmp_path / "data"
        
        scheduler = SocialScheduler(config_dir=config_dir, data_dir=data_dir)
        
        assert config_dir.exists()
        assert data_dir.exists()
    
    def test_scheduler_loads_config(self, tmp_path):
        """Test scheduler loads existing config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create a config file
        config_data = {
            "platforms": {
                "twitter": {
                    "email": "test@example.com",
                    "password": "secret",
                    "enabled": True
                }
            }
        }
        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        scheduler = SocialScheduler(config_dir=config_dir)
        
        assert Platform.TWITTER in scheduler.platform_configs
        assert scheduler.platform_configs[Platform.TWITTER].email == "test@example.com"


class TestSchedulerSaveConfig:
    """Test saving scheduler configuration."""
    
    def test_save_config_creates_file(self, tmp_path):
        """Test saving config creates file."""
        scheduler = SocialScheduler(config_dir=tmp_path)
        scheduler.platform_configs[Platform.TWITTER] = PlatformConfig(
            email="test@test.com",
            password="secret"
        )
        scheduler.save_config()
        
        config_file = tmp_path / "config.json"
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert "platforms" in data
        assert "twitter" in data["platforms"]


class TestUsageTrackerPersistence:
    """Test UsageTracker persistence."""
    
    def test_usage_saved_to_file(self, tmp_path):
        """Test usage data is saved to file."""
        tracker = UsageTracker(data_dir=tmp_path)
        tracker.record_post()
        
        usage_file = tmp_path / "usage.json"
        assert usage_file.exists()
        
        with open(usage_file, 'r') as f:
            data = json.load(f)
        
        assert data["posts_this_week"] == 1
    
    def test_usage_loaded_from_file(self, tmp_path):
        """Test usage data is loaded from file."""
        # Create existing usage file
        usage_file = tmp_path / "usage.json"
        usage_file.write_text(json.dumps({"posts_this_week": 3}))
        
        tracker = UsageTracker(data_dir=tmp_path)
        info = tracker.get_usage_info()
        
        assert info["posts_this_week"] == 3
