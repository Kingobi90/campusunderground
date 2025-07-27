#!/usr/bin/env python3
"""
Deployment script for the new Moodle integration implementation.
This script helps replace the old implementation with the new one.
"""

import os
import sys
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_deploy')

def backup_file(file_path):
    """Create a backup of a file."""
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} does not exist, skipping backup")
        return False
        
    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
    
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return False

def replace_file(old_file, new_file):
    """Replace old file with new file."""
    if not os.path.exists(new_file):
        logger.error(f"New file {new_file} does not exist")
        return False
        
    # Backup the old file if it exists
    if os.path.exists(old_file):
        if not backup_file(old_file):
            logger.error(f"Failed to backup {old_file}, aborting replacement")
            return False
            
        try:
            # Replace the old file with the new one
            shutil.copy2(new_file, old_file)
            logger.info(f"Replaced {old_file} with {new_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to replace {old_file} with {new_file}: {e}")
            return False
    else:
        # If old file doesn't exist, just copy the new one
        try:
            shutil.copy2(new_file, old_file)
            logger.info(f"Created {old_file} from {new_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create {old_file} from {new_file}: {e}")
            return False

def main():
    """Main function to deploy the new implementation."""
    print("\n=== Campus Underground Moodle Integration Deployment ===\n")
    
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Backend files to replace
    backend_files = [
        ("api_server.py", "api_server_new.py"),
        ("moodle_client.py", "moodle_client_new.py")
    ]
    
    # Frontend files to replace
    frontend_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "campus-underground-frontend", "src", "services"))
    frontend_files = [
        ("moodleService.ts", "moodleService_new.ts")
    ]
    
    # Replace backend files
    print("Deploying backend files:")
    for old_file, new_file in backend_files:
        old_path = os.path.join(base_dir, old_file)
        new_path = os.path.join(base_dir, new_file)
        
        print(f"  - Replacing {old_file}...", end=" ")
        if replace_file(old_path, new_path):
            print("SUCCESS")
        else:
            print("FAILED")
    
    # Replace frontend files
    print("\nDeploying frontend files:")
    for old_file, new_file in frontend_files:
        old_path = os.path.join(frontend_dir, old_file)
        new_path = os.path.join(frontend_dir, new_file)
        
        print(f"  - Replacing {old_file}...", end=" ")
        if replace_file(old_path, new_path):
            print("SUCCESS")
        else:
            print("FAILED")
    
    print("\n=== Deployment Complete ===\n")
    print("Next steps:")
    print("1. Restart the API server: python api_server.py")
    print("2. Run integration tests: python test_integration.py")
    print("3. Test the frontend integration")

if __name__ == "__main__":
    main()
