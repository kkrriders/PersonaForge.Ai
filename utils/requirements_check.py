"""
Requirements checker - Validates that all required packages are installed
"""

import sys
import importlib
import subprocess
from typing import List, Dict, Any

class RequirementsChecker:
    def __init__(self):
        self.required_packages = {
            'aiosqlite': 'aiosqlite',
            'requests': 'requests', 
            'schedule': 'schedule',
            'PIL': 'pillow',
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'pydantic': 'pydantic',
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn',
            'dotenv': 'python-dotenv',
            'cryptography': 'cryptography',
            'jinja2': 'jinja2'
        }
        
        self.optional_packages = {
            'pyperclip': 'pyperclip'
        }
    
    def check_package(self, import_name: str) -> bool:
        """Check if a package can be imported"""
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
    
    def check_all_requirements(self) -> Dict[str, Any]:
        """Check all required packages"""
        results = {
            'missing_required': [],
            'missing_optional': [],
            'available': [],
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        # Check required packages
        for import_name, pip_name in self.required_packages.items():
            if self.check_package(import_name):
                results['available'].append(pip_name)
            else:
                results['missing_required'].append(pip_name)
        
        # Check optional packages
        for import_name, pip_name in self.optional_packages.items():
            if not self.check_package(import_name):
                results['missing_optional'].append(pip_name)
        
        return results
    
    def get_install_commands(self, missing_packages: List[str]) -> List[str]:
        """Get pip install commands for missing packages"""
        if not missing_packages:
            return []
        
        return [f"pip install {' '.join(missing_packages)}"]
    
    def print_requirements_report(self):
        """Print a detailed requirements report"""
        print("🔍 REQUIREMENTS CHECK")
        print("=" * 50)
        
        results = self.check_all_requirements()
        
        print(f"Python Version: {results['python_version']}")
        print(f"Available Packages: {len(results['available'])}")
        print(f"Missing Required: {len(results['missing_required'])}")
        print(f"Missing Optional: {len(results['missing_optional'])}")
        
        if results['missing_required']:
            print("\n❌ MISSING REQUIRED PACKAGES:")
            for package in results['missing_required']:
                print(f"  • {package}")
            
            print("\n📦 TO INSTALL MISSING PACKAGES:")
            commands = self.get_install_commands(results['missing_required'])
            for cmd in commands:
                print(f"  {cmd}")
        
        if results['missing_optional']:
            print("\n⚠️  MISSING OPTIONAL PACKAGES:")
            for package in results['missing_optional']:
                print(f"  • {package}")
            
            print("\n📦 TO INSTALL OPTIONAL PACKAGES:")
            commands = self.get_install_commands(results['missing_optional'])
            for cmd in commands:
                print(f"  {cmd}")
        
        if not results['missing_required']:
            print("\n✅ All required packages are installed!")
        
        return len(results['missing_required']) == 0

def check_requirements():
    """Standalone function to check requirements"""
    checker = RequirementsChecker()
    return checker.print_requirements_report()

if __name__ == "__main__":
    check_requirements()