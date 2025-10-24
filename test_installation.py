#!/usr/bin/env python3
"""
Test script to verify the Video Subtitler installation
Run this after setup to ensure everything is configured correctly
"""

import os
import sys
import subprocess
import importlib


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)


def print_status(check_name, status, message=""):
    """Print status of a check"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check_name}", end="")
    if message:
        print(f": {message}")
    else:
        print()


def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    print_status("Python Version", is_valid, f"{version.major}.{version.minor}.{version.micro}")
    return is_valid


def check_required_packages():
    """Check if required Python packages are installed"""
    print_header("Python Packages Check")
    
    packages = [
        'flask',
        'celery',
        'redis',
        'google.cloud.speech',
        'google.cloud.translate',
        'yt_dlp',
        'dotenv',
    ]
    
    all_installed = True
    for package in packages:
        try:
            importlib.import_module(package)
            print_status(package, True, "installed")
        except ImportError:
            print_status(package, False, "NOT FOUND")
            all_installed = False
    
    return all_installed


def check_system_commands():
    """Check if required system commands are available"""
    print_header("System Commands Check")
    
    commands = ['ffmpeg', 'redis-cli']
    all_available = True
    
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version' if cmd == 'ffmpeg' else 'ping'],
                capture_output=True,
                timeout=5
            )
            if cmd == 'redis-cli':
                # For redis-cli, check if it can ping the server
                is_available = b'PONG' in result.stdout
                msg = "running" if is_available else "not running"
            else:
                is_available = result.returncode == 0
                msg = "installed"
            
            print_status(cmd, is_available, msg)
            all_available = all_available and is_available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_status(cmd, False, "NOT FOUND")
            all_available = False
    
    return all_available


def check_environment_files():
    """Check if environment files exist"""
    print_header("Environment Files Check")
    
    files = {
        '.env': 'Environment configuration',
        'google-credentials.json': 'Google Cloud credentials',
    }
    
    all_exist = True
    for file, description in files.items():
        exists = os.path.exists(file)
        print_status(f"{file} ({description})", exists)
        all_exist = all_exist and exists
    
    return all_exist


def check_directories():
    """Check if required directories exist"""
    print_header("Directories Check")
    
    dirs = ['temp_files', 'output_files', 'static', 'templates']
    
    all_exist = True
    for directory in dirs:
        exists = os.path.exists(directory) and os.path.isdir(directory)
        print_status(directory, exists)
        all_exist = all_exist and exists
    
    return all_exist


def check_google_cloud_credentials():
    """Check if Google Cloud credentials are valid"""
    print_header("Google Cloud Configuration Check")
    
    if not os.path.exists('google-credentials.json'):
        print_status("Google Cloud Credentials File", False, "File not found")
        return False
    
    try:
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            'google-credentials.json'
        )
        print_status("Google Cloud Credentials", True, "Valid JSON format")
        print_status("Project ID", True, credentials.project_id)
        return True
    except Exception as e:
        print_status("Google Cloud Credentials", False, str(e))
        return False


def check_api_endpoints():
    """Check if Flask app can be imported"""
    print_header("Application Check")
    
    try:
        import app
        print_status("Flask App Import", True)
        return True
    except Exception as e:
        print_status("Flask App Import", False, str(e))
        return False


def print_summary(results):
    """Print summary of all checks"""
    print_header("Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if all(results.values()):
        print("\n✅ All checks passed! Your installation is ready.")
        print("\nTo start the application, run:")
        print("  ./start.sh")
        print("\nOr manually:")
        print("  source venv/bin/activate")
        print("  python app.py")
        return True
    else:
        print("\n❌ Some checks failed. Please review the output above.")
        print("\nFailed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  - {check}")
        
        print("\nRefer to README.md or QUICKSTART.md for setup instructions.")
        return False


def main():
    """Run all checks"""
    print("\n🎬 AI Video Subtitler - Installation Test")
    
    results = {
        "Python Version": check_python_version(),
        "Python Packages": check_required_packages(),
        "System Commands": check_system_commands(),
        "Environment Files": check_environment_files(),
        "Directories": check_directories(),
        "Google Cloud Config": check_google_cloud_credentials(),
        "Application Import": check_api_endpoints(),
    }
    
    success = print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
