"""Tests for Post model."""
import pytest
from datetime import datetime
from pathlib import Path

from social_scheduler.post import Post, Platform


class TestPlatform:
    """Test platform enum."""
    
    def test_from_string_valid(self):
        """Test valid platform parsing."""
        assert Platform.from_string("twitter") == Platform.TWITTER
        assert Platform.from_string("Twitter") == Platform.TWITTER
        assert Platform.from_string("x") == Platform.TWITTER
        
        assert Platform.from_string("linkedin") == Platform.LINKEDIN
        assert Platform.from_string("li") == Platform.LINKEDIN
        
        assert Platform.from_string("instagram") == Platform.INSTAGRAM
        assert Platform.from_string("ig") == Platform.INSTAGRAM
        
        assert Platform.from_string("all") == Platform.ALL
        assert Platform.from_string("*") == Platform.ALL
    
    def test_from_string_invalid(self):
        """Test invalid platform raises error."""
        with pytest.raises(ValueError, match="Unknown platform"):
            Platform.from_string("facebook")


class TestPost:
    """Test Post model."""
    
    def test_create_basic_post(self):
        """Test creating a basic post."""
        post = Post(content="Hello World", platforms=[Platform.TWITTER])
        
        assert post.content == "Hello World"
        assert post.platforms == [Platform.TWITTER]
        assert post.scheduled_time is None
        assert post.status == "pending"
    
    def test_post_with_hashtags(self):
        """Test post with hashtags."""
        post = Post(
            content="Hello",
            platforms=[Platform.TWITTER],
            hashtags=["opensource", "python"]
        )
        
        full_content = post.get_full_content()
        assert "#opensource" in full_content
        assert "#python" in full_content
    
    def test_post_content_truncation(self):
        """Test content truncation with max length."""
        post = Post(
            content="A" * 300,
            platforms=[Platform.TWITTER]
        )
        
        truncated = post.get_full_content(max_length=100)
        assert len(truncated) <= 100
        assert truncated.endswith("...")
    
    def test_to_csv_row(self):
        """Test conversion to CSV row."""
        post = Post(
            content="Test content",
            platforms=[Platform.TWITTER, Platform.LINKEDIN],
            hashtags=["test"],
            link="https://example.com"
        )
        
        row = post.to_csv_row()
        
        assert row["content"] == "Test content"
        assert "twitter" in row["platforms"]
        assert "linkedin" in row["platforms"]
        assert row["hashtags"] == "test"
        assert row["link"] == "https://example.com"
    
    def test_from_csv_row(self):
        """Test creating post from CSV row."""
        row = {
            "content": "CSV test",
            "platforms": "twitter,linkedin",
            "hashtags": "csv,test",
            "link": "https://test.com"
        }
        
        post = Post.from_csv_row(row)
        
        assert post.content == "CSV test"
        assert Platform.TWITTER in post.platforms
        assert Platform.LINKEDIN in post.platforms
        assert "csv" in post.hashtags
        assert "test" in post.hashtags
    
    def test_parse_platforms_string(self):
        """Test parsing platforms from string."""
        platforms = Post.parse_platforms("twitter, instagram")
        
        assert Platform.TWITTER in platforms
        assert Platform.INSTAGRAM in platforms
        assert len(platforms) == 2
    
    def test_parse_media_paths(self):
        """Test parsing media paths from string."""
        paths = Post.parse_media_paths("/tmp/test.png, /tmp/test2.jpg")
        
        assert len(paths) == 2
        assert all(isinstance(p, Path) for p in paths)
