"""
Comment Generation Module

Handles dynamic comment generation using OpenAI's API.
"""

import os
import time
from typing import List

from openai import OpenAI


def generate_comment(prompt: str, max_retries: int = 3) -> str | None:
    """
    Generates a playful comment for a gym selfie using OpenAI's API.
    
    Args:
        prompt: The prompt to generate comment for (e.g., 'gym selfie')
        max_retries: Maximum number of retry attempts
    
    Returns:
        Generated comment text stripped of extra whitespace
        
    Raises:
        Exception: If OpenAI API call fails after all retries
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)

    # Construct the prompt for gym selfie comments
    system_prompt = "You are a friendly social media copywriter."
    user_prompt = f"Write a playful comment for a {prompt} in around 10-15 words, with a friendly tone. Make it encouraging and positive. Include 1-2 relevant emojis."

    for attempt in range(max_retries):
        try:
            print(f"🤖 Generating comment for '{prompt}' (attempt {attempt + 1}/{max_retries})...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using the specified model from requirements
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50,  # Keep it short and sweet
                temperature=0.9,  # Add some creativity variation
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            if response.choices and response.choices[0].message:
                comment = response.choices[0].message.content.strip()

                # Clean up the comment (remove quotes if AI added them)
                comment = comment.strip('"\'')

                print(f"✅ Generated comment: {comment}")
                return comment
            else:
                raise Exception("Empty response from OpenAI API")

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"🚫 All {max_retries} attempts failed for comment generation")
                raise Exception(f"Failed to generate comment after {max_retries} attempts: {str(e)}")
    return None


def generate_multiple_comments(prompt: str, count: int = 3, ensure_unique: bool = True) -> List[str]:
    """
    Generates multiple unique comments for the same prompt.
    
    Args:
        prompt: The prompt to generate comments for
        count: Number of comments to generate
        ensure_unique: Whether to ensure all comments are unique
    
    Returns:
        List of generated comments
    """
    comments = []
    attempts = 0
    max_total_attempts = count * 3  # Allow extra attempts for uniqueness

    print(f"🎯 Generating {count} {'unique ' if ensure_unique else ''}comments for '{prompt}'...")

    while len(comments) < count and attempts < max_total_attempts:
        try:
            comment = generate_comment(prompt)

            if ensure_unique and comment in comments:
                print(f"🔄 Duplicate comment detected, generating another...")
                attempts += 1
                continue

            comments.append(comment)
            print(f"✅ Comment {len(comments)}/{count} generated")

        except Exception as e:
            print(f"❌ Failed to generate comment: {e}")
            attempts += 1

        attempts += 1

    if len(comments) < count:
        print(f"⚠️  Only generated {len(comments)}/{count} comments after {attempts} attempts")

    return comments


def validate_comment(comment: str, max_length: int = 150, min_length: int = 5) -> bool:
    """
    Validates that a comment meets basic requirements.
    
    Args:
        comment: The comment to validate
        max_length: Maximum allowed comment length
        min_length: Minimum required comment length
    
    Returns:
        True if comment is valid, False otherwise
    """
    if not comment or not isinstance(comment, str):
        return False

    comment = comment.strip()

    # Check length requirements
    if len(comment) < min_length or len(comment) > max_length:
        return False

    # Check for inappropriate content (basic filtering)
    banned_words = ['spam', 'fake', 'bot', 'advertisement', 'promotion']
    comment_lower = comment.lower()

    if any(word in comment_lower for word in banned_words):
        return False

    return True


def get_comment_variations(base_prompt: str = "gym selfie") -> List[str]:
    """
    Returns different prompt variations for more diverse comments.
    
    Args:
        base_prompt: The base prompt to create variations from
    
    Returns:
        List of prompt variations
    """
    variations = [
        f"{base_prompt}",
        f"motivational {base_prompt}",
        f"inspiring {base_prompt}",
        f"fitness {base_prompt}",
        f"workout {base_prompt}"
    ]

    return variations


# Test function for development/debugging
def test_comment_generation():
    """
    Test function to verify comment generation is working correctly.
    """
    print("🧪 Testing comment generation...")

    try:
        # Test single comment generation
        comment = generate_comment("gym selfie")
        print(f"✅ Single comment test passed: {comment}")

        # Validate the comment
        is_valid = validate_comment(comment)
        print(f"✅ Comment validation: {'PASSED' if is_valid else 'FAILED'}")

        # Test multiple comment generation
        comments = generate_multiple_comments("workout selfie", count=2)
        print(f"✅ Multiple comments test: Generated {len(comments)} comments")

        return True

    except Exception as e:
        print(f"❌ Comment generation test failed: {e}")
        return False
