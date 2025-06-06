"""
Instagram Automation Main Script

Orchestrates the entire Instagram comment automation process:
1. Manages three isolated Instagram profiles using Playwright
2. Generates dynamic comments via OpenAI API
3. Posts comments to target Instagram post
4. Logs all activities with structured logging
5. Sends Telegram notification upon completion
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Playwright

from modules.comment_gen import generate_comment, validate_comment
from modules.logger import init_logger, write_log_entry, get_current_timestamp, get_log_summary
from modules.notifier import send_completion_notification, send_error_notification, send_progress_notification
from modules.poster import post_comment, simulate_post, USE_REAL_INSTAGRAM
from modules.profile_manager import login_profile, close_context

# Configuration
TARGET_POST_URL = os.getenv("INSTAGRAM_TARGET_POST", "")  # Set this to your target Instagram post URL
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
COMMENT_PROMPT = os.getenv("COMMENT_PROMPT", "gym workout motivation")


def load_profile_configs() -> List[Dict[str, str]]:
    """
    Loads profile configurations from environment variables.
    
    Returns:
        List of profile dictionaries with id, username, and password
    """
    profiles = []

    for i in range(1, 4):  # profiles 1-3
        username = os.getenv(f"INSTAGRAM_USER{i}")
        password = os.getenv(f"INSTAGRAM_PASS{i}")

        if username and password:
            profiles.append({
                "id": f"profile{i}",
                "username": username,
                "password": password
            })
        else:
            print(f"⚠️ Profile {i} credentials not found (INSTAGRAM_USER{i}/INSTAGRAM_PASS{i})")

    return profiles


def process_single_profile(playwright: Playwright, profile: Dict[str, str],
                           target_post_url: str, comment_prompt: str) -> Dict[str, Any]:
    """
    Processes a single profile through the complete automation workflow.
    
    Args:
        playwright: Playwright instance
        profile: Profile configuration dictionary
        target_post_url: Instagram post URL to comment on
        comment_prompt: Prompt for comment generation
        
    Returns:
        Dictionary with processing results
    """
    profile_id = profile["id"]
    username = profile["username"]
    password = profile["password"]

    result = {
        "profile_id": profile_id,
        "success": False,
        "comment": "",
        "error": None,
        "timestamp": get_current_timestamp()
    }

    context = None

    try:
        print(f"\n{'=' * 60}")
        print(f"🚀 Processing {profile_id} ({username})")
        print(f"{'=' * 60}")

        # Step 1: Generate comment
        print(f"🤖 [{profile_id}] Generating comment...")
        send_progress_notification(profile_id, "Generating comment...")

        comment = generate_comment(comment_prompt)
        if not comment or not validate_comment(comment):
            error_msg = "Failed to generate valid comment"
            print(f"❌ [{profile_id}] {error_msg}")
            result["error"] = error_msg
            write_log_entry(profile_id, "", result["timestamp"], error_msg)
            send_error_notification(error_msg, profile_id)
            return result

        result["comment"] = comment
        print(f"✅ [{profile_id}] Generated comment: {comment}")

        # Step 2: Login to Instagram
        print(f"🔐 [{profile_id}] Logging into Instagram...")
        send_progress_notification(profile_id, "Logging into Instagram...")

        context = login_profile(
            playwright=playwright,
            profile_id=profile_id,
            username=username,
            password=password,
            target_post_url=target_post_url,
            headless=HEADLESS_MODE
        )

        if not context:
            error_msg = "Failed to login to Instagram"
            print(f"❌ [{profile_id}] {error_msg}")
            result["error"] = error_msg
            write_log_entry(profile_id, comment, result["timestamp"], error_msg)
            send_error_notification(error_msg, profile_id)
            return result

        print(f"✅ [{profile_id}] Successfully logged in")
        send_progress_notification(profile_id, "Login successful", comment)

        # Step 3: Post comment
        print(f"💬 [{profile_id}] Posting comment...")
        send_progress_notification(profile_id, "Posting comment...", comment)

        if USE_REAL_INSTAGRAM:
            post_success = post_comment(context, comment, target_post_url)
        else:
            post_success = simulate_post(profile_id, comment, target_post_url)

        if post_success:
            print(f"✅ [{profile_id}] Comment posted successfully!")
            result["success"] = True
            write_log_entry(profile_id, comment, result["timestamp"])
            send_progress_notification(profile_id, "Comment posted successfully", comment)
        else:
            error_msg = "Failed to post comment"
            print(f"❌ [{profile_id}] {error_msg}")
            result["error"] = error_msg
            write_log_entry(profile_id, comment, result["timestamp"], error_msg)
            send_error_notification(error_msg, profile_id)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"💥 [{profile_id}] {error_msg}")
        result["error"] = error_msg
        write_log_entry(profile_id, result.get("comment", ""), result["timestamp"], error_msg)
        send_error_notification(error_msg, profile_id)

    finally:
        # Clean up browser context
        if context:
            print(f"🔒 [{profile_id}] Closing browser context...")
            close_context(context)

    return result


def main():
    """Main orchestrator function that runs the entire automation process."""

    # Load environment variables
    load_dotenv()

    print("🚀 Instagram Automation Starting...")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎭 Simulation Mode: {'ON' if not USE_REAL_INSTAGRAM else 'OFF'}")
    print(f"👤 Headless Mode: {'ON' if HEADLESS_MODE else 'OFF'}")

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Initialize logger
    log_file = f"output/comments_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    init_logger(log_file)
    print(f"📝 Log file: {log_file}")

    # Load profile configurations
    profiles = load_profile_configs()
    if not profiles:
        print("❌ No valid profile configurations found!")
        print("💡 Make sure to set INSTAGRAM_USER1/INSTAGRAM_PASS1, etc. in your .env file")
        return

    print(f"👥 Found {len(profiles)} profile(s): {[p['id'] for p in profiles]}")

    # Check target post URL
    if not TARGET_POST_URL:
        print("⚠️ No target post URL set!")
        print("💡 Set INSTAGRAM_TARGET_POST in your .env file")
        if USE_REAL_INSTAGRAM:
            print("❌ Cannot proceed without target post URL in real mode")
            return
        else:
            print("🎭 Continuing with simulation mode...")
    else:
        print(f"🎯 Target post: {TARGET_POST_URL}")

    # Process all profiles
    results = []
    successful_profiles = []
    failed_profiles = []

    with sync_playwright() as playwright:
        for i, profile in enumerate(profiles, 1):
            print(f"\n🔄 Processing profile {i}/{len(profiles)}")

            try:
                result = process_single_profile(
                    playwright=playwright,
                    profile=profile,
                    target_post_url=TARGET_POST_URL,
                    comment_prompt=COMMENT_PROMPT
                )

                results.append(result)

                if result["success"]:
                    successful_profiles.append(result["profile_id"])
                else:
                    failed_profiles.append(result["profile_id"])

                # Add delay between profiles to avoid rate limiting
                if i < len(profiles):
                    delay = 30  # 30 seconds between profiles
                    print(f"⏳ Waiting {delay} seconds before next profile...")
                    time.sleep(delay)

            except KeyboardInterrupt:
                print("\n⚠️ Process interrupted by user")
                break
            except Exception as e:
                print(f"💥 Critical error processing {profile['id']}: {str(e)}")
                failed_profiles.append(profile["id"])
                continue

    # Generate summary
    summary = get_log_summary(log_file)

    # Display results
    print(f"\n{'=' * 80}")
    print("📊 AUTOMATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"📝 Total Profiles: {len(profiles)}")
    print(f"✅ Successful: {len(successful_profiles)} ({successful_profiles})")
    print(f"❌ Failed: {len(failed_profiles)} ({failed_profiles})")
    print(f"📈 Success Rate: {summary.get('success_rate', '0%')}")
    print(f"📄 Log File: {log_file}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Send completion notification
    try:
        print(f"\n📱 Sending completion notification...")
        send_completion_notification(summary)
        print(f"✅ Notification sent successfully")
    except Exception as e:
        print(f"❌ Failed to send notification: {str(e)}")

    print(f"\n🎉 Instagram Automation Complete!")

    # Return appropriate exit code
    if failed_profiles:
        print(f"⚠️ Some profiles failed - check logs for details")
        sys.exit(1)
    else:
        print(f"✅ All profiles processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Automation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        sys.exit(1)
