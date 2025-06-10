"""
Notifier Module

Handles sending Telegram notifications upon completion of comment posting.
"""

import os
import time
from typing import Optional, Dict, Any

import requests


class TelegramNotifier:
    """
    Telegram notification manager with internal credential handling.
    
    This approach eliminates parameter pollution while maintaining testability.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize notifier with optional explicit credentials.
        Falls back to environment variables if not provided.
        
        Args:
            bot_token: Optional explicit bot token (defaults to TG_BOT_TOKEN env var)
            chat_id: Optional explicit chat ID (defaults to TG_CHAT_ID env var)
        """
        self.bot_token = bot_token or os.getenv("TG_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TG_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            raise ValueError(
                "Telegram credentials required. Set TG_BOT_TOKEN and TG_CHAT_ID environment variables "
                "or pass them explicitly to constructor."
            )

    def _send_message(self, message: str, max_retries: int = 3) -> None:
        """
        Internal method to send messages to Telegram.
        
        Args:
            message: Message text to send
            max_retries: Maximum number of retry attempts
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        for attempt in range(max_retries):
            try:
                print(f"📤 Sending Telegram notification (attempt {attempt + 1}/{max_retries})...")

                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()

                result = response.json()
                if result.get("ok"):
                    print(f"✅ Telegram notification sent successfully!")
                    print(f"📱 Message ID: {result.get('result', {}).get('message_id', 'unknown')}")
                    return
                else:
                    error_msg = result.get("description", "Unknown error")
                    raise Exception(f"Telegram API error: {error_msg}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error on attempt {attempt + 1}: {str(e)}")
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

        raise Exception(f"Failed to send Telegram notification after {max_retries} attempts")

    def send_completion(self, summary: Dict[str, Any]) -> None:
        """
        Send completion notification with execution summary.
        
        Args:
            summary: Dictionary containing execution summary data
        """
        message_parts = [
            "🎉 <b>Instagram Automation Completed</b>",
            "",
            f"📊 <b>Execution Summary:</b>",
            f"• Total Operations: {summary.get('total_entries', 0)}",
            f"• Successful: {summary.get('successful', 0)} ✅",
            f"• Errors: {summary.get('errors', 0)} ❌",
            f"• Success Rate: {summary.get('success_rate', '0%')}",
            "",
            f"👥 <b>Profiles Processed:</b>",
        ]

        profiles = summary.get('profiles_processed', [])
        if profiles:
            for profile in profiles:
                message_parts.append(f"• {profile}")
        else:
            message_parts.append("• No profiles processed")

        message_parts.extend([
            "",
            f"🕒 <b>Completed at:</b> {summary.get('latest_timestamp', 'Unknown')}",
            "",
            "📝 Check logs for detailed information."
        ])

        message = "\n".join(message_parts)

        try:
            self._send_message(message)
        except Exception as e:
            print(f"❌ Failed to send completion notification: {e}")
            # Fallback message
            fallback = "✅ Instagram automation completed. Check logs for details."
            try:
                self._send_message(fallback)
            except Exception as fallback_error:
                print(f"❌ Fallback notification also failed: {fallback_error}")
                raise

    def send_error(self, error_message: str, profile_id: Optional[str] = None) -> None:
        """
        Send error notification.
        
        Args:
            error_message: Error message to send
            profile_id: Optional profile ID where error occurred
        """
        profile_info = f" ({profile_id})" if profile_id else ""
        message = f"🚨 <b>Instagram Automation Error{profile_info}</b>\n\n❌ {error_message}"

        try:
            self._send_message(message)
        except Exception as e:
            print(f"❌ Failed to send error notification: {e}")

    def send_progress(self, profile_id: str, status: str, comment: Optional[str] = None) -> None:
        """
        Send progress notification for individual profile updates.
        
        Args:
            profile_id: Profile identifier
            status: Status message (e.g., "Login successful", "Comment posted")
            comment: Optional comment text
        """
        message_parts = [
            f"📱 <b>Profile Update: {profile_id}</b>",
            f"📈 Status: {status}"
        ]

        if comment:
            truncated_comment = comment[:100] + "..." if len(comment) > 100 else comment
            message_parts.append(f"💬 Comment: {truncated_comment}")

        message = "\n".join(message_parts)

        try:
            self._send_message(message)
        except Exception as e:
            print(f"❌ Failed to send progress notification: {e}")

    def validate_credentials(self) -> bool:
        """
        Validate Telegram credentials by sending a test message.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            self._send_message("🔧 Testing Telegram connection...", max_retries=1)
            return True
        except Exception as e:
            print(f"❌ Telegram credentials validation failed: {e}")
            return False

    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the Telegram bot.
        
        Returns:
            Bot information dictionary or None if failed
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                print(f"🤖 Bot info: {bot_info.get('first_name', 'Unknown')} (@{bot_info.get('username', 'unknown')})")
                return bot_info
            else:
                print(f"❌ Failed to get bot info: {result.get('description', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"❌ Error getting bot info: {e}")
            return None


# Global notifier instance for simple usage
_notifier = None


def get_notifier() -> TelegramNotifier:
    """
    Get the global notifier instance, creating it if necessary.
    
    Returns:
        Global TelegramNotifier instance
    """
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier


# Convenience functions for backward compatibility and simple usage
def send_completion_notification(summary: Dict[str, Any]) -> None:
    """Send completion notification using global notifier."""
    get_notifier().send_completion(summary)


def send_error_notification(error_message: str, profile_id: Optional[str] = None) -> None:
    """Send error notification using global notifier."""
    get_notifier().send_error(error_message, profile_id)


def send_progress_notification(profile_id: str, status: str, comment: Optional[str] = None) -> None:
    """Send progress notification using global notifier."""
    get_notifier().send_progress(profile_id, status, comment)


def validate_telegram_credentials() -> bool:
    """Validate Telegram credentials using global notifier."""
    try:
        return get_notifier().validate_credentials()
    except ValueError:
        return False


def get_bot_info() -> Optional[Dict[str, Any]]:
    """Get bot info using global notifier."""
    try:
        return get_notifier().get_bot_info()
    except ValueError:
        return None


# Backward compatibility functions for testing
def send_telegram(bot_token: str, chat_id: str, message: str, max_retries: int = 3) -> None:
    """
    Legacy function for backward compatibility with tests.
    Creates temporary notifier instance with explicit credentials.
    """
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
    notifier._send_message(message, max_retries)


# Test function
def test_telegram_notification():
    """Test function to verify Telegram notifications are working correctly."""
    print("🧪 Testing Telegram notification...")

    try:
        notifier = TelegramNotifier()

        # Test basic message
        notifier._send_message("🧪 Test message from Instagram Automation")

        # Test with summary
        test_summary = {
            "total_entries": 3,
            "successful": 2,
            "errors": 1,
            "success_rate": "66.7%",
            "profiles_processed": ["profile1", "profile2", "profile3"],
            "latest_timestamp": "2025-06-07T12:34:56Z"
        }

        notifier.send_completion(test_summary)

        print("✅ Telegram notification test passed")
        return True

    except Exception as e:
        print(f"❌ Telegram notification test failed: {e}")
        return False
