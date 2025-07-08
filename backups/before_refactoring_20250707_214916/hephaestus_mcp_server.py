#!/usr/bin/env python3
"""
MCP Server entry point for Hephaestus.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the MCP server
from hephaestus.api.mcp.server import main

if __name__ == "__main__":
    main()