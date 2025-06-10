"""
AdsPower Profile Manager

Integrates AdsPower profiles with Playwright for Instagram automation.
Provides seamless management of browser contexts through AdsPower Local API.
"""

import time
from typing import Optional, Dict, Any, List

from playwright.sync_api import BrowserContext, Playwright, Page, TimeoutError as PlaywrightTimeoutError

from .client import AdsPowerClient, AdsPowerProfile


class AdsPowerProfileManager:
    """
    Manages Instagram automation using AdsPower profiles and Playwright.
    
    This class provides integration between AdsPower's profile management
    and Playwright's browser automation capabilities.
    """
    
    def __init__(self, adspower_base_url: str = "http://localhost:50325", 
                 adspower_api_key: Optional[str] = None,
                 allow_credential_fallback: bool = True,
                 credential_fallback_timeout: int = 60):
        """
        Initialize the AdsPower profile manager.
        
        Args:
            adspower_base_url: AdsPower Local API base URL
            adspower_api_key: API key for headless mode (optional)
            allow_credential_fallback: Whether to allow automatic credential fallback when auto-login fails
            credential_fallback_timeout: Timeout in seconds for login completion
        """
        self.adspower_client = AdsPowerClient(adspower_base_url, adspower_api_key)
        self.active_contexts: Dict[str, BrowserContext] = {}
        self.allow_credential_fallback = allow_credential_fallback
        self.credential_fallback_timeout = credential_fallback_timeout
    
    def check_adspower_connection(self) -> bool:
        """
        Check if AdsPower is running and accessible.
        
        Returns:
            True if AdsPower API is accessible, False otherwise
        """
        return self.adspower_client.check_connection()
    
    def get_available_profiles(self, group_id: Optional[str] = None) -> List[AdsPowerProfile]:
        """
        Get all available AdsPower profiles.
        
        Args:
            group_id: Optional group ID to filter profiles
            
        Returns:
            List of available profiles
        """
        return self.adspower_client.get_profiles(group_id)
    
    def login_profile(self, playwright: Playwright, profile_id: str, 
                     username: str, password: str,
                     target_post_url: str = None, headless: bool = True,
                     max_retries: int = 3) -> Optional[BrowserContext]:
        """
        Start an AdsPower profile and connect it with Playwright.
        
        Args:
            playwright: Playwright instance
            profile_id: AdsPower profile ID
            username: Instagram username for fallback login
            password: Instagram password for fallback login
            target_post_url: Optional Instagram post URL to navigate to
            headless: Whether to run in headless mode
            max_retries: Maximum number of retry attempts
            
        Returns:
            BrowserContext if successful, None if failed
        """
        if not self.check_adspower_connection():
            print(f"❌ [{profile_id}] AdsPower is not running or not accessible")
            return None
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 [{profile_id}] Starting AdsPower profile (attempt {attempt + 1}/{max_retries})")
                
                # Start AdsPower profile
                browser_data = self.adspower_client.start_profile(profile_id, headless)
                if not browser_data:
                    print(f"❌ [{profile_id}] Failed to start AdsPower profile")
                    continue
                
                # Connect Playwright to the AdsPower browser
                context = self._connect_playwright_to_adspower(
                    playwright, profile_id, username, password, browser_data, target_post_url
                )
                
                if context:
                    self.active_contexts[profile_id] = context
                    print(f"✅ [{profile_id}] Successfully connected to AdsPower profile")
                    return context
                
            except Exception as e:
                print(f"❌ [{profile_id}] Error during profile login attempt {attempt + 1}: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⏳ [{profile_id}] Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
        
        print(f"🚫 [{profile_id}] All login attempts failed")
        return None
    
    def _connect_playwright_to_adspower(self, playwright: Playwright, profile_id: str,
                                       username: str, password: str,
                                       browser_data: Dict[str, Any], 
                                       target_post_url: str = None) -> Optional[BrowserContext]:
        """
        Connect Playwright to an AdsPower browser instance.
        
        Args:
            playwright: Playwright instance
            profile_id: Profile identifier
            username: Instagram username for fallback login
            password: Instagram password for fallback login
            browser_data: Browser connection data from AdsPower
            target_post_url: Optional post URL to navigate to
            
        Returns:
            BrowserContext if successful, None if failed
        """
        try:
            # Get WebSocket endpoint for Playwright
            ws_endpoint = browser_data.get("ws", {}).get("puppeteer")
            if not ws_endpoint:
                print(f"❌ [{profile_id}] No WebSocket endpoint found in AdsPower response")
                return None
            
            # Connect Playwright to the browser
            browser = playwright.chromium.connect_over_cdp(ws_endpoint)
            
            # Get the default context (AdsPower profile context)
            contexts = browser.contexts
            if not contexts:
                print(f"❌ [{profile_id}] No browser contexts available")
                browser.close()
                return None
            
            context = contexts[0]
            
            # Get or create a page
            pages = context.pages
            if pages:
                page = pages[0]
            else:
                page = context.new_page()
            
            # Navigate to Instagram login if not already there
            current_url = page.url
            if "instagram.com" not in current_url:
                print(f"🌐 [{profile_id}] Navigating to Instagram...")
                page.goto("https://www.instagram.com/", timeout=30000)
            
            # Check if already logged in or handle login
            if self._handle_instagram_login(page, profile_id, username, password):
                # Navigate to target post if provided
                if target_post_url:
                    self._navigate_to_post(page, target_post_url)
                
                return context
            else:
                print(f"❌ [{profile_id}] Instagram login failed")
                browser.close()
                return None
            
        except Exception as e:
            print(f"❌ [{profile_id}] Error connecting Playwright to AdsPower: {str(e)}")
            return None
    
    def _handle_instagram_login(self, page: Page, profile_id: str,
                               username: str, password: str) -> bool:
        """
        Handle Instagram login process if needed.
        
        Args:
            page: Playwright page instance
            profile_id: Profile identifier for logging
            username: Instagram username for fallback login
            password: Instagram password for fallback login
            
        Returns:
            True if login successful or already logged in, False otherwise
        """
        try:
            # Check if already logged in
            if self._is_already_logged_in(page):
                print(f"✅ [{profile_id}] Already logged into Instagram")
                return True
            
            # Handle cookies popup first
            self._handle_cookies_popup(page, profile_id)
            
            # Wait for potential auto-login (AdsPower may auto-fill credentials)
            print(f"⏳ [{profile_id}] Waiting for auto-login...")
            time.sleep(5)
            
            # Check again if logged in after auto-login attempt
            if self._is_already_logged_in(page):
                print(f"✅ [{profile_id}] Auto-login successful")
                return True
            
            # If still not logged in, offer automatic credential fallback
            print(f"⚠️ [{profile_id}] Auto-login failed - profile may need automatic credential fallback")
            return self._handle_credential_fallback(page, profile_id, username, password)
            
        except Exception as e:
            print(f"❌ [{profile_id}] Error during Instagram login: {str(e)}")
            return False
    
    def _handle_credential_fallback(self, page: Page, profile_id: str,
                                      username: str, password: str) -> bool:
        """
        Handle automatic credential fallback when auto-login fails.
        
        Args:
            page: Playwright page instance
            profile_id: Profile identifier for logging
            username: Instagram username for fallback login
            password: Instagram password for fallback login
            
        Returns:
            True if login successful, False otherwise
        """
        # Check if credentials are available
        if not username or not password:
            print(f"❌ [{profile_id}] No credentials available for fallback login")
            return False
            
        # Check if automatic credential fallback is allowed
        if not self.allow_credential_fallback:
            print(f"❌ [{profile_id}] Automatic credential fallback disabled - profile needs proper AdsPower configuration")
            return False
            
        try:
            print(f"🔐 [{profile_id}] Attempting automatic credential fallback with credentials...")
            
            # Check if we're on a login page
            current_url = page.url
            if "instagram.com/accounts/login" not in current_url:
                # Navigate to login page
                print(f"🌐 [{profile_id}] Navigating to login page...")
                page.goto("https://www.instagram.com/accounts/login/", timeout=15000)
                time.sleep(3)
            
            # Wait for login form
            page.wait_for_selector('input[name="username"]', timeout=10000)
            
            # Check for login form
            username_input = page.locator('input[name="username"]')
            password_input = page.locator('input[name="password"]')
            
            if username_input.is_visible() and password_input.is_visible():
                print(f"📝 [{profile_id}] Filling login credentials...")
                
                # Fill login form
                page.fill('input[name="username"]', username)
                page.fill('input[name="password"]', password)
                
                # Click login button
                page.click('button[type="submit"]')
                
                # Wait for login completion
                print(f"⏳ [{profile_id}] Waiting for login completion...")
                return self._wait_for_login_completion(page, profile_id)
            else:
                print(f"❌ [{profile_id}] Login form not found")
                return False
                
        except Exception as e:
            print(f"❌ [{profile_id}] Error in automatic credential fallback: {str(e)}")
            return False
    
    def _wait_for_login_completion(self, page: Page, profile_id: str, timeout: int = 15000) -> bool:
        """
        Wait for login to complete and handle common post-login scenarios.
        
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
                    print(f"✅ [{profile_id}] Login successful!")
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
    
    def _is_already_logged_in(self, page: Page) -> bool:
        """
        Check if user is already logged into Instagram.
        
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
    
    def _handle_cookies_popup(self, page: Page, profile_id: str) -> None:
        """
        Handle Instagram cookies consent popup if it appears.
        
        Args:
            page: Playwright page instance
            profile_id: Profile identifier for logging
        """
        try:
            cookie_selectors = [
                'button[data-cookiebanner="accept_only_essential_cookie"]',
                'button:has-text("Only allow essential cookies")',
                'button:has-text("Accept")',
                'button:has-text("Allow essential and optional cookies")',
                '[data-testid="cookie-banner"] button',
                'button:has-text("Decline optional cookies")',
                'button:has-text("Allow all cookies")'
            ]
            
            print(f"🍪 [{profile_id}] Checking for cookies popup...")
            time.sleep(2)
            
            for selector in cookie_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        print(f"🍪 [{profile_id}] Found cookies popup, clicking: {selector}")
                        page.click(selector, timeout=3000)
                        time.sleep(1)
                        print(f"✅ [{profile_id}] Cookies popup handled")
                        return
                except PlaywrightTimeoutError:
                    continue
                except Exception as e:
                    print(f"⚠️ [{profile_id}] Error with selector {selector}: {str(e)}")
                    continue
            
            print(f"ℹ️ [{profile_id}] No cookies popup found or already handled")
            
        except Exception as e:
            print(f"⚠️ [{profile_id}] Error handling cookies popup: {str(e)}")
    
    def _navigate_to_post(self, page: Page, post_url: str) -> bool:
        """
        Navigate to a specific Instagram post.
        
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
    
    def close_context(self, profile_id: str) -> None:
        """
        Close browser context and stop AdsPower profile.
        
        Args:
            profile_id: Profile ID to close
        """
        try:
            # Close Playwright context if exists
            if profile_id in self.active_contexts:
                context = self.active_contexts[profile_id]
                context.close()
                del self.active_contexts[profile_id]
                print(f"🔒 [{profile_id}] Playwright context closed")
            
            # Stop AdsPower profile
            success = self.adspower_client.stop_profile(profile_id)
            if success:
                print(f"🔒 [{profile_id}] AdsPower profile stopped")
            else:
                print(f"⚠️ [{profile_id}] Failed to stop AdsPower profile")
                
        except Exception as e:
            print(f"⚠️ [{profile_id}] Error closing context: {str(e)}")
    
    def get_profile_status(self, profile_id: str) -> str:
        """
        Get the current status of an AdsPower profile.
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            Profile status string
        """
        return self.adspower_client.check_profile_status(profile_id)
    
    def cleanup_all_contexts(self) -> None:
        """
        Close all active contexts and stop all profiles.
        """
        print("🔒 Cleaning up all active AdsPower contexts...")
        
        for profile_id in list(self.active_contexts.keys()):
            self.close_context(profile_id)
        
        print("✅ All AdsPower contexts cleaned up") 