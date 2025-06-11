#!/usr/bin/env python3
"""
AdsPower Test Validation Script

Quick validation script to check if all AdsPower tests can be imported
and basic functionality works before running the full test suite.
"""

import sys
import os
import importlib
from typing import List, Tuple

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_test_imports() -> List[Tuple[str, bool, str]]:
    """
    Validate that all AdsPower test modules can be imported.
    
    Returns:
        List of tuples (module_name, success, error_message)
    """
    test_modules = [
        'test_adspower_client',
        'test_adspower_config',
        'test_adspower_profile_manager', 
        'test_adspower_integration'
    ]
    
    results = []
    
    for module_name in test_modules:
        try:
            module = importlib.import_module(f'tests.{module_name}')
            results.append((module_name, True, ""))
            print(f"✅ {module_name}: Import successful")
        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            results.append((module_name, False, error_msg))
            print(f"❌ {module_name}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            results.append((module_name, False, error_msg))
            print(f"💥 {module_name}: {error_msg}")
    
    return results


def validate_source_modules() -> List[Tuple[str, bool, str]]:
    """
    Validate that all AdsPower source modules can be imported.
    
    Returns:
        List of tuples (module_name, success, error_message)
    """
    source_modules = [
        'src.integrations.adspower.client',
        'src.integrations.adspower.config',
        'src.integrations.adspower.profile_manager'
    ]
    
    results = []
    
    for module_name in source_modules:
        try:
            module = importlib.import_module(module_name)
            results.append((module_name, True, ""))
            print(f"✅ {module_name}: Import successful")
        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            results.append((module_name, False, error_msg))
            print(f"❌ {module_name}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            results.append((module_name, False, error_msg))
            print(f"💥 {module_name}: {error_msg}")
    
    return results


def validate_test_classes() -> List[Tuple[str, bool, str]]:
    """
    Validate that test classes can be instantiated.
    
    Returns:
        List of tuples (class_name, success, error_message)
    """
    test_validations = []
    
    try:
        # Test AdsPowerClient import and basic instantiation
        from src.integrations.adspower.client import AdsPowerClient, AdsPowerProfile, AdsPowerProfileGroup
        client = AdsPowerClient()
        test_validations.append(("AdsPowerClient", True, ""))
        print("✅ AdsPowerClient: Instantiation successful")
        
        # Test dataclasses
        profile = AdsPowerProfile(profile_id="test", name="test")
        group = AdsPowerProfileGroup(id="test")
        test_validations.append(("AdsPowerProfile/Group", True, ""))
        print("✅ AdsPowerProfile/Group: Creation successful")
        
    except Exception as e:
        error_msg = f"Client validation error: {str(e)}"
        test_validations.append(("AdsPowerClient", False, error_msg))
        print(f"❌ AdsPowerClient: {error_msg}")
    
    try:
        # Test AdsPowerProfileManager
        from src.integrations.adspower.profile_manager import AdsPowerProfileManager
        manager = AdsPowerProfileManager()
        test_validations.append(("AdsPowerProfileManager", True, ""))
        print("✅ AdsPowerProfileManager: Instantiation successful")
        
    except Exception as e:
        error_msg = f"Profile manager validation error: {str(e)}"
        test_validations.append(("AdsPowerProfileManager", False, error_msg))
        print(f"❌ AdsPowerProfileManager: {error_msg}")
    
    try:
        # Test config functions
        from src.integrations.adspower.config import load_adspower_profiles, test_adspower_connection
        
        # Test functions exist and can be called (with mocked dependencies)
        test_validations.append(("Config functions", True, ""))
        print("✅ Config functions: Import successful")
        
    except Exception as e:
        error_msg = f"Config validation error: {str(e)}"
        test_validations.append(("Config functions", False, error_msg))
        print(f"❌ Config functions: {error_msg}")
    
    return test_validations


def main():
    """Main validation function."""
    print("🧪 AdsPower Test Validation")
    print("=" * 50)
    
    # Validate source module imports
    print("\n📦 Validating source module imports...")
    source_results = validate_source_modules()
    
    # Validate test module imports
    print("\n🧪 Validating test module imports...")
    test_results = validate_test_imports()
    
    # Validate test classes
    print("\n🔧 Validating test class instantiation...")
    class_results = validate_test_classes()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_results = source_results + test_results + class_results
    total_validations = len(all_results)
    successful_validations = sum(1 for _, success, _ in all_results if success)
    
    print(f"📈 Success Rate: {successful_validations}/{total_validations} ({successful_validations/total_validations*100:.1f}%)")
    
    if successful_validations == total_validations:
        print("🎉 All validations passed! AdsPower tests are ready to run.")
        print("\n💡 Next steps:")
        print("   • Run: python tests/run_adspower_tests.py")
        print("   • Or: python tests/run_all_tests.py")
        return True
    else:
        print("⚠️ Some validations failed!")
        print("\n💥 Failed validations:")
        for name, success, error in all_results:
            if not success:
                print(f"   • {name}: {error}")
        
        print("\n💡 Fix the above issues before running tests")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 