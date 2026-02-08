import pytest
import os
import logging
from datetime import datetime
from modules.logger import setup_logger

def test_setup_logger_creates_log_file(tmp_path):
    """Test that logger creates log file with correct name"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = setup_logger(str(log_dir))
    logger.info("Test message")

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"briefing_{today}.log"
    assert log_file.exists()

    with open(log_file, 'r') as f:
        content = f.read()
        assert "Test message" in content

def test_setup_logger_level():
    """Test logger is set to INFO level"""
    logger = setup_logger()
    assert logger.level == logging.INFO
