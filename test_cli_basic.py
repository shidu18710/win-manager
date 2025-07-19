#!/usr/bin/env python3
"""
Basic CLI functionality test
"""
import subprocess
import sys
import json

def test_cli_command(cmd, expected_exit=0):
    """Test a CLI command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Command: {cmd}")
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout[:200]}...")
        print(f"Error: {result.stderr[:200]}...")
        print("-" * 50)
        
        if result.returncode == expected_exit:
            print("✓ PASS")
        else:
            print("✗ FAIL")
        
        return result.returncode == expected_exit
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Run basic CLI tests"""
    print("=== Basic CLI Tests ===")
    
    tests = [
        "uv run win-manager --help",
        "uv run win-manager ls",
        "uv run win-manager --output json ls",
        "uv run win-manager --output yaml ls",
        "uv run win-manager layout list",
        "uv run win-manager --output json layout list",
        "uv run win-manager --dry-run grid --columns 3",
        "uv run win-manager tool status",
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test_cli_command(test):
            passed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())