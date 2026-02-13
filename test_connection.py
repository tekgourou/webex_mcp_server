#!/usr/bin/env python3
"""
Test script to verify Webex connection and MCP server setup
"""

import os
import sys

def test_imports():
    """Test that required packages are installed."""
    print("Testing package imports...")
    try:
        import mcp
        print("  ✅ mcp package installed")
    except ImportError:
        print("  ❌ mcp package not found - run: pip install mcp")
        return False
    
    try:
        from webexteamssdk import WebexTeamsAPI
        print("  ✅ webexteamssdk package installed")
    except ImportError:
        print("  ❌ webexteamssdk not found - run: pip install webexteamssdk")
        return False
    
    return True


def test_token():
    """Test that Webex token is configured."""
    print("\nTesting Webex token...")
    token = os.getenv("WEBEX_ACCESS_TOKEN")
    
    if not token:
        print("  ❌ WEBEX_ACCESS_TOKEN environment variable not set")
        print("  Set it with: export WEBEX_ACCESS_TOKEN='your_token_here'")
        return False
    
    print(f"  ✅ Token found (length: {len(token)} characters)")
    return True


def test_connection():
    """Test connection to Webex API."""
    print("\nTesting Webex API connection...")
    
    try:
        from webexteamssdk import WebexTeamsAPI
        token = os.getenv("WEBEX_ACCESS_TOKEN")
        
        api = WebexTeamsAPI(access_token=token)
        me = api.people.me()
        
        print(f"  ✅ Connected successfully!")
        print(f"  Bot/User Name: {me.displayName}")
        print(f"  Email: {me.emails[0]}")
        print(f"  ID: {me.id}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Connection failed: {str(e)}")
        return False


def test_spaces():
    """Test listing Webex spaces."""
    print("\nTesting space listing...")
    
    try:
        from webexteamssdk import WebexTeamsAPI
        token = os.getenv("WEBEX_ACCESS_TOKEN")
        
        api = WebexTeamsAPI(access_token=token)
        rooms = list(api.rooms.list(max=5))
        
        print(f"  ✅ Found {len(rooms)} spaces")
        
        if rooms:
            print("\n  First few spaces:")
            for i, room in enumerate(rooms[:3], 1):
                print(f"    {i}. {room.title} ({room.type})")
        else:
            print("  ℹ️  No spaces found - bot may need to be added to spaces")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to list spaces: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Webex MCP Server - Connection Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Package Installation", test_imports()))
    
    if results[-1][1]:  # Only continue if packages are installed
        results.append(("Token Configuration", test_token()))
        
        if results[-1][1]:  # Only continue if token is set
            results.append(("API Connection", test_connection()))
            results.append(("Space Listing", test_spaces()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Your Webex MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Configure Claude Desktop (see README.md)")
        print("2. Restart Claude Desktop")
        print("3. Ask Claude: 'Can you list my Webex spaces?'")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("See README.md for troubleshooting help.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
