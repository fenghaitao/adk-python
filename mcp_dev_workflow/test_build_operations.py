#!/usr/bin/env python3
"""
Test script to verify build operations in MCP build server
"""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


async def test_build_operations():
    """Test specific build operations that were timing out."""
    print("Testing build operations that were timing out...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")

        # Create a simple Python project
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()

        src_dir = project_dir / "src"
        src_dir.mkdir()

        tests_dir = project_dir / "tests"
        tests_dir.mkdir()

        # Create a simple calculator module
        calculator_py = src_dir / "calculator.py"
        calculator_py.write_text(
            """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
        )

        # Create a test file
        test_file = tests_dir / "test_calculator.py"
        test_file.write_text(
            """
import sys
sys.path.insert(0, 'src')
from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2
"""
        )

        # Create a requirements file
        requirements_txt = project_dir / "requirements.txt"
        requirements_txt.write_text("pytest>=7.0.0")

        # Test install_dependencies
        print("\n1. Testing install_dependencies...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_txt)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print("   ✅ install_dependencies works")
            else:
                print(f"   ❌ install_dependencies failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("   ❌ install_dependencies timed out")
        except Exception as e:
            print(f"   ❌ install_dependencies error: {e}")

        # Test run_tests
        print("\n2. Testing run_tests...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tests_dir), "-v"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print("   ✅ run_tests works")
            else:
                print(f"   ❌ run_tests failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("   ❌ run_tests timed out")
        except Exception as e:
            print(f"   ❌ run_tests error: {e}")

        # Test lint_code (black)
        print("\n3. Testing lint_code (black)...")
        try:
            result = subprocess.run(
                ["black", "--check", str(project_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print("   ✅ black linting works")
            else:
                print(f"   ⚠️  black linting found issues or failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("   ❌ black linting timed out")
        except Exception as e:
            print(f"   ❌ black linting error: {e}")

        # Test lint_code (isort)
        print("\n4. Testing lint_code (isort)...")
        try:
            result = subprocess.run(
                ["isort", "--check-only", str(project_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print("   ✅ isort works")
            else:
                print(f"   ⚠️  isort found issues or failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("   ❌ isort timed out")
        except Exception as e:
            print(f"   ❌ isort error: {e}")

        # Test build_package
        print("\n5. Testing build_package...")
        try:
            # Create a basic pyproject.toml for building
            pyproject_toml = project_dir / "pyproject.toml"
            pyproject_toml.write_text(
                """
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-calculator"
version = "0.1.0"
description = "A simple calculator for testing"
authors = [{name = "Test User", email = "test@example.com"}]
dependencies = []
"""
            )

            result = subprocess.run(
                [sys.executable, "-m", "build"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print("   ✅ build_package works")
            else:
                print(f"   ❌ build_package failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("   ❌ build_package timed out")
        except Exception as e:
            print(f"   ❌ build_package error: {e}")


def main():
    """Main function."""
    print("Testing build operations that were timing out in MCP workflow...\n")
    asyncio.run(test_build_operations())
    print("\nTest completed.")


if __name__ == "__main__":
    main()
