#!/usr/bin/env python3
"""
Comprehensive Test Runner for Instagram Automation Project

Runs all test suites and provides a detailed summary report:
- Logger module tests
- Comment generation module tests  
- Notifier module tests
- Integration tests
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import individual test runners
from tests.test_logger import run_logger_tests
from tests.test_comment_gen import run_comment_gen_tests
from tests.test_notifier import run_notifier_tests
from tests.test_integration import run_integration_tests


def print_header(title):
    """Print a formatted header for test sections."""
    print("\n" + "🔥" * 60)
    print(f"🚀 {title}")
    print("🔥" * 60)


def print_summary(results):
    """Print a comprehensive test summary."""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    total_modules = len(results)
    passed_modules = sum(1 for success in results.values() if success)
    
    # Overall results
    print(f"\n🎯 Overall Results:")
    print(f"   • Total Test Modules: {total_modules}")
    print(f"   • Modules Passed: {passed_modules}")
    print(f"   • Modules Failed: {total_modules - passed_modules}")
    print(f"   • Overall Success Rate: {(passed_modules / total_modules * 100):.1f}%")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for module, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   • {module}: {status}")
    
    # Status
    overall_success = all(results.values())
    if overall_success:
        print(f"\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  Some tests failed. Please review the output above.")
        print(f"   Fix any failing tests.")
    
    print("=" * 80)
    return overall_success


def run_all_tests():
    """Run all test suites and return overall success status."""
    print_header("INSTAGRAM AUTOMATION PROJECT - COMPREHENSIVE TEST SUITE")
    print("🧪 Running all tests of modules...")
    print("   This will test Logger, Comment Generation, Notifier, and Integration")
    
    results = {}
    
    try:
        # Run Logger Tests
        print_header("LOGGER MODULE TESTS")
        results["Logger Module"] = run_logger_tests()
        
    except Exception as e:
        print(f"❌ Logger tests crashed: {e}")
        results["Logger Module"] = False
    
    try:
        # Run Comment Generation Tests
        print_header("COMMENT GENERATION MODULE TESTS")
        results["Comment Generation Module"] = run_comment_gen_tests()
        
    except Exception as e:
        print(f"❌ Comment generation tests crashed: {e}")
        results["Comment Generation Module"] = False
    
    try:
        # Run Notifier Tests
        print_header("NOTIFIER MODULE TESTS")
        results["Notifier Module"] = run_notifier_tests()
        
    except Exception as e:
        print(f"❌ Notifier tests crashed: {e}")
        results["Notifier Module"] = False
    
    try:
        # Run Integration Tests
        print_header("INTEGRATION TESTS")
        results["Integration Tests"] = run_integration_tests()
        
    except Exception as e:
        print(f"❌ Integration tests crashed: {e}")
        results["Integration Tests"] = False
    
    # Print comprehensive summary
    overall_success = print_summary(results)
    
    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 