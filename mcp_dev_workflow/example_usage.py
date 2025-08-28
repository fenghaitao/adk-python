#!/usr/bin/env python3
"""
Example usage of the git remote URL functions
"""

from get_git_remote import get_git_remotes
from get_git_remote import get_origin_url


def main():
    """Demonstrate different ways to use the git remote functions."""

    print("=== Git Remote URL Examples ===\n")

    # Example 1: Get origin URL (most common use case)
    print("1. Getting origin remote URL:")
    try:
        origin_url = get_origin_url()
        if origin_url:
            print(f"   Origin URL: {origin_url}")
        else:
            print("   No origin remote found")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Example 2: Get all remotes
    print("2. Getting all remotes:")
    try:
        remotes = get_git_remotes()
        if remotes:
            for remote_name, remote_info in remotes.items():
                print(f"   Remote: {remote_name}")
                for remote_type, url in remote_info.items():
                    print(f"     {remote_type}: {url}")
        else:
            print("   No remotes configured")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Example 3: Check if specific remote exists
    print("3. Checking for specific remote:")
    try:
        remotes = get_git_remotes()
        remote_name = "origin"
        if remote_name in remotes:
            print(f"   Remote '{remote_name}' exists:")
            for remote_type, url in remotes[remote_name].items():
                print(f"     {remote_type}: {url}")
        else:
            print(f"   Remote '{remote_name}' not found")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
