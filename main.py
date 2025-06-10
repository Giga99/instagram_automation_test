"""
Instagram Automation Main Script

Orchestrates Instagram comment automation using AdsPower profiles:
1. Manages Instagram profiles through AdsPower API
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

from playwright.sync_api import sync_playwright, Playwright

from src.integrations.adspower.config import load_adspower_profiles
from src.integrations.adspower.profile_manager import AdsPowerProfileManager
from src.integrations.instagram.poster import post_comment, simulate_post, POST_COMMENT
from src.integrations.openai.comment_gen import generate_comment, validate_comment
from src.integrations.telegram.notifier import send_completion_notification, send_error_notification, \
    send_progress_notification
from src.utils.config import config
from src.utils.logger import init_logger, write_log_entry, get_current_timestamp, get_log_summary


def load_profile_configs() -> List[Dict[str, any]]:
    """
    Load profiles from AdsPower configuration.
    
    Returns:
        List of AdsPower profile dictionaries ready for automation
    """
    print("🏢 Loading profiles from AdsPower...")

    try:
        profiles = load_adspower_profiles()

        if not profiles:
            print("❌ No AdsPower profiles found!")
            return []

        print(f"✅ Loaded {len(profiles)} AdsPower profiles ready for automation")
        return profiles

    except Exception as e:
        print(f"❌ Error loading AdsPower profiles: {str(e)}")
        print("💡 Make sure AdsPower is running and configured properly")
        return []


def process_single_profile(playwright: Playwright, profile: Dict[str, str],
                           target_post_url: str, headless_mode: bool, comment_prompt: str) -> Dict[str, Any]:
    """
    Processes a single AdsPower profile through the complete automation workflow.
    
    Args:
        playwright: Playwright instance
        profile: AdsPower profile configuration dictionary
        target_post_url: Instagram post URL to comment on
        headless_mode: Headless mode flag for AdsPower session
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
    adspower_manager = None

    try:
        print(f"\n{'=' * 60}")
        print(f"🚀 Processing AdsPower Profile: {profile_id} ({username})")
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

        # Step 2: Connect to AdsPower profile
        print(f"🔐 [{profile_id}] Connecting to AdsPower profile...")
        send_progress_notification(profile_id, "Connecting to AdsPower...")

        # Initialize AdsPower manager with automatic login fallback options
        adspower_manager = AdsPowerProfileManager(
            allow_credential_fallback=True,  # Enable automatic login fallback with credentials
            credential_fallback_timeout=90  # 90-second timeout for login completion
        )
        context = adspower_manager.login_profile(playwright, profile_id, username, password, target_post_url,
                                                 headless_mode)

        if not context:
            error_msg = "Failed to connect to AdsPower profile"
            print(f"❌ [{profile_id}] {error_msg}")
            result["error"] = error_msg
            write_log_entry(profile_id, comment, result["timestamp"], error_msg)
            send_error_notification(error_msg, profile_id)
            return result

        print(f"✅ [{profile_id}] Connected to AdsPower profile")

        send_progress_notification(profile_id, "AdsPower session ready", comment)

        # Step 3: Post comment
        print(f"💬 [{profile_id}] Posting comment...")
        send_progress_notification(profile_id, "Posting comment...", comment)

        if POST_COMMENT:
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
        # Clean up AdsPower context
        if adspower_manager:
            print(f"🔒 [{profile_id}] Closing AdsPower context...")
            adspower_manager.close_context(profile_id)

    return result


def main():
    """Main orchestrator function that runs the entire AdsPower automation process."""

    print("🚀 Instagram Automation Starting")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎭 Simulation Mode: {'ON' if not config.post_comment else 'OFF'}")
    print(f"👤 Headless Mode: {'ON' if config.headless_mode else 'OFF'}")
    print(f"🏢 Profile Manager: AdsPower Professional")

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Initialize logger
    log_file = f"output/adspower_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    init_logger(log_file)
    print(f"📝 Log file: {log_file}")

    # Load AdsPower profile configurations
    profiles = load_profile_configs()
    if not profiles:
        print("❌ No valid AdsPower profiles found!")
        return

    print(f"👥 Found {len(profiles)} AdsPower profile(s):")
    for p in profiles:
        profile_type = "AdsPower"
        if p.get('group'):
            profile_type += f" - ({p['group']})"
        print(f"   • {p['id']}{profile_type}")

    # Check target post URL
    if not config.instagram_post_url:
        print("⚠️ No target post URL set!")
        print("💡 Set INSTAGRAM_POST_URL in your .env file")
        if config.post_comment:
            print("❌ Cannot proceed without target post URL in real mode")
            return
        else:
            print("🎭 Continuing with simulation mode...")
    else:
        print(f"🎯 Target post: {config.instagram_post_url}")

    # Process all AdsPower profiles
    results = []
    successful_profiles = []
    failed_profiles = []

    with sync_playwright() as playwright:
        for i, profile in enumerate(profiles, 1):
            print(f"\n🔄 Processing AdsPower profile {i}/{len(profiles)}")

            try:
                result = process_single_profile(
                    playwright=playwright,
                    profile=profile,
                    target_post_url=config.instagram_post_url,
                    headless_mode=config.headless_mode,
                    comment_prompt=config.comment_prompt
                )

                results.append(result)

                if result["success"]:
                    successful_profiles.append(result["profile_id"])
                else:
                    failed_profiles.append(result["profile_id"])

                # Add intelligent delay between profiles
                if i < len(profiles):
                    current_profile = profiles[i - 1]
                    next_profile = profiles[i] if i < len(profiles) else None

                    # Use profile-specific delay or default
                    delay = current_profile.get('settings', {}).get('delay_between_profiles', 30)

                    # Add extra delay for different groups
                    if next_profile and current_profile.get('group') != next_profile.get('group'):
                        delay += 10  # Extra 10 seconds for group switching
                        print(
                            f"🔄 Switching from group '{current_profile.get('group', 'default')}' to '{next_profile.get('group', 'default')}'")

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
    print("📊 ADSPOWER AUTOMATION SUMMARY")
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

    print(f"\n🎉 AdsPower Instagram Automation Complete!")

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
        print("💡 Make sure AdsPower is running and properly configured")
        sys.exit(1)
