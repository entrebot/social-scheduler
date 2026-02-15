"""Post data models."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class Platform(Enum):
    """Supported social media platforms."""
    
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    ALL = "all"
    
    @classmethod
    def from_string(cls, value: str) -> Platform:
        """Parse platform from string."""
        mapping = {
            "twitter": cls.TWITTER,
            "x": cls.TWITTER,
            "t": cls.TWITTER,
            "linkedin": cls.LINKEDIN,
            "li": cls.LINKEDIN,
            "instagram": cls.INSTAGRAM,
            "ig": cls.INSTAGRAM,
            "insta": cls.INSTAGRAM,
            "all": cls.ALL,
            "*": cls.ALL,
        }
        normalized = value.lower().strip()
        if normalized not in mapping:
            raise ValueError(f"Unknown platform: {value}")
        return mapping[normalized]


class Post(BaseModel):
    """A social media post."""
    
    id: str | None = None
    content: str = Field(..., min_length=1, max_length=2000)
    platforms: list[Platform] = Field(default_factory=list)
    scheduled_time: datetime | None = None
    media_paths: list[Path] = Field(default_factory=list)
    alt_text: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    link: str | None = None
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    posted_at: datetime | None = None
    error_message: str | None = None
    
    @validator("media_paths", pre=True)
    def validate_media_paths(cls, v: Any) -> list[Path]:
        """Convert string paths to Path objects."""
        if not v:
            return []
        if isinstance(v, str):
            return [Path(v)] if v else []
        return [Path(p) for p in v if p]
    
    @validator("hashtags", "mentions", pre=True)
    def validate_tags(cls, v: Any) -> list[str]:
        """Convert string to list if needed."""
        if not v:
            return []
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return [str(t).strip() for t in v if t]
    
    @validator("platforms", pre=True)
    def validate_platforms(cls, v: Any) -> list[Platform]:
        """Parse platforms from strings."""
        if not v:
            return []
        if isinstance(v, str):
            if "," in v:
                return [Platform.from_string(p.strip()) for p in v.split(",") if p.strip()]
            return [Platform.from_string(v)]
        return v
    
    def get_full_content(self, max_length: int | None = None) -> str:
        """Get post content with hashtags appended."""
        content = self.content
        
        if self.hashtags:
            tags = " ".join(f"#{tag.lstrip('#')}" for tag in self.hashtags)
            content = f"{content}\n\n{tags}".strip()
        
        if max_length and len(content) > max_length:
            # Truncate intelligently
            content = content[:max_length-3] + "..."
        
        return content
    
    def to_csv_row(self) -> dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "content": self.content,
            "platforms": ",".join(p.value for p in self.platforms),
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else "",
            "media_paths": ",".join(str(p) for p in self.media_paths),
            "alt_text": self.alt_text or "",
            "hashtags": ",".join(self.hashtags),
            "link": self.link or "",
        }
    
    @classmethod
    def from_csv_row(cls, row: dict[str, Any]) -> Post:
        """Create Post from CSV row dictionary."""
        # Parse scheduled_time
        scheduled_time = None
        if row.get("scheduled_time"):
            try:
                scheduled_time = datetime.fromisoformat(row["scheduled_time"])
            except (ValueError, TypeError):
                pass
        
        return cls(
            content=row.get("content", ""),
            platforms=cls.parse_platforms(row.get("platforms", "")),
            scheduled_time=scheduled_time,
            media_paths=cls.parse_media_paths(row.get("media_paths", "")),
            alt_text=row.get("alt_text") or None,
            hashtags=[h.strip() for h in row.get("hashtags", "").split(",") if h.strip()],
            link=row.get("link") or None,
        )
    
    @staticmethod
    def parse_platforms(value: str) -> list[Platform]:
        """Parse comma-separated platforms."""
        if not value:
            return []
        return [Platform.from_string(p.strip()) for p in value.split(",") if p.strip()]
    
    @staticmethod
    def parse_media_paths(value: str) -> list[Path]:
        """Parse comma-separated media paths."""
        if not value:
            return []
        return [Path(p.strip()) for p in value.split(",") if p.strip()]
