"""Tests for CLI commands."""
import pytest
from click.testing import CliRunner
from social_scheduler.cli import cli


class TestStatusCommand:
    """Test status command."""
    
    def test_status_shows_info(self):
        """Test status shows usage info."""
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "Tier" in result.output
        assert "Free" in result.output or "Premium" in result.output


class TestConfigCommand:
    """Test config command."""
    
    def test_config_missing_platform(self):
        """Test config requires platform."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config'])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output
    
    def test_config_help(self):
        """Test config help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--help'])
        
        assert result.exit_code == 0
        assert "platform" in result.output.lower()


class TestPostCommand:
    """Test post command."""
    
    def test_post_requires_content(self):
        """Test post requires content."""
        runner = CliRunner()
        result = runner.invoke(cli, ['post'])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output
    
    def test_post_requires_platforms(self):
        """Test post requires platforms."""
        runner = CliRunner()
        result = runner.invoke(cli, ['post', '-c', 'Hello'])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output
    
    def test_post_help(self):
        """Test post help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['post', '--help'])
        
        assert result.exit_code == 0
        assert "content" in result.output.lower()


class TestImportCommand:
    """Test import command."""
    
    def test_import_requires_file(self):
        """Test import requires CSV file."""
        runner = CliRunner()
        result = runner.invoke(cli, ['import'])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output
    
    def test_import_nonexistent_file(self):
        """Test import with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '/nonexistent/file.csv'])
        
        assert result.exit_code != 0
        assert "does not exist" in result.output


class TestScheduledCommand:
    """Test scheduled command."""
    
    def test_scheduled_no_posts(self):
        """Test scheduled with no posts."""
        runner = CliRunner()
        result = runner.invoke(cli, ['scheduled'])
        
        assert result.exit_code == 0
        # Should handle empty gracefully


class TestHelp:
    """Test help commands."""
    
    def test_main_help(self):
        """Test main help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "social-scheduler" in result.output
    
    def test_version(self):
        """Test version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output
