"""
Instagram Automation Project - Test Suite

This directory contains a comprehensive, well-organized test suite for the Instagram
automation project. Tests are organized by category for better maintainability.

DIRECTORY STRUCTURE:
===================

📁 tests/
├── 📁 utils/                    # Utility module tests
│   └── test_logger.py          # Logger functionality tests
├── 📁 integrations/             # External service integration tests
│   ├── 📁 openai_integration/  # OpenAI integration tests
│   │   └── test_comment_gen.py # Comment generation tests
│   ├── 📁 telegram/            # Telegram integration tests
│   │   └── test_notifier.py    # Notification system tests
│   ├── 📁 instagram/           # Instagram automation tests
│   │   └── test_poster.py      # Comment posting tests
│   └── 📁 adspower/            # AdsPower integration tests
│       ├── test_adspower_client.py        # API client tests
│       ├── test_adspower_config.py        # Configuration tests
│       ├── test_adspower_profile_manager.py # Profile management tests
│       ├── test_adspower_integration.py   # End-to-end workflow tests
│       └── run_adspower_tests.py          # AdsPower test runner
├── 📁 integration/             # End-to-end integration tests
│   └── test_integration.py    # Cross-module integration tests
├── run_all_tests.py           # Main test runner
└── discover_tests.py          # Test discovery utility

RUNNING TESTS:
=============

🚀 All Tests:
   python tests/run_all_tests.py

🔌 AdsPower Tests:
   python tests/integrations/adspower/run_adspower_tests.py

🔍 Test Discovery:
   python tests/discover_tests.py

📁 Category Tests:
   python -m pytest tests/utils/
   python -m pytest tests/integrations/openai_integration/
   python -m pytest tests/integrations/telegram/
   python -m pytest tests/integrations/instagram/
   python -m pytest tests/integrations/adspower/
   python -m pytest tests/integration/

🧪 Individual Tests:
   python -m pytest tests/utils/test_logger.py
   python -m pytest tests/integrations/openai_integration/test_comment_gen.py
   python -m pytest tests/integrations/telegram/test_notifier.py
   python -m pytest tests/integrations/instagram/test_poster.py
   python -m pytest tests/integration/test_integration.py

TEST CATEGORIES:
===============

📝 Utils Tests (19 tests)
   - Logger functionality and file operations
   - Configuration management
   - Date and time utilities

🤖 OpenAI Integration Tests (22 tests)
   - Comment generation and validation
   - API interaction and error handling
   - Retry logic and rate limiting

📱 Telegram Integration Tests (24 tests)
   - Bot API communication
   - Message formatting and sending
   - Notification workflows

💬 Instagram Integration Tests (25 tests)
   - Comment posting automation
   - Browser interaction and element detection
   - Rate limiting and error recovery

🔌 AdsPower Integration Tests (54 tests)
   - Profile management and browser automation
   - API client functionality
   - End-to-end workflow testing

🔗 Integration Tests (3 tests)
   - Cross-module functionality
   - Complete workflow simulation
   - Error handling across components

TOTAL: 147 tests across 9 modules
"""

__version__ = "1.0.0" 