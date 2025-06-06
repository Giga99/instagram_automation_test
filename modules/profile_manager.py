"""
Profile Manager Module

Handles browser context management and Instagram login functionality.
"""

import os
import time
from typing import Optional, Dict, Any

from playwright.sync_api import BrowserContext, Playwright, Page, TimeoutError as PlaywrightTimeoutError


def create_browser_context(playwright: Playwright, profile_id: str, headless: bool = True) -> BrowserContext:
    """
    Creates a new browser context with profile-specific configuration.
    
    Args:
        playwright: Playwright instance
        profile_id: Profile identifier for data persistence
        headless: Whether to run browser in headless mode
        
    Returns:
        Configured BrowserContext
    """
    # Create user data directory for profile isolation
    user_data_dir = os.path.join("browser_profiles", profile_id)
    os.makedirs(user_data_dir, exist_ok=True)

    # Launch browser with persistent context
    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",  # Speed up browsing
            "--disable-javascript",  # Basic security
        ]
    )

    # Create context with realistic settings
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="en-US",
        timezone_id="America/New_York",
    )

    return context


def login_profile(playwright: Playwright, profile_id: str, username: str, password: str,
                  target_post_url: str = None, headless: bool = True, max_retries: int = 3) -> Optional[BrowserContext]:
    """
    Attempts to log into Instagram using the specified profile credentials.
    
    Args:
        playwright: Playwright instance
        profile_id: Profile identifier (e.g., 'profile1')
        username: Instagram username
        password: Instagram password
        target_post_url: Optional Instagram post URL to navigate to after login
        headless: Whether to run browser in headless mode
        max_retries: Maximum number of retry attempts
    
    Returns:
        BrowserContext if successful, None if login failed after retries
    """
    if not username or not password:
        print(f"❌ [{profile_id}] Missing username or password")
        return None

    print(f"🚀 [{profile_id}] Starting login process...")

    for attempt in range(max_retries):
        context = None
        try:
            print(f"🔄 [{profile_id}] Login attempt {attempt + 1}/{max_retries}")

            # Create browser context
            context = create_browser_context(playwright, profile_id, headless)
            page = context.new_page()

            # Navigate to Instagram login
            print(f"🌐 [{profile_id}] Navigating to Instagram...")
            page.goto("https://www.instagram.com/accounts/login/", timeout=30000)

            # Wait for login form
            page.wait_for_selector('input[name="username"]', timeout=10000)

            # Check if already logged in
            if is_already_logged_in(page):
                print(f"✅ [{profile_id}] Already logged in!")
                if target_post_url:
                    navigate_to_post(page, target_post_url)
                return context

            # Fill login form
            print(f"📝 [{profile_id}] Filling login credentials...")
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)

            # Click login button
            page.click('button[type="submit"]')

            # Wait for login to complete
            print(f"⏳ [{profile_id}] Waiting for login completion...")

            # Check for various post-login scenarios
            if wait_for_login_completion(page, profile_id):
                print(f"✅ [{profile_id}] Login successful!")

                # Navigate to target post if provided
                if target_post_url:
                    navigate_to_post(page, target_post_url)

                return context
            else:
                print(f"❌ [{profile_id}] Login failed")
                if context:
                    context.close()
                context = None

        except PlaywrightTimeoutError as e:
            print(f"⏰ [{profile_id}] Timeout during login attempt {attempt + 1}: {str(e)}")
            if context:
                context.close()
            context = None

        except Exception as e:
            print(f"❌ [{profile_id}] Error during login attempt {attempt + 1}: {str(e)}")
            if context:
                context.close()
            context = None

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"⏳ [{profile_id}] Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

    print(f"🚫 [{profile_id}] All login attempts failed")
    return None


def is_already_logged_in(page: Page) -> bool:
    """
    Checks if user is already logged into Instagram.
    
    Args:
        page: Playwright page instance
        
    Returns:
        True if already logged in, False otherwise
    """
    try:
        # Check for common logged-in indicators
        page.wait_for_selector('svg[aria-label="Home"]', timeout=3000)
        return True
    except PlaywrightTimeoutError:
        try:
            # Alternative check - profile menu
            page.wait_for_selector('[role="menuitem"]', timeout=1000)
            return True
        except PlaywrightTimeoutError:
            return False


def wait_for_login_completion(page: Page, profile_id: str, timeout: int = 15000) -> bool:
    """
    Waits for login to complete and handles common post-login scenarios.
    
    Args:
        page: Playwright page instance
        profile_id: Profile identifier for logging
        timeout: Timeout in milliseconds
        
    Returns:
        True if login successful, False otherwise
    """
    start_time = time.time()

    while time.time() - start_time < timeout / 1000:
        try:
            # Check for successful login indicators
            if page.locator('svg[aria-label="Home"]').is_visible(timeout=1000):
                return True

            # Check for "Save Your Login Info" dialog
            if page.locator('text="Save Your Login Info"').is_visible(timeout=1000):
                print(f"📱 [{profile_id}] Handling 'Save Login Info' dialog...")
                page.click('text="Not Now"')
                continue

            # Check for "Turn on Notifications" dialog
            if page.locator('text="Turn on Notifications"').is_visible(timeout=1000):
                print(f"🔔 [{profile_id}] Handling notifications dialog...")
                page.click('text="Not Now"')
                continue

            # Check for two-factor authentication
            if page.locator('text="Two-Factor Authentication"').is_visible(timeout=1000):
                print(f"🔐 [{profile_id}] Two-factor authentication required - login failed")
                return False

            # Check for incorrect password
            if page.locator('text="Sorry, your password was incorrect"').is_visible(timeout=1000):
                print(f"🔑 [{profile_id}] Incorrect password")
                return False

            # Check for suspicious login attempt
            if page.locator('text="Suspicious Login Attempt"').is_visible(timeout=1000):
                print(f"🚨 [{profile_id}] Suspicious login attempt detected")
                return False

        except PlaywrightTimeoutError:
            pass

        time.sleep(0.5)

    print(f"⏰ [{profile_id}] Login completion timeout")
    return False


def navigate_to_post(page: Page, post_url: str) -> bool:
    """
    Navigates to a specific Instagram post.
    
    Args:
        page: Playwright page instance
        post_url: Instagram post URL
        
    Returns:
        True if navigation successful, False otherwise
    """
    try:
        print(f"🎯 Navigating to post: {post_url}")
        page.goto(post_url, timeout=15000)

        # Wait for post to load
        page.wait_for_selector('article', timeout=10000)
        print(f"✅ Post loaded successfully")
        return True

    except PlaywrightTimeoutError:
        print(f"⏰ Timeout loading post: {post_url}")
        return False
    except Exception as e:
        print(f"❌ Error navigating to post: {str(e)}")
        return False


def close_context(context: BrowserContext) -> None:
    """
    Safely closes a browser context.
    
    Args:
        context: BrowserContext to close
    """
    try:
        if context:
            context.close()
            print("🔒 Browser context closed")
    except Exception as e:
        print(f"⚠️ Error closing context: {str(e)}")


def get_profile_info(context: BrowserContext) -> Dict[str, Any]:
    """
    Retrieves profile information from logged-in context.
    
    Args:
        context: Authenticated BrowserContext
        
    Returns:
        Dictionary with profile information
    """
    try:
        page = context.new_page()
        page.goto("https://www.instagram.com/", timeout=10000)

        # Try to get username from profile menu
        page.wait_for_selector('[role="menuitem"]', timeout=5000)
        # This is a simplified implementation
        return {"status": "logged_in", "username": "unknown"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        if 'page' in locals():
            page.close()
