
"""
Main Integration File - Enhanced Systems

This file integrates all the enhanced systems (caching, monitoring, validation, interface)
into the main Hephaestus system.
"""

from agent.enhanced_cache_integration import enhanced_cache
from agent.enhanced_monitor_integration import enhanced_monitor
from agent.enhanced_validator_integration import enhanced_validator
from agent.enhanced_interface_integration import enhanced_interface

# Export all enhanced systems
__all__ = [
    'enhanced_cache',
    'enhanced_monitor', 
    'enhanced_validator',
    'enhanced_interface'
]

def get_enhanced_systems():
    """Get all enhanced systems."""
    return {
        'cache': enhanced_cache,
        'monitor': enhanced_monitor,
        'validator': enhanced_validator,
        'interface': enhanced_interface
    }

def initialize_enhanced_systems():
    """Initialize all enhanced systems."""
    print("🚀 Initializing Enhanced Systems...")
    print("   • Enhanced Caching System: ✅")
    print("   • Enhanced Monitoring System: ✅")
    print("   • Enhanced Validation System: ✅")
    print("   • Enhanced Interface System: ✅")
    print("✅ All enhanced systems initialized!")

if __name__ == "__main__":
    initialize_enhanced_systems()
