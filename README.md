# Instagram Automation Project

This project automates posting three comments to Instagram using three isolated profiles, dynamic content generation via OpenAI, structured logging, comprehensive retry logic, and Telegram notifications.

## 🎯 Project Description

The Instagram Automation system is a production-ready solution that manages multiple browser profiles to:

- Log into three separate Instagram accounts simultaneously using Playwright automation
- Generate unique, playful comments for gym selfies using OpenAI's API
- Post these comments to a specified Instagram post with intelligent DOM interaction
- Implement robust error handling with exponential backoff retry logic
- Log all activities with comprehensive structured logging (JSON/CSV)
- Send detailed Telegram notifications upon completion
- Support both simulation and real Instagram posting modes

## ✨ Key Features

- **🔐 Multi-Profile Management**: Isolated browser contexts with separate user data directories
- **🤖 AI-Powered Content**: Dynamic comment generation using OpenAI GPT models
- **🎭 Simulation Mode**: Safe testing without real Instagram interaction
- **🔄 Robust Retry Logic**: Exponential backoff for login and posting failures
- **📊 Structured Logging**: Comprehensive activity tracking in JSON or CSV format
- **📱 Telegram Integration**: Real-time notifications with detailed status reports
- **🧪 Comprehensive Testing**: 111 tests across 6 modules with 100% success rate
- **⚡ Performance Optimized**: Efficient browser automation with minimal resource usage

## 📋 Prerequisites

- **Python 3.10+**
- **OpenAI API Key** - For dynamic comment generation
- **Three Instagram test accounts** - For multi-profile automation
- **Telegram Bot Token** (optional) - For completion notifications
- **Playwright Browser Dependencies** - Installed via `playwright install`

## 🚀 Installation Instructions

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd InstagramAutomationTestProject
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**

   ```bash
   playwright install
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your actual credentials
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Instagram Account Credentials
INSTAGRAM_USER1=username1
INSTAGRAM_PASS1=password1
INSTAGRAM_USER2=username2
INSTAGRAM_PASS2=password2
INSTAGRAM_USER3=username3
INSTAGRAM_PASS3=password3

# Target Instagram Post
INSTAGRAM_POST_URL=https://www.instagram.com/p/example_post_id/

# Telegram Notifications (Optional)
TG_BOT_TOKEN=your_telegram_bot_token
TG_CHAT_ID=your_chat_id
```

## 🏃‍♂️ Running the Script

Execute the main automation script:

```bash
python main.py
```

### What the script does:

1. **Profile Management**: Creates three isolated Playwright browser contexts with separate user data directories
2. **Authentication**: Logs into each Instagram account with retry logic and 2FA detection (up to 3 attempts per profile)
3. **Content Generation**: Uses OpenAI to generate unique, playful comments for gym selfies
4. **Comment Posting**: Posts generated comments with intelligent DOM interaction and success verification
5. **Error Handling**: Implements exponential backoff retry logic with comprehensive error detection
6. **Logging**: Records all activities (successes and failures) in structured format with atomic file operations
7. **Notification**: Sends detailed Telegram alerts upon completion with success/failure statistics

## 🧪 Testing

The project includes a comprehensive test suite with **111 tests** across **6 modules**:

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific module tests
python -m pytest tests/test_logger.py -v
python -m pytest tests/test_comment_gen.py -v
python -m pytest tests/test_notifier.py -v
python -m pytest tests/test_profile_manager.py -v
python -m pytest tests/test_poster.py -v
python -m pytest tests/test_integration.py -v
```

### Test Coverage:

- **Foundation**: 41 tests - Logger (19), Comment Generation (22)
- **Notifications**: 24 tests - Notifier module
- **Browser Automation**: 43 tests - Profile Manager (18), Poster (25)
- **Integration**: 3 tests - End-to-end workflow validation

**All tests achieve 100% success rate with comprehensive mocking of external APIs (OpenAI, Telegram, Playwright).**

## 📁 File Structure Overview

```
InstagramAutomationTestProject/
├── README.md                    # This documentation file
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies (Playwright >=1.40.0)
├── main.py                      # Main orchestrator script (150+ lines)
├── modules/                     # Core functionality modules (2,500+ lines)
│   ├── __init__.py             # Package initialization
│   ├── profile_manager.py      # Browser automation & Instagram login (213+ lines)
│   ├── comment_gen.py          # OpenAI comment generation (100+ lines)
│   ├── poster.py               # Instagram comment posting (200+ lines)
│   ├── logger.py               # Structured logging with atomic operations (100+ lines)
│   └── notifier.py             # Telegram notifications (150+ lines)
├── profiles/                    # Playwright user data directories
│   ├── profile1/               # Browser data for account 1
│   ├── profile2/               # Browser data for account 2
│   └── profile3/               # Browser data for account 3
├── tests/                       # Comprehensive test suite (111 tests)
│   ├── run_all_tests.py        # Test runner with detailed reporting
│   ├── test_logger.py          # Logger module tests (19 tests)
│   ├── test_comment_gen.py     # Comment generation tests (22 tests)
│   ├── test_notifier.py        # Telegram notification tests (24 tests)
│   ├── test_profile_manager.py # Browser automation tests (18 tests)
│   ├── test_poster.py          # Comment posting tests (25 tests)
│   └── test_integration.py     # Integration tests (3 tests)
└── output/
    └── comments_log.json       # Activity log file
```

### Module Responsibilities:

- **`profile_manager.py`**: Manages Playwright browser contexts, handles Instagram login with 2FA detection, implements retry logic with exponential backoff
- **`comment_gen.py`**: Integrates with OpenAI API to generate dynamic, contextual comments with error handling
- **`poster.py`**: Handles Instagram comment posting with intelligent DOM interaction, simulation mode, and success verification
- **`logger.py`**: Provides structured logging in JSON or CSV format with atomic file operations and comprehensive error tracking
- **`notifier.py`**: Sends Telegram notifications using Bot API with detailed status reports and error handling

## 🎭 Simulation Mode

For testing without real Instagram interaction, the project includes a comprehensive simulation mode:

- **Current Setting**: `USE_REAL_INSTAGRAM = False` in `modules/poster.py`
- **Simulation Behavior**: Comments are logged to console with realistic delays and success simulation
- **Real Mode**: Set `USE_REAL_INSTAGRAM = True` when ready to use real accounts
- **Safety Features**: Prevents accidental posting during development and testing

**Note**: Simulation mode is enabled by default to prevent accidental posting during development.

## 🔧 Customization Options

### Switch to CSV Logging:

Edit `modules/logger.py`:

```python
LOG_FORMAT = "csv"  # Change from "json"
```

### Target Different Instagram Post:

Update the `INSTAGRAM_POST_URL` in your `.env` file:

```env
INSTAGRAM_POST_URL=https://www.instagram.com/p/your_target_post/
```

### Disable Telegram Notifications:

Leave `TG_BOT_TOKEN` and `TG_CHAT_ID` blank in `.env` - the script will automatically skip notifications.

### Configure Retry Logic:

Modify retry parameters in respective modules:

- Login retries: `profile_manager.py`
- Posting retries: `poster.py`
- API retries: `comment_gen.py` and `notifier.py`

## 🛡️ Error Handling & Retry Logic

### Advanced Login Retry Logic:

- **Attempts**: Up to 3 login attempts per profile with exponential backoff
- **2FA Detection**: Automatic detection and handling of two-factor authentication prompts
- **Dialog Handling**: Intelligent handling of "Save Login Info" and other Instagram dialogs
- **Session Management**: Persistent browser sessions across retries
- **Fallback**: Failed logins are logged and skipped (other profiles continue)

### Robust Posting Retry Logic:

- **Attempts**: Up to 3 posting attempts per comment with intelligent retry delays
- **DOM Interaction**: Multiple methods for comment input detection and interaction
- **Success Verification**: Multi-layered verification of successful comment posting
- **Rate Limiting**: Detection and handling of Instagram rate limits and restrictions
- **Error Classification**: Detailed categorization of posting failures for better debugging

### Comprehensive Error Logging:

All errors are captured in the log file with:

- Profile ID and context information
- Timestamp (ISO 8601 UTC)
- Detailed error messages with stack traces
- Retry attempt numbers and outcomes
- Performance metrics and timing data

## 📊 Output Logging

### JSON Format (Default):

```json
[
  {
    "profile_id": "profile1",
    "timestamp": "2025-06-07T12:34:56Z",
    "comment": "Looking strong! 💪 Keep crushing those goals! 🔥",
    "status": "success",
    "retry_count": 0,
    "execution_time": 2.34,
    "error": null
  }
]
```

### CSV Format:

```csv
profile_id,timestamp,comment,status,retry_count,execution_time,error
profile1,2025-06-07T12:34:56Z,"Looking strong! 💪 Keep crushing those goals! 🔥",success,0,2.34,
```

## 🚨 Security Notes

- **Never commit real credentials** - Use `.env.example` as template only
- **User data isolation** - Each profile maintains separate browser data directories
- **API key protection** - Environment variables prevent credential exposure
- **Error sanitization** - Sensitive data is excluded from error logs and notifications
- **Secure browser contexts** - Playwright contexts are properly isolated and cleaned up
- **Rate limiting compliance** - Built-in delays and restrictions to respect Instagram's limits

## 🔍 Troubleshooting

### Common Issues:

1. **Playwright Installation**: Run `playwright install` if browser download fails
2. **Environment Variables**: Verify all required variables are set in `.env`
3. **Instagram Blocks**: Use test accounts and avoid rapid-fire requests
4. **OpenAI Limits**: Check API quota and rate limits
5. **Telegram Setup**: Verify bot token and chat ID are correct
6. **2FA Issues**: Ensure accounts have appropriate 2FA settings for automation
7. **DOM Changes**: Instagram UI changes may require updating selectors in `poster.py`

### Debug Mode:

Enable verbose logging by modifying the logging configuration in `modules/logger.py`:

```python
LOG_LEVEL = "DEBUG"  # Change from "INFO"
```

### Test Debugging:

Run specific tests with verbose output:

```bash
python -m pytest tests/test_profile_manager.py::test_login_success -v -s
```

## 🚀 Production Deployment

The project is production-ready with the following considerations:

1. **Environment Setup**: Ensure all dependencies are installed in production environment
2. **Credential Management**: Use secure credential storage (not `.env` files in production)
3. **Monitoring**: Implement log monitoring and alerting for the JSON/CSV output files
4. **Scaling**: Consider rate limits when scaling to more profiles or posts
5. **Maintenance**: Regular updates to handle Instagram UI changes

## 📈 Future Enhancements

- Support for additional social media platforms (Twitter, Facebook, TikTok)
- Advanced comment templates with machine learning personalization
- Scheduling and automation features with cron job integration
- Enhanced error recovery mechanisms with intelligent retry strategies
- Performance monitoring and analytics dashboard
- Multi-language support for international accounts
- Advanced browser fingerprinting protection
- Headless mode optimization for server environments

---

**⚠️ Disclaimer**: This tool is for educational and testing purposes. Ensure compliance with Instagram's Terms of Service and use responsibly with test accounts only. The developers are not responsible for any misuse or violations of platform policies.
