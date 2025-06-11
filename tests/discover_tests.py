#!/usr/bin/env python3
"""
Test Discovery Script

Automatically discovers and lists all available tests in the organized test structure.
Useful for understanding the test organization and running specific test categories.
"""

import os
import sys
import importlib
import unittest
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def discover_test_modules(base_path: str = "tests") -> dict:
    """
    Discover all test modules in the organized test structure.
    
    Args:
        base_path: Base path to search for tests
        
    Returns:
        Dictionary organized by category containing test modules
    """
    test_structure = {
        "utils": [],
        "integrations": {
            "openai_integration": [],
            "telegram": [],
            "instagram": [],
            "adspower": []
        },
        "integration": [],
        "root": []
    }
    
    tests_dir = Path(base_path)
    
    # Discover utils tests
    utils_dir = tests_dir / "utils"
    if utils_dir.exists():
        for test_file in utils_dir.glob("test_*.py"):
            module_path = f"tests.utils.{test_file.stem}"
            test_structure["utils"].append({
                "module": module_path,
                "file": str(test_file),
                "name": test_file.stem.replace("test_", "").replace("_", " ").title()
            })
    
    # Discover integration tests
    integrations_dir = tests_dir / "integrations"
    if integrations_dir.exists():
        for service_dir in integrations_dir.iterdir():
            if service_dir.is_dir() and service_dir.name in test_structure["integrations"]:
                for test_file in service_dir.glob("test_*.py"):
                    module_path = f"tests.integrations.{service_dir.name}.{test_file.stem}"
                    test_structure["integrations"][service_dir.name].append({
                        "module": module_path,
                        "file": str(test_file),
                        "name": test_file.stem.replace("test_", "").replace("_", " ").title()
                    })
    
    # Discover end-to-end integration tests
    integration_dir = tests_dir / "integration"
    if integration_dir.exists():
        for test_file in integration_dir.glob("test_*.py"):
            module_path = f"tests.integration.{test_file.stem}"
            test_structure["integration"].append({
                "module": module_path,
                "file": str(test_file),
                "name": test_file.stem.replace("test_", "").replace("_", " ").title()
            })
    
    # Discover root level tests
    for test_file in tests_dir.glob("test_*.py"):
        module_path = f"tests.{test_file.stem}"
        test_structure["root"].append({
            "module": module_path,
            "file": str(test_file),
            "name": test_file.stem.replace("test_", "").replace("_", " ").title()
        })
    
    return test_structure


def count_tests_in_module(module_path: str) -> int:
    """
    Count the number of test cases in a module.
    
    Args:
        module_path: Full module path
        
    Returns:
        Number of test cases
    """
    try:
        module = importlib.import_module(module_path)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        return suite.countTestCases()
    except Exception:
        return 0


def print_test_structure(test_structure: dict):
    """
    Print the discovered test structure in a formatted way.
    
    Args:
        test_structure: Dictionary containing organized test modules
    """
    print("🔍 DISCOVERED TEST STRUCTURE")
    print("=" * 60)
    
    total_tests = 0
    total_modules = 0
    
    # Utils tests
    if test_structure["utils"]:
        print("\n📁 UTILS TESTS")
        print("-" * 30)
        for test_info in test_structure["utils"]:
            test_count = count_tests_in_module(test_info["module"])
            total_tests += test_count
            total_modules += 1
            print(f"   📝 {test_info['name']}: {test_count} tests")
            print(f"      Module: {test_info['module']}")
    
    # Integration tests
    print("\n📁 INTEGRATION TESTS")
    print("-" * 30)
    
    for service, tests in test_structure["integrations"].items():
        if tests:
            service_name = service.upper()
            print(f"\n   🔌 {service_name}")
            for test_info in tests:
                test_count = count_tests_in_module(test_info["module"])
                total_tests += test_count
                total_modules += 1
                print(f"      • {test_info['name']}: {test_count} tests")
                print(f"        Module: {test_info['module']}")
    
    # End-to-end integration tests
    if test_structure["integration"]:
        print(f"\n   🔗 END-TO-END INTEGRATION")
        for test_info in test_structure["integration"]:
            test_count = count_tests_in_module(test_info["module"])
            total_tests += test_count
            total_modules += 1
            print(f"      • {test_info['name']}: {test_count} tests")
            print(f"        Module: {test_info['module']}")
    
    # Root level tests
    if test_structure["root"]:
        print("\n📁 ROOT LEVEL TESTS")
        print("-" * 30)
        for test_info in test_structure["root"]:
            test_count = count_tests_in_module(test_info["module"])
            total_tests += test_count
            total_modules += 1
            print(f"   📄 {test_info['name']}: {test_count} tests")
            print(f"      Module: {test_info['module']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"📦 Total Modules: {total_modules}")
    print(f"🧪 Total Tests: {total_tests}")
    print(f"📁 Categories: {len([k for k, v in test_structure.items() if v and k != 'integrations']) + len([k for k, v in test_structure['integrations'].items() if v])}")


def print_run_commands():
    """Print available commands to run different test categories."""
    print("\n🚀 AVAILABLE RUN COMMANDS")
    print("=" * 60)
    print("📋 Main Test Suite:")
    print("   python tests/run_all_tests.py")
    print()
    print("🔌 AdsPower Integration Tests:")
    print("   python tests/integrations/adspower/run_adspower_tests.py")
    print()
    print("🧪 Individual Test Modules:")
    print("   python -m pytest tests/utils/test_logger.py")
    print("   python -m pytest tests/integrations/openai_integration/test_comment_gen.py")
    print("   python -m pytest tests/integrations/telegram/test_notifier.py")
    print("   python -m pytest tests/integrations/instagram/test_poster.py")
    print("   python -m pytest tests/integration/test_integration.py")
    print()
    print("📁 Category-based Testing:")
    print("   python -m pytest tests/utils/")
    print("   python -m pytest tests/integrations/openai_integration/")
    print("   python -m pytest tests/integrations/telegram/")
    print("   python -m pytest tests/integrations/instagram/")
    print("   python -m pytest tests/integrations/adspower/")
    print("   python -m pytest tests/integration/")


def main():
    """Main discovery function."""
    print("🔍 Instagram Automation Project - Test Discovery")
    print("=" * 60)
    
    # Discover tests
    test_structure = discover_test_modules()
    
    # Print structure
    print_test_structure(test_structure)
    
    # Print run commands
    print_run_commands()
    
    print("\n✅ Test discovery completed!")


if __name__ == "__main__":
    main() 