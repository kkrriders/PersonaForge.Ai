

import sys
import os
import subprocess
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("🚀" * 50)
    print("         PersonaForge.AI - LinkedIn Automation")
    print("         Local-First, Privacy-Focused Solution")
    print("🚀" * 50)
    print()

def check_python_version():
    """Check if Python version is adequate"""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"❌ Python {min_version[0]}.{min_version[1]}+ required. Current: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python version: {current_version[0]}.{current_version[1]}")
    return True

def check_ollama():
    """Check if Ollama is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is available")
            
            # Check if llama3:8b is available
            if 'llama3:8b' in result.stdout:
                print("✅ llama3:8b model is available")
            else:
                print("⚠️  llama3:8b model not found. Install with: ollama pull llama3:8b")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found. Please install from https://ollama.ai")
        return False

def check_dependencies():
    """Check required Python packages"""
    try:
        from utils.requirements_check import RequirementsChecker
        checker = RequirementsChecker()
        results = checker.check_all_requirements()
        
        if results['missing_required']:
            print("❌ Missing required packages:")
            for package in results['missing_required']:
                print(f"   • {package}")
            print("\n📦 Install with: pip install -r requirements.txt")
            return False
        else:
            print(f"✅ All {len(results['available'])} required packages installed")
            
            if results['missing_optional']:
                print("⚠️  Optional packages missing:")
                for package in results['missing_optional']:
                    print(f"   • {package}")
            
            return True
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'data/images',
        'data/posts', 
        'data/schedules',
        'data/analytics',
        'data/backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📝 Creating .env file from template...")
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created. Please customize your settings.")
        else:
            print("⚠️  .env.example not found. Creating basic .env file...")
            basic_env = """# PersonaForge.AI Configuration
OLLAMA_HOST=http://0.0.0.0:11434
OLLAMA_MODEL=llama3:8b
DATABASE_PATH=data/linkedin_tool.db
LOCAL_STORAGE_ONLY=true
ENCRYPT_DATA=true
"""
            with open('.env', 'w') as f:
                f.write(basic_env)
            print("✅ Basic .env file created")
    else:
        print("✅ .env file exists")

def run_system_check():
    """Run comprehensive system check"""
    print("🔍 SYSTEM CHECK")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Ollama", check_ollama)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("✅ All checks passed! Setting up environment...")
        setup_directories()
        create_env_file()
        return True
    else:
        print("❌ Some checks failed. Please resolve issues before continuing.")
        return False

def launch_application():
    """Launch the main application"""
    try:
        print("\n🚀 Launching PersonaForge.AI...")
        print("=" * 40)
        
        # Import and run main application
        import main
        import asyncio
        
        asyncio.run(main.main())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        print("Please check logs and try again.")

def main():
    """Main startup function"""
    print_banner()
    
    if run_system_check():
        launch_application()
    else:
        print("\n💡 NEXT STEPS:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Install Ollama: https://ollama.ai")
        print("3. Pull model: ollama pull llama3.8b")
        print("4. Run again: python startup.py")
        sys.exit(1)

if __name__ == "__main__":
    main()