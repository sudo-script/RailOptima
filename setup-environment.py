#!/usr/bin/env python3
"""
RailOptima Environment Setup Script
This script sets up the development environment for RailOptima on any machine.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """Print a formatted header"""
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  {text}", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

def print_step(step, text):
    """Print a formatted step"""
    print_colored(f"\n[{step}] {text}", Colors.YELLOW)

def check_command(command):
    """Check if a command is available in the system"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print_colored(f"  Running: {command}", Colors.BLUE)
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        print_colored(f"  ✅ {description} completed successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"  ❌ {description} failed", Colors.RED)
        print_colored(f"  Error: {e.stderr}", Colors.RED)
        return False

def setup_python_environment():
    """Set up Python virtual environment and dependencies"""
    print_step("1", "Setting up Python Environment")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print_colored("❌ Python 3.8 or higher is required", Colors.RED)
        return False
    
    print_colored(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected", Colors.GREEN)
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print_colored("  ✅ Virtual environment already exists", Colors.GREEN)
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:
        activate_script = "venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    # Upgrade pip
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install Python dependencies
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def setup_node_environment():
    """Set up Node.js environment and dependencies"""
    print_step("2", "Setting up Node.js Environment")
    
    # Check if Node.js is installed
    if not check_command("node"):
        print_colored("❌ Node.js is not installed. Please install Node.js from https://nodejs.org/", Colors.RED)
        return False
    
    # Check Node.js version
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print_colored(f"✅ Node.js {node_version} detected", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ Could not determine Node.js version", Colors.RED)
        return False
    
    # Install frontend dependencies
    frontend_dir = Path("SIHH-main")
    if frontend_dir.exists():
        if not run_command("npm install", "Installing frontend dependencies", cwd=frontend_dir):
            return False
    else:
        print_colored("  ⚠️ Frontend directory not found, skipping frontend setup", Colors.YELLOW)
    
    return True

def create_environment_file():
    """Create .env file from template"""
    print_step("3", "Creating Environment Configuration")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print_colored("  ✅ .env file already exists", Colors.GREEN)
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print_colored("  ✅ Created .env file from template", Colors.GREEN)
        print_colored("  📝 Please review and update .env file with your specific configuration", Colors.YELLOW)
    else:
        print_colored("  ⚠️ env.example not found, creating basic .env file", Colors.YELLOW)
        with open(env_file, "w") as f:
            f.write("""# RailOptima Environment Configuration
API_HOST=localhost
API_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_PORT=9002
DEBUG=true
ENVIRONMENT=development
""")
    
    return True

def create_directories():
    """Create necessary directories"""
    print_step("4", "Creating Required Directories")
    
    directories = [
        "reports",
        "logs",
        "data",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print_colored(f"  ✅ Created directory: {directory}", Colors.GREEN)
        else:
            print_colored(f"  ✅ Directory already exists: {directory}", Colors.GREEN)
    
    return True

def test_installation():
    """Test the installation"""
    print_step("5", "Testing Installation")
    
    # Test Python imports
    try:
        import pandas
        import matplotlib
        import fastapi
        print_colored("  ✅ Python dependencies imported successfully", Colors.GREEN)
    except ImportError as e:
        print_colored(f"  ❌ Python dependency import failed: {e}", Colors.RED)
        return False
    
    # Test if frontend can start (just check if dependencies are installed)
    frontend_dir = Path("SIHH-main")
    if frontend_dir.exists():
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            print_colored("  ✅ Frontend dependencies installed successfully", Colors.GREEN)
        else:
            print_colored("  ⚠️ Frontend dependencies may not be properly installed", Colors.YELLOW)
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete!")
    
    print_colored("\n🚀 Next Steps:", Colors.BOLD)
    print_colored("1. Review and update the .env file with your configuration", Colors.WHITE)
    print_colored("2. Activate the virtual environment:", Colors.WHITE)
    
    if platform.system() == "Windows":
        print_colored("   venv\\Scripts\\activate", Colors.CYAN)
    else:
        print_colored("   source venv/bin/activate", Colors.CYAN)
    
    print_colored("3. Start the application using one of these methods:", Colors.WHITE)
    print_colored("   - PowerShell: .\\start-railoptima.ps1", Colors.CYAN)
    print_colored("   - Batch: start-railoptima.bat", Colors.CYAN)
    print_colored("   - Manual: Follow the README instructions", Colors.CYAN)
    
    print_colored("\n📊 Access URLs:", Colors.BOLD)
    print_colored("   - Frontend: http://localhost:9002", Colors.CYAN)
    print_colored("   - API: http://localhost:8000", Colors.CYAN)
    print_colored("   - API Docs: http://localhost:8000/docs", Colors.CYAN)
    
    print_colored("\n📚 Documentation:", Colors.BOLD)
    print_colored("   - README.md - Main documentation", Colors.WHITE)
    print_colored("   - docs/ - Detailed module documentation", Colors.WHITE)

def main():
    """Main setup function"""
    print_header("RailOptima Environment Setup")
    print_colored("This script will set up RailOptima on your machine.", Colors.WHITE)
    print_colored("Make sure you have Python 3.8+ and Node.js installed.", Colors.YELLOW)
    
    # Check prerequisites
    if not check_command("python"):
        print_colored("❌ Python is not installed or not in PATH", Colors.RED)
        return False
    
    if not check_command("node"):
        print_colored("❌ Node.js is not installed or not in PATH", Colors.RED)
        print_colored("Please install Node.js from https://nodejs.org/", Colors.YELLOW)
        return False
    
    # Run setup steps
    steps = [
        setup_python_environment,
        setup_node_environment,
        create_environment_file,
        create_directories,
        test_installation
    ]
    
    for step in steps:
        if not step():
            print_colored("\n❌ Setup failed. Please check the errors above.", Colors.RED)
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n\nSetup cancelled by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
