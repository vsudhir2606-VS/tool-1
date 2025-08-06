
#!/usr/bin/env python3
"""
Installation script for Desktop Auto Highlighter
This script helps install the required dependencies and setup the application.
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        subprocess.run(["tesseract", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("🔍 Desktop Auto Highlighter - Installation Script")
    print("=" * 50)
    
    # Required packages
    packages = [
        "opencv-python",
        "pytesseract",
        "Pillow",
        "pyautogui",
        "numpy"
    ]
    
    print("Installing Python packages...")
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("\n✅ All Python packages installed successfully!")
    
    # Check Tesseract OCR
    print("\nChecking Tesseract OCR...")
    if check_tesseract():
        print("✅ Tesseract OCR is installed")
    else:
        print("❌ Tesseract OCR not found")
        print("\nPlease install Tesseract OCR:")
        
        system = platform.system().lower()
        if system == "windows":
            print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("Or use: winget install UB-Mannheim.TesseractOCR")
        elif system == "darwin":  # macOS
            print("macOS: brew install tesseract")
        elif system == "linux":
            print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("CentOS/RHEL: sudo yum install tesseract")
        else:
            print("Visit: https://github.com/tesseract-ocr/tesseract")
    
    print("\n" + "=" * 50)
    print("Installation complete!")
    print("Run the application with: python desktop_highlighter.py")

if __name__ == "__main__":
    main()
