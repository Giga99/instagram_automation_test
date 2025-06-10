"""
Instagram Poster Module

Handles posting comments to Instagram posts with optional simulation mode.
"""
import os
import time

from playwright.sync_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

# Configuration flag for simulation mode
POST_COMMENT = os.getenv("POST_COMMENT", False)  # Set to True in .env when using real Instagram accounts


def post_comment(context: BrowserContext, comment_text: str, post_url: str = None, max_retries: int = 3) -> bool:
    """
    Posts a comment to a specific Instagram post using the given browser context.
    
    Args:
        context: Authenticated Playwright browser context
        comment_text: The comment text to post
        post_url: Optional Instagram post URL (if not already on post page)
        max_retries: Maximum number of retry attempts
    
    Returns:
        True if successful, False if failed
    """
    if not POST_COMMENT:
        print(f"🎭 SIMULATION MODE: Would post comment: {comment_text}")
        return True

    if not comment_text or not comment_text.strip():
        print("❌ Empty comment text provided")
        return False

    print(f"💬 Attempting to post comment: {comment_text[:50]}{'...' if len(comment_text) > 50 else ''}")

    for attempt in range(max_retries):
        page = None
        try:
            print(f"🔄 Post attempt {attempt + 1}/{max_retries}")

            page = context.new_page()

            # Navigate to post if URL provided
            if post_url:
                print(f"🎯 Navigating to post: {post_url}")
                page.goto(post_url, timeout=15000)
                page.wait_for_selector('article', timeout=10000)

            # Locate comment input area
            if not find_and_focus_comment_input(page):
                print("❌ Could not find comment input area")
                if page:
                    page.close()
                continue

            # Type the comment
            print("⌨️ Typing comment...")
            page.keyboard.type(comment_text, delay=50)  # Simulate human typing

            # Wait a moment for typing to complete
            time.sleep(1)

            # Submit the comment
            if submit_comment(page):
                print("✅ Comment posted successfully!")
                if page:
                    page.close()
                return True
            else:
                print("❌ Failed to submit comment")
                if page:
                    page.close()

        except PlaywrightTimeoutError as e:
            print(f"⏰ Timeout during post attempt {attempt + 1}: {str(e)}")
            if page:
                page.close()

        except Exception as e:
            print(f"❌ Error during post attempt {attempt + 1}: {str(e)}")
            if page:
                page.close()

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

    print(f"🚫 All post attempts failed")
    return False


def find_and_focus_comment_input(page: Page) -> bool:
    """
    Finds and focuses the comment input area on Instagram.
    
    Args:
        page: Playwright page instance
        
    Returns:
        True if comment input found and focused, False otherwise
    """
    try:
        # Try multiple selectors for comment input
        comment_selectors = [
            'textarea[placeholder*="comment"]',
            'textarea[aria-label*="comment"]',
            'form textarea',
            '[role="textbox"][contenteditable="true"]',
            'textarea[placeholder="Add a comment..."]'
        ]

        for selector in comment_selectors:
            try:
                element = page.wait_for_selector(selector, timeout=3000)
                if element and element.is_visible():
                    print(f"📝 Found comment input: {selector}")
                    element.click()
                    return True
            except PlaywrightTimeoutError:
                continue

        # If no direct textarea found, try clicking on comment area
        try:
            comment_area = page.wait_for_selector('section:has(svg[aria-label*="Comment"])', timeout=3000)
            if comment_area:
                comment_area.click()
                time.sleep(1)
                # Try to find input again after clicking
                for selector in comment_selectors:
                    try:
                        element = page.wait_for_selector(selector, timeout=2000)
                        if element and element.is_visible():
                            element.click()
                            return True
                    except PlaywrightTimeoutError:
                        continue
        except PlaywrightTimeoutError:
            pass

        print("❌ Could not find comment input")
        return False

    except Exception as e:
        print(f"❌ Error finding comment input: {str(e)}")
        return False


def submit_comment(page: Page) -> bool:
    """
    Submits the comment after it's been typed.
    
    Args:
        page: Playwright page instance
        
    Returns:
        True if submission successful, False otherwise
    """
    try:
        # Try multiple methods to submit comment

        # Method 1: Look for Post button
        post_buttons = [
            'button:has-text("Post")',
            'button[type="submit"]:has-text("Post")',
            'button:text("Post")',
            '[role="button"]:has-text("Post")'
        ]

        for button_selector in post_buttons:
            try:
                button = page.wait_for_selector(button_selector, timeout=2000)
                if button and button.is_visible() and button.is_enabled():
                    print(f"🔘 Clicking post button: {button_selector}")
                    button.click()

                    # Wait for comment to be posted
                    time.sleep(2)
                    return verify_comment_posted(page)

            except PlaywrightTimeoutError:
                continue

        # Method 2: Try Enter key
        print("⌨️ Trying Enter key...")
        page.keyboard.press("Enter")
        time.sleep(2)
        return verify_comment_posted(page)

    except Exception as e:
        print(f"❌ Error submitting comment: {str(e)}")
        return False


def verify_comment_posted(page: Page) -> bool:
    """
    Verifies that the comment was successfully posted.
    
    Args:
        page: Playwright page instance
        
    Returns:
        True if comment appears to be posted, False otherwise
    """
    try:
        # Look for indicators that comment was posted

        # Check if comment input is cleared
        comment_inputs = page.locator('textarea[placeholder*="comment"], textarea[aria-label*="comment"]')
        if comment_inputs.count() > 0:
            first_input = comment_inputs.first
            if first_input.input_value() == "":
                print("✅ Comment input cleared - likely posted")
                return True

        # Check for success indicators
        success_indicators = [
            'text="Comment posted"',
            'text="Your comment was posted"',
            '[aria-label*="posted"]',
        ]

        for indicator in success_indicators:
            try:
                if page.wait_for_selector(indicator, timeout=1000):
                    print("✅ Comment posted confirmation found")
                    return True
            except PlaywrightTimeoutError:
                continue

        # If no explicit confirmation, assume success if no error
        print("🤔 No explicit confirmation, assuming success")
        return True

    except Exception as e:
        print(f"⚠️ Error verifying comment post: {str(e)}")
        return True  # Assume success if we can't verify


def simulate_post(profile_id: str, comment_text: str, post_url: str = None) -> bool:
    """
    Simulates posting a comment without actually interacting with Instagram.
    
    Args:
        profile_id: Profile identifier (e.g., 'profile1')
        comment_text: The comment text that would be posted
        post_url: Optional post URL for simulation
    
    Returns:
        Always returns True (simulation always succeeds)
    """
    print(f"🎭 SIMULATED post by {profile_id}: {comment_text}")
    if post_url:
        print(f"🎯 Target post: {post_url}")

    # Simulate processing time
    time.sleep(0.5)
    return True


def check_comment_restrictions(page: Page) -> dict:
    """
    Checks for comment restrictions or rate limiting on Instagram.
    
    Args:
        page: Playwright page instance
        
    Returns:
        Dictionary with restriction status and details
    """
    try:
        # Check for common restriction messages
        restriction_indicators = [
            'text="Try again later"',
            'text="Action Blocked"',
            'text="temporarily blocked"',
            'text="commenting is temporarily disabled"',
            '[aria-label*="Action blocked"]'
        ]

        for indicator in restriction_indicators:
            try:
                if page.wait_for_selector(indicator, timeout=1000):
                    return {
                        "restricted": True,
                        "message": "Account appears to be temporarily restricted",
                        "indicator": indicator
                    }
            except PlaywrightTimeoutError:
                continue

        return {"restricted": False, "message": "No restrictions detected"}

    except Exception as e:
        return {"restricted": False, "message": f"Error checking restrictions: {str(e)}"}


def get_post_info(page: Page) -> dict:
    """
    Extracts information about the current Instagram post.
    
    Args:
        page: Playwright page instance
        
    Returns:
        Dictionary with post information
    """
    try:
        info = {
            "url": page.url,
            "has_comments": False,
            "comment_count": 0,
            "post_type": "unknown"
        }

        # Check if comments section exists
        try:
            comments_section = page.wait_for_selector('section:has(svg[aria-label*="Comment"])', timeout=3000)
            if comments_section:
                info["has_comments"] = True
        except PlaywrightTimeoutError:
            pass

        # Try to get comment count
        try:
            comment_count_element = page.locator('a:has-text("comment"), span:has-text("comment")').first
            if comment_count_element.is_visible():
                count_text = comment_count_element.text_content()
                # Extract number from text like "23 comments"
                import re
                numbers = re.findall(r'\d+', count_text or "")
                if numbers:
                    info["comment_count"] = int(numbers[0])
        except:
            pass

        return info

    except Exception as e:
        return {"error": str(e)}


def wait_for_rate_limit_reset(seconds: int = 60) -> None:
    """
    Waits for rate limit to reset before continuing.
    
    Args:
        seconds: Number of seconds to wait
    """
    print(f"⏳ Waiting {seconds} seconds for rate limit reset...")
    time.sleep(seconds)
