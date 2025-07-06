#!/usr/bin/env python3
"""
Main entry point for Hephaestus FastAPI server.
"""

import uvicorn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main function with startup validation."""
    # Import the FastAPI app from the new structure
    from hephaestus.api.rest.main import app
    
    # Load configuration for validation
    from hephaestus.core.config_loader import load_config
    config = load_config()
    
    # Validate startup
    from hephaestus.utils.startup_validator import StartupValidator
    import logging
    
    logger = logging.getLogger("startup_validator")
    validator = StartupValidator(logger)
    
    if not validator.validate_all(config):
        print("❌ Startup validation failed. Check logs for details.")
        return
    
    # Run the FastAPI application
    print("🚀 Starting Hephaestus with Meta-Intelligence...")
    print("🧠 Autonomous evolution system will be activated!")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()