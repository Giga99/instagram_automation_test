# 🚀 Instagram Automation

Professional Instagram comment automation using AdsPower browser profiles for enterprise-grade anti-detection and session management with automatic credential fallback.

## 🏢 **AdsPower Professional Features**

✅ **Professional Anti-Detection** - Unique browser fingerprints per profile  
✅ **Persistent Sessions** - Instagram stays logged in between runs  
✅ **Automatic Credential Fallback** - Seamless login when auto-login fails  
✅ **Enterprise Proxy Management** - Integrated proxy per profile  
✅ **Advanced Session Storage** - Full browser profile persistence  
✅ **Professional Profile Management** - GUI + API control  
✅ **Group Organization** - Organize profiles by campaigns  
✅ **Intelligent Error Handling** - Handles 2FA, suspicious login, and dialog boxes

## 📋 **Prerequisites**

### **1. AdsPower Setup**

```bash
# 1. Download and install AdsPower from https://www.adspower.com/
# 2. Get paid subscription (required for API access)
# 3. Launch AdsPower desktop application
# 4. Create Instagram profiles with saved credentials (recommended)
```

### **2. System Requirements**

```bash
pip install -r requirements.txt
playwright install chromium
```

### **3. Environment Configuration**

Create `.env` file:

```env
# Target Configuration
INSTAGRAM_POST_URL=https://www.instagram.com/p/your_target_post/
COMMENT_PROMPT=gym workout motivation

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Automation Settings
HEADLESS_MODE=true              # Run browsers in headless mode
POST_COMMENT=true               # Post to real Instagram (false = simulation)

# Telegram Notifications (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# AdsPower API Configuration
ADSPOWER_BASE_URL=http://localhost:50325
ADSPOWER_API_KEY=your_api_key
```

## 🚀 **Quick Start Guide**

### **Step 1: Set Up AdsPower Profiles**

1. **Create profiles in AdsPower desktop app**
2. **Configure Instagram credentials** (username/password) in each profile
3. **Set up proxies** (recommended for each profile)
4. **Organize profiles into groups** for campaign management

### **Step 2: Verify Profile Setup**

```bash
# Test connection and list existing profiles
python -c "from src.integrations.adspower.config import load_adspower_profiles; profiles = load_adspower_profiles(); print(f'Found {len(profiles)} profiles')"
```

### **Step 3: Run Automation**

```bash
# Run the automation with your AdsPower profiles
python main.py
```

## 📁 **Project Structure**

```
instagram-automation/
├── main.py                          # Main automation orchestrator
├── requirements.txt                 # All dependencies
├── .env                            # Configuration file
├── src/                            # Source code modules
│   ├── utils/                      # Utility modules
│   │   ├── logger.py              # Structured logging system
│   │   └── date_utils.py          # Date/time utilities
│   └── integrations/              # External service integrations
│       ├── openai/                # OpenAI integration
│       │   └── comment_gen.py     # Comment generation
│       ├── telegram/              # Telegram integration
│       │   └── notifier.py        # Telegram notifications
│       ├── instagram/             # Instagram automation
│       │   └── poster.py          # Comment posting
│       └── adspower/              # AdsPower integration
│           ├── client.py          # Direct AdsPower API client
│           ├── config.py          # AdsPower profile loader
│           └── profile_manager.py # High-level profile manager
├── tests/                          # Comprehensive test suite
│   ├── utils/                     # Utility module tests
│   │   └── test_logger.py         # Logger functionality (19 tests)
│   ├── integrations/              # Integration tests
│   │   ├── openai_integration/    # OpenAI tests
│   │   │   └── test_comment_gen.py # Comment generation (22 tests)
│   │   ├── telegram/              # Telegram tests
│   │   │   └── test_notifier.py   # Notification system (24 tests)
│   │   ├── instagram/             # Instagram tests
│   │   │   └── test_poster.py     # Comment posting (25 tests)
│   │   └── adspower/              # AdsPower tests
│   │       ├── test_adspower_client.py        # API client (26 tests)
│   │       ├── test_adspower_config.py        # Configuration (8 tests)
│   │       ├── test_adspower_profile_manager.py # Profile management (12 tests)
│   │       ├── test_adspower_integration.py   # End-to-end workflow (8 tests)
│   │       └── run_adspower_tests.py          # AdsPower test runner
│   ├── integration/               # End-to-end integration tests
│   │   └── test_integration.py    # Cross-module integration (3 tests)
│   ├── run_all_tests.py          # Main test runner
│   ├── discover_tests.py         # Test discovery utility
│   └── README.md                 # Test documentation
└── output/                        # Logs and results
```

## 🔄 **Automation Workflow**

### **1. Profile Loading & Validation**

```python
# Load profiles from AdsPower with Instagram credentials
# Profiles include:
# - Profile ID and name
# - Instagram username/password
# - Group organization
# - Creation and last-used timestamps
```

### **2. Intelligent Login Process**

```python
# For each profile:
# 1. Start AdsPower browser profile
# 2. Connect Playwright to browser
# 3. Check if already logged into Instagram
# 4. If not logged in:
#    - Attempt AdsPower auto-login (5 seconds)
#    - If auto-login fails → Automatic credential fallback
#    - Fill login form with saved credentials
#    - Handle post-login dialogs (Save Login, Notifications)
#    - Detect and handle errors (2FA, incorrect password, etc.)
```

### **3. Comment Generation & Posting**

```python
# For each successfully logged-in profile:
# 1. Generate dynamic comment via OpenAI
# 2. Navigate to target Instagram post
# 3. Post comment with natural timing
# 4. Log all activities
# 5. Clean up browser session
```

## ⚙️ **Configuration Options**

### **AdsPower Profile Manager Settings**

```python
# In main.py, you can configure:
adspower_manager = AdsPowerProfileManager(
    allow_credential_fallback=True,     # Enable automatic login fallback
    credential_fallback_timeout=90      # Login completion timeout (seconds)
)
```

### **Environment Variables**

```env
# Required
INSTAGRAM_POST_URL=https://www.instagram.com/p/your_post/
OPENAI_API_KEY=your_openai_key

# Optional
COMMENT_PROMPT=gym workout motivation  # Default prompt for comments
HEADLESS_MODE=true                     # Run browsers headlessly
POST_COMMENT=true                      # true = real posting, false = simulation
ADSPOWER_BASE_URL=http://localhost:50325
ADSPOWER_API_KEY=your_key             # For headless mode
TELEGRAM_BOT_TOKEN=your_token         # For notifications
TELEGRAM_CHAT_ID=your_chat_id         # For notifications
```

### **Profile Requirements**

Each AdsPower profile should have:

- **Instagram Username** - Stored in profile configuration
- **Instagram Password** - Stored in profile configuration
- **Unique Proxy** (recommended) - Configured in AdsPower
- **Browser Fingerprint** - Automatically managed by AdsPower
- **Group Assignment** (optional) - For campaign organization

## 🧪 **Comprehensive Test Suite**

The project includes a professional-grade test suite with **147 tests** across all modules:

### **Test Organization**

- **📝 Utils Tests (19)**: Logger functionality, file operations, configuration
- **🤖 OpenAI Integration Tests (22)**: Comment generation, API interaction, validation
- **📱 Telegram Integration Tests (24)**: Bot API, message sending, notifications
- **💬 Instagram Integration Tests (25)**: Comment posting, browser automation, rate limiting
- **🔌 AdsPower Integration Tests (54)**: Profile management, browser automation, workflows
- **🔗 End-to-End Integration Tests (3)**: Cross-module functionality, complete workflows

### **Running Tests**

```bash
# Run all core tests (93 tests, ~15 seconds)
python tests/run_all_tests.py

# Run AdsPower integration tests (54 tests, ~1 second)
python tests/integrations/adspower/run_adspower_tests.py

# Discover all available tests
python tests/discover_tests.py

# Run tests by category
python -m pytest tests/utils/                          # Utils tests
python -m pytest tests/integrations/openai_integration/ # OpenAI tests
python -m pytest tests/integrations/telegram/          # Telegram tests
python -m pytest tests/integrations/instagram/         # Instagram tests
python -m pytest tests/integrations/adspower/          # AdsPower tests
python -m pytest tests/integration/                    # Integration tests
```

### **Test Features**

- ✅ **100% Pass Rate** across all test categories
- ✅ **Comprehensive Mocking** for external dependencies
- ✅ **Error Simulation** for various failure scenarios
- ✅ **Performance Testing** with timing validation
- ✅ **Unicode Support** for international characters
- ✅ **Retry Logic Testing** for network failures

## 📊 **Monitoring & Logging**

### **Real-time Console Output**

```bash
🚀 Instagram Automation Starting
📅 Timestamp: 2024-01-15 14:30:00
🎭 Simulation Mode: OFF
👤 Headless Mode: ON
🏢 Profile Manager: AdsPower Professional

🏢 Loading profiles from AdsPower...
✅ Loaded 3 AdsPower profiles ready for automation

👥 Found 3 AdsPower profile(s):
   • profile_123 - AdsPower (Campaign_A)
   • profile_456 - AdsPower (Campaign_A)
   • profile_789 - AdsPower (Campaign_B)

🎯 Target post: https://www.instagram.com/p/example_post/

🔄 Processing AdsPower profile 1/3
🚀 Processing AdsPower Profile: profile_123 (username1)
🤖 [profile_123] Generating comment...
✅ [profile_123] Generated comment: This workout is incredible! 💪
🔐 [profile_123] Connecting to AdsPower profile...
🔄 [profile_123] Starting AdsPower profile (attempt 1/3)
✅ [profile_123] Already logged into Instagram
💬 [profile_123] Posting comment...
✅ [profile_123] Comment posted successfully!
```

### **Structured JSON Logs**

```json
{
  "profile_id": "profile_123",
  "comment": "This workout is incredible! 💪",
  "timestamp": "2024-01-15T14:30:15Z",
  "success": true,
  "error": null
}
```

### **Telegram Notifications**

- **Progress Updates**: Real-time status per profile
- **Error Alerts**: Immediate notification of failures
- **Completion Summary**: Final statistics and success rate

## 🛠️ **Troubleshooting**

### **Common Issues & Solutions**

#### **AdsPower Connection Failed**

```bash
❌ [profile_123] AdsPower is not running or not accessible
```

**Solution**: Launch AdsPower desktop application and ensure it's running on port 50325

#### **Auto-Login Failed → Automatic Fallback**

```bash
⚠️ [profile_123] Auto-login failed - profile may need automatic credential fallback
🔐 [profile_123] Attempting automatic credential fallback with credentials...
📝 [profile_123] Filling login credentials...
✅ [profile_123] Login successful!
```

**This is normal behavior** - the system automatically handles login failures

#### **No Credentials Available**

```bash
❌ [profile_123] No credentials available for fallback login
```

**Solution**: Ensure username/password are configured in AdsPower profile settings

#### **Two-Factor Authentication Detected**

```bash
🔐 [profile_123] Two-factor authentication required - login failed
```

**Solution**: Disable 2FA for automation accounts or use pre-authenticated AdsPower sessions

#### **Profile Creation Timestamps**

```bash
KeyError: 'created_time' or 'last_open_time'
```

**Solution**: Update AdsPower to latest version - older versions may not include timestamp data

### **Advanced Debugging**

```bash
# Enable debug logging in src/integrations/adspower/adspower/client.py
logger.setLevel(logging.DEBUG)

# Check specific profile status
python -c "
from src.integrations.adspower.adspower.client import AdsPowerClient
client = AdsPowerClient()
status = client.check_profile_status('your_profile_id')
print(f'Profile status: {status}')
"
```

## 🔐 **Security & Anti-Detection**

### **Professional Features**

- **Unique Browser Fingerprints** - Each profile appears as different device
- **Canvas Fingerprint Protection** - Randomized canvas signatures
- **WebRTC IP Protection** - Prevents real IP detection
- **Font Fingerprinting** - Unique font detection per profile
- **Timezone Spoofing** - Location-based timezone matching
- **Persistent Sessions** - Reduces login frequency suspicion

### **Best Practices**

- **Use unique proxies** for each profile
- **Maintain realistic timing** between actions (30+ seconds between profiles)
- **Keep profiles organized** by campaign/client
- **Monitor Instagram compliance** with their terms of service
- **Use session persistence** to reduce login challenges
- **Configure realistic delays** in automation settings

## 📈 **Scaling & Enterprise**

### **Profile Organization**

```python
# Automatic group-based processing
# - Profiles organized by AdsPower groups
# - Intelligent delays between groups
# - Campaign-specific targeting
```

### **Multiple Campaign Management**

```python
# Group profiles by campaign in AdsPower:
# Campaign_A: profiles for fitness content
# Campaign_B: profiles for business content
# Campaign_C: profiles for lifestyle content

# The system automatically processes by groups with delays
```

### **Performance Optimization**

- **Headless Mode**: Faster execution without UI
- **Parallel Processing**: Multiple profiles can run simultaneously
- **Session Reuse**: Persistent Instagram sessions
- **Smart Retry Logic**: Exponential backoff on failures

## 🎯 **Advanced Features**

### **Automatic Error Recovery**

```python
# Handles common Instagram scenarios:
# - "Save Your Login Info" → Clicks "Not Now"
# - "Turn on Notifications" → Clicks "Not Now"
# - "Suspicious Login Attempt" → Reports failure
# - "Incorrect Password" → Reports failure
# - Two-Factor Authentication → Reports failure
```

### **Intelligent Timing**

```python
# Built-in delays:
# - 5 seconds for auto-login attempt
# - 30+ seconds between profiles
# - Extra 10 seconds when switching groups
# - Exponential backoff on retries
```

### **Professional Logging**

```python
# Comprehensive logging:
# - JSON-structured logs
# - Success/failure tracking
# - Error categorization
# - Performance metrics
# - Timestamp tracking
```

## 🚀 **Production Deployment**

### **Server Setup**

```bash
# Install on headless server
export HEADLESS_MODE=true
export POST_COMMENT=true
export ADSPOWER_API_KEY=your_key

# Run automation
nohup python main.py > automation.log 2>&1 &
```

### **Monitoring & Alerts**

```bash
# Set up Telegram notifications for production
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id

# Logs will be in output/ directory
tail -f output/adspower_log_*.json
```

---

## 📞 **Support**

### **Quick Diagnostics**

1. **Check AdsPower Connection**: Launch AdsPower desktop app
2. **Verify Profile Setup**: Run profile loading test
3. **Check Logs**: Review `output/adspower_log_*.json`
4. **Test Environment**: Verify `.env` configuration

### **Common Solutions**

- **Connection Issues**: Restart AdsPower application
- **Login Failures**: Check Instagram credentials in profiles
- **API Errors**: Verify AdsPower API key and subscription
- **Proxy Issues**: Test proxy configuration in AdsPower

**Professional Instagram automation with enterprise-grade anti-detection and automatic credential fallback! 🚀**
