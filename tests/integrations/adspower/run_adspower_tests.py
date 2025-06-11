#!/usr/bin/env python3
"""
AdsPower Test Runner

Comprehensive test runner for all AdsPower integration tests.
Provides detailed reporting, coverage analysis, and performance metrics.
"""

import unittest
import sys
import os
import time
from io import StringIO
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


class AdsPowerTestResult(unittest.TextTestResult):
    """Custom test result class with enhanced reporting."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_times = {}
        self.start_time = None
        
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
        
    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time:
            duration = time.time() - self.start_time
            self.test_times[str(test)] = duration


class AdsPowerTestRunner:
    """Enhanced test runner for AdsPower tests."""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.test_modules = [
            'test_adspower_client',
            'test_adspower_config', 
            'test_adspower_profile_manager',
            'test_adspower_integration'
        ]
    
    def discover_tests(self) -> unittest.TestSuite:
        """Discover all AdsPower tests."""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        for module_name in self.test_modules:
            try:
                module = __import__(f'tests.integrations.adspower.{module_name}', fromlist=[module_name])
                module_suite = loader.loadTestsFromModule(module)
                suite.addTest(module_suite)
                print(f"✅ Loaded tests from {module_name}")
            except ImportError as e:
                print(f"⚠️ Could not load {module_name}: {str(e)}")
            except Exception as e:
                print(f"❌ Error loading {module_name}: {str(e)}")
        
        return suite
    
    def run_tests(self) -> Dict[str, Any]:
        """Run all AdsPower tests and return results."""
        print("🧪 AdsPower Test Suite")
        print("=" * 60)
        
        # Discover tests
        suite = self.discover_tests()
        test_count = suite.countTestCases()
        print(f"📊 Found {test_count} test cases")
        
        if test_count == 0:
            print("❌ No tests found!")
            return {"success": False, "error": "No tests found"}
        
        print("\n🚀 Running tests...")
        print("-" * 60)
        
        # Run tests
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=self.verbosity,
            resultclass=AdsPowerTestResult
        )
        
        start_time = time.time()
        result = runner.run(suite)
        total_time = time.time() - start_time
        
        # Print results
        print(stream.getvalue())
        
        # Generate summary
        summary = self._generate_summary(result, total_time)
        self._print_summary(summary)
        
        return summary
    
    def _generate_summary(self, result: AdsPowerTestResult, total_time: float) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        passed = total_tests - failures - errors - skipped
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "success": failures == 0 and errors == 0,
            "total_tests": total_tests,
            "passed": passed,
            "failures": failures,
            "errors": errors,
            "skipped": skipped,
            "success_rate": success_rate,
            "total_time": total_time,
            "average_time": total_time / total_tests if total_tests > 0 else 0,
            "test_times": getattr(result, 'test_times', {}),
            "failure_details": result.failures,
            "error_details": result.errors
        }
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print formatted test summary."""
        print("\n" + "=" * 60)
        print("📊 ADSPOWER TEST SUMMARY")
        print("=" * 60)
        
        # Overall results
        status_icon = "✅" if summary["success"] else "❌"
        print(f"{status_icon} Overall Status: {'PASS' if summary['success'] else 'FAIL'}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Total Time: {summary['total_time']:.2f}s")
        print(f"⚡ Average Time: {summary['average_time']:.3f}s per test")
        
        print(f"\n📋 Test Breakdown:")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failures']}")
        print(f"   💥 Errors: {summary['errors']}")
        print(f"   ⏭️ Skipped: {summary['skipped']}")
        print(f"   📊 Total: {summary['total_tests']}")
        
        # Performance analysis
        if summary["test_times"]:
            self._print_performance_analysis(summary["test_times"])
        
        # Failure details
        if summary["failures"] or summary["errors"]:
            self._print_failure_details(summary)
    
    def _print_performance_analysis(self, test_times: Dict[str, float]):
        """Print performance analysis of tests."""
        print(f"\n⚡ Performance Analysis:")
        
        # Sort tests by duration
        sorted_tests = sorted(test_times.items(), key=lambda x: x[1], reverse=True)
        
        # Show slowest tests
        print(f"   🐌 Slowest Tests:")
        for test_name, duration in sorted_tests[:5]:
            test_short_name = test_name.split('.')[-1] if '.' in test_name else test_name
            print(f"      • {test_short_name}: {duration:.3f}s")
        
        # Show fastest tests
        print(f"   🚀 Fastest Tests:")
        for test_name, duration in sorted_tests[-5:]:
            test_short_name = test_name.split('.')[-1] if '.' in test_name else test_name
            print(f"      • {test_short_name}: {duration:.3f}s")
    
    def _print_failure_details(self, summary: Dict[str, Any]):
        """Print detailed failure information."""
        print(f"\n💥 Failure Details:")
        
        if summary["failures"]:
            print(f"   ❌ Test Failures:")
            for i, (test, traceback) in enumerate(summary["failure_details"], 1):
                test_name = str(test).split('.')[-1] if '.' in str(test) else str(test)
                print(f"      {i}. {test_name}")
                # Print first line of traceback for quick reference
                first_line = traceback.split('\n')[0] if traceback else "No details"
                print(f"         {first_line}")
        
        if summary["errors"]:
            print(f"   💥 Test Errors:")
            for i, (test, traceback) in enumerate(summary["error_details"], 1):
                test_name = str(test).split('.')[-1] if '.' in str(test) else str(test)
                print(f"      {i}. {test_name}")
                # Print first line of traceback for quick reference
                first_line = traceback.split('\n')[0] if traceback else "No details"
                print(f"         {first_line}")


def run_specific_test_module(module_name: str):
    """Run tests from a specific module."""
    print(f"🧪 Running tests from {module_name}")
    print("=" * 50)
    
    try:
        loader = unittest.TestLoader()
        module = __import__(f'tests.{module_name}', fromlist=[module_name])
        suite = loader.loadTestsFromModule(module)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Could not import {module_name}: {str(e)}")
        return False
    except Exception as e:
        print(f"💥 Error running {module_name}: {str(e)}")
        return False


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AdsPower Test Runner")
    parser.add_argument(
        '--module', '-m',
        help='Run tests from specific module (e.g., test_adspower_client)',
        choices=['test_adspower_client', 'test_adspower_config', 
                'test_adspower_profile_manager', 'test_adspower_integration']
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output (minimal)'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    # Run specific module or all tests
    if args.module:
        success = run_specific_test_module(args.module)
        sys.exit(0 if success else 1)
    else:
        runner = AdsPowerTestRunner(verbosity=verbosity)
        summary = runner.run_tests()
        
        # Exit with appropriate code
        sys.exit(0 if summary["success"] else 1)


if __name__ == '__main__':
    main() 