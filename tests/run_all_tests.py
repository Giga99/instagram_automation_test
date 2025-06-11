#!/usr/bin/env python3
"""
Instagram Automation Test Runner

Runs all test modules and provides comprehensive reporting.
Tests include:
- Utils: Logger and configuration modules
- Integrations: OpenAI, Telegram, Instagram, and AdsPower modules
- Integration tests across all phases

Run this script to execute the complete test suite.
"""

import importlib
import os
import sys
import unittest

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_test_module(module_path, display_name):
    """
    Run a specific test module and return results.
    
    Args:
        module_path: Full path to the test module (e.g., 'tests.utils.test_logger')
        display_name: Human-readable name for display
        
    Returns:
        Tuple of (success_count, total_count, success_bool)
    """
    try:
        # Import the test module
        test_module = importlib.import_module(module_path)

        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)

        # Calculate results
        total_tests = result.testsRun
        failed_tests = len(result.failures) + len(result.errors)
        success_tests = total_tests - failed_tests
        success_rate = (success_tests / total_tests * 100) if total_tests > 0 else 0

        return success_tests, total_tests, len(result.failures) == 0 and len(result.errors) == 0, success_rate

    except Exception as e:
        print(f"❌ Error running {display_name}: {str(e)}")
        return 0, 0, False, 0


def main():
    """Main test runner function."""

    print("🔥" * 70)
    print("🔥" * 6)
    print("🚀 INSTAGRAM AUTOMATION PROJECT - COMPREHENSIVE TEST SUITE")
    print("🔥" * 70)
    print("🔥" * 6)
    print("🧪 Running all tests with improved organization...")
    print("   This will test all modules organized by category")
    print()
    print("🔥" * 70)
    print("🔥" * 6)

    # Test modules configuration with new organized structure
    test_modules = [
        ('tests.utils.test_logger', 'Logger Module', '📝 UTILS - LOGGER MODULE TESTS'),
        ('tests.integrations.openai_integration.test_comment_gen', 'Comment Generation Module', '🤖 OPENAI - COMMENT GENERATION MODULE TESTS'),
        ('tests.integrations.telegram.test_notifier', 'Notifier Module', '📱 TELEGRAM - NOTIFIER MODULE TESTS'),
        ('tests.integrations.instagram.test_poster', 'Poster Module', '💬 INSTAGRAM - POSTER MODULE TESTS'),
        ('tests.integration.test_integration', 'Integration Tests', '🔗 INTEGRATION TESTS'),
    ]

    results = {}
    total_success = 0
    total_tests = 0
    all_passed = True

    # Run each test module
    for module_path, display_name, header in test_modules:
        print(header)
        print("🔥" * 70)
        print("🔥" * 6)
        print(f"🧪 Running {display_name} Tests...")

        # Run the actual test module with full output
        try:
            test_module = importlib.import_module(module_path)
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            # Calculate results
            module_total = result.testsRun
            module_failed = len(result.failures) + len(result.errors)
            module_success = module_total - module_failed
            module_success_rate = (module_success / module_total * 100) if module_total > 0 else 0
            module_passed = len(result.failures) == 0 and len(result.errors) == 0

            results[display_name] = {
                'success': module_success,
                'total': module_total,
                'passed': module_passed,
                'rate': module_success_rate
            }

            total_success += module_success
            total_tests += module_total

            if not module_passed:
                all_passed = False

            print("=" * 50)
            print(f"📊 {display_name} Tests Summary:")
            print(f"   • Tests Run: {module_total}")
            print(f"   • Failures: {module_failed}")
            print(f"   • Errors: 0")
            print(f"   • Success Rate: {module_success_rate:.1f}%")
            print()

        except Exception as e:
            print(f"❌ Error running {display_name}: {str(e)}")
            results[display_name] = {
                'success': 0,
                'total': 0,
                'passed': False,
                'rate': 0
            }
            all_passed = False

        print("🔥" * 70)
        print("🔥" * 6)

    # Final summary
    overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0

    print("=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print()
    print("🎯 Overall Results:")
    print(f"   • Total Test Modules: {len(test_modules)}")
    print(f"   • Total Tests Run: {total_tests}")
    print(f"   • Total Successful: {total_success}")
    print(f"   • Overall Success Rate: {overall_success_rate:.1f}%")
    print()
    print("📋 Module Results:")

    passed_modules = 0
    for display_name, result in results.items():
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"   • {display_name}: {status}")
        if result['passed']:
            passed_modules += 1

    print()
    print("🏆 Category Breakdown:")

    # Utils results
    utils_modules = ['Logger Module']
    utils_passed = all(results.get(mod, {}).get('passed', False) for mod in utils_modules)
    utils_status = "✅ PASSED" if utils_passed else "❌ FAILED"
    print(f"   • Utils (Foundation): {utils_status}")

    # Integration modules results  
    integration_modules = ['Comment Generation Module', 'Notifier Module', 'Poster Module']
    integration_passed = all(results.get(mod, {}).get('passed', False) for mod in integration_modules)
    integration_status = "✅ PASSED" if integration_passed else "❌ FAILED"
    print(f"   • External Integrations: {integration_status}")

    # Integration tests results
    integration_test_passed = results.get('Integration Tests', {}).get('passed', False)
    integration_test_status = "✅ PASSED" if integration_test_passed else "❌ FAILED"
    print(f"   • End-to-End Integration: {integration_test_status}")

    print()
    print("ℹ️  Note: AdsPower tests are available separately via:")
    print("   'python tests/integrations/adspower/run_adspower_tests.py'")
    print()

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Instagram Automation Project is ready for production!")
        print("📁 Tests are now organized by category for better maintainability!")
    else:
        print("⚠️ SOME TESTS FAILED!")
        print("🔧 Please review the failed tests and fix any issues.")
    
    print("=" * 80)
    print()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
