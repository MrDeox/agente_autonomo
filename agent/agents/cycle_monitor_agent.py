"""
Cycle Monitor Agent

Automatically detects and resolves problems of stuck cycles, orphaned processes, and system bottlenecks
"""
import psutil
import time
import logging
import subprocess
import os
import signal
from typing import List, Dict, Any, Optional
from pathlib import Path
import threading

logger = logging.getLogger("CycleMonitorAgent")

class CycleMonitorAgent:
    """Agent that monitors and resolves system bottlenecks and stuck cycles"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitoring_active = False
        self.monitor_thread = None
        self.check_interval = config.get("cycle_monitor_interval", 60)  # 1 minute
        self.max_cycle_time = config.get("max_cycle_time", 300)  # 5 minutes
        self.max_memory_usage = config.get("max_memory_usage", 80)  # 80%
        self.max_cpu_usage = config.get("max_cpu_usage", 90)  # 90%
        
        logger.info("🔄 Cycle Monitor Agent initialized")
    
    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.monitoring_active:
            logger.warning("Cycle monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔄 Cycle monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🔄 Cycle monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_system_health()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in cycle monitor loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _check_system_health(self):
        """Check overall system health and resolve issues"""
        issues_found = []
        
        # Check for stuck processes
        stuck_processes = self._detect_stuck_processes()
        if stuck_processes:
            issues_found.append(f"Found {len(stuck_processes)} stuck processes")
            self._resolve_stuck_processes(stuck_processes)
        
        # Check for orphaned sandboxes
        orphaned_sandboxes = self._detect_orphaned_sandboxes()
        if orphaned_sandboxes:
            issues_found.append(f"Found {len(orphaned_sandboxes)} orphaned sandboxes")
            self._cleanup_orphaned_sandboxes(orphaned_sandboxes)
        
        # Check memory usage
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > self.max_memory_usage:
            issues_found.append(f"High memory usage: {memory_usage}%")
            self._optimize_memory_usage()
        
        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > self.max_cpu_usage:
            issues_found.append(f"High CPU usage: {cpu_usage}%")
            self._optimize_cpu_usage()
        
        # Check for long-running cycles
        long_cycles = self._detect_long_running_cycles()
        if long_cycles:
            issues_found.append(f"Found {len(long_cycles)} long-running cycles")
            self._resolve_long_cycles(long_cycles)
        
        if issues_found:
            logger.warning(f"🔄 System health issues detected: {', '.join(issues_found)}")
        else:
            logger.debug("✅ System health check passed")
    
    def _detect_stuck_processes(self) -> List[Dict[str, Any]]:
        """Detect processes that might be stuck"""
        stuck_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                # Check for processes consuming high CPU for too long
                if proc.info['cpu_percent'] > 50:
                    # Get process creation time
                    create_time = proc.info['create_time']
                    if create_time:
                        uptime = time.time() - create_time
                        if uptime > 300:  # 5 minutes
                            stuck_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'uptime': uptime
                            })
                
                # Check for multiprocessing processes that might be orphaned
                if 'multiprocessing' in proc.info['name'].lower():
                    create_time = proc.info['create_time']
                    if create_time:
                        uptime = time.time() - create_time
                        if uptime > 600:  # 10 minutes
                            stuck_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'uptime': uptime,
                                'type': 'orphaned_multiprocessing'
                            })
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return stuck_processes
    
    def _resolve_stuck_processes(self, stuck_processes: List[Dict[str, Any]]):
        """Resolve stuck processes"""
        for process in stuck_processes:
            try:
                pid = process['pid']
                name = process['name']
                
                # Try graceful termination first
                try:
                    os.kill(pid, signal.SIGTERM)
                    logger.info(f"🔄 Sent SIGTERM to stuck process {name} (PID: {pid})")
                    time.sleep(2)
                    
                    # Check if process is still running
                    if psutil.pid_exists(pid):
                        # Force kill if still running
                        os.kill(pid, signal.SIGKILL)
                        logger.info(f"🔄 Force killed stuck process {name} (PID: {pid})")
                    else:
                        logger.info(f"✅ Successfully terminated stuck process {name} (PID: {pid})")
                        
                except ProcessLookupError:
                    logger.info(f"Process {name} (PID: {pid}) already terminated")
                except PermissionError:
                    logger.warning(f"Cannot terminate process {name} (PID: {pid}) - permission denied")
                    
            except Exception as e:
                logger.error(f"Error resolving stuck process {process}: {e}")
    
    def _detect_orphaned_sandboxes(self) -> List[str]:
        """Detect orphaned sandbox directories"""
        orphaned_sandboxes = []
        
        try:
            # Look for hephaestus sandboxes older than 30 minutes
            sandbox_pattern = "/tmp/hephaestus_sandbox_*"
            import glob
            sandboxes = glob.glob(sandbox_pattern)
            
            current_time = time.time()
            for sandbox in sandboxes:
                try:
                    # Check if sandbox is older than 30 minutes
                    sandbox_age = current_time - os.path.getctime(sandbox)
                    if sandbox_age > 1800:  # 30 minutes
                        orphaned_sandboxes.append(sandbox)
                except OSError:
                    # Sandbox might have been deleted
                    continue
                    
        except Exception as e:
            logger.error(f"Error detecting orphaned sandboxes: {e}")
        
        return orphaned_sandboxes
    
    def _cleanup_orphaned_sandboxes(self, orphaned_sandboxes: List[str]):
        """Clean up orphaned sandbox directories"""
        for sandbox in orphaned_sandboxes:
            try:
                import shutil
                shutil.rmtree(sandbox)
                logger.info(f"🧹 Cleaned up orphaned sandbox: {sandbox}")
            except Exception as e:
                logger.error(f"Error cleaning up sandbox {sandbox}: {e}")
    
    def _detect_long_running_cycles(self) -> List[Dict[str, Any]]:
        """Detect cycles that have been running too long"""
        long_cycles = []
        
        # This would need to be integrated with the actual cycle tracking system
        # For now, we'll check for processes that might indicate stuck cycles
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('test' in arg.lower() for arg in cmdline):
                    # Check if test process has been running too long
                    create_time = proc.info.get('create_time')
                    if create_time:
                        uptime = time.time() - create_time
                        if uptime > self.max_cycle_time:
                            long_cycles.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'uptime': uptime
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return long_cycles
    
    def _resolve_long_cycles(self, long_cycles: List[Dict[str, Any]]):
        """Resolve long-running cycles"""
        for cycle in long_cycles:
            try:
                pid = cycle['pid']
                name = cycle['name']
                
                # Terminate long-running test processes
                if 'test' in name.lower() or 'pytest' in name.lower():
                    os.kill(pid, signal.SIGTERM)
                    logger.info(f"🔄 Terminated long-running test process {name} (PID: {pid})")
                    
            except Exception as e:
                logger.error(f"Error resolving long cycle {cycle}: {e}")
    
    def _optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            logger.info("🧹 Forced garbage collection to optimize memory")
            
            # Clear Python cache if needed
            cache_dirs = ['__pycache__', '.pytest_cache', '.ruff_cache']
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                    logger.info(f"🧹 Cleared cache directory: {cache_dir}")
                    
        except Exception as e:
            logger.error(f"Error optimizing memory usage: {e}")
    
    def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        try:
            # Reduce monitoring frequency temporarily
            original_interval = self.check_interval
            self.check_interval = min(self.check_interval * 2, 300)  # Max 5 minutes
            logger.info(f"🔄 Reduced monitoring frequency to {self.check_interval}s due to high CPU usage")
            
            # Restore original interval after some time
            def restore_interval():
                time.sleep(60)  # Wait 1 minute
                self.check_interval = original_interval
                logger.info(f"🔄 Restored monitoring frequency to {self.check_interval}s")
            
            threading.Thread(target=restore_interval, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error optimizing CPU usage: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Count active processes
            active_processes = len([p for p in psutil.process_iter() if p.is_running()])
            
            # Check for stuck processes
            stuck_processes = self._detect_stuck_processes()
            
            # Check for orphaned sandboxes
            orphaned_sandboxes = self._detect_orphaned_sandboxes()
            
            return {
                "monitoring_active": self.monitoring_active,
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent,
                "active_processes": active_processes,
                "stuck_processes_count": len(stuck_processes),
                "orphaned_sandboxes_count": len(orphaned_sandboxes),
                "check_interval": self.check_interval,
                "last_check": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    def force_cleanup(self):
        """Force immediate cleanup of all detected issues"""
        logger.info("🧹 Starting forced cleanup...")
        
        # Clean up stuck processes
        stuck_processes = self._detect_stuck_processes()
        if stuck_processes:
            self._resolve_stuck_processes(stuck_processes)
        
        # Clean up orphaned sandboxes
        orphaned_sandboxes = self._detect_orphaned_sandboxes()
        if orphaned_sandboxes:
            self._cleanup_orphaned_sandboxes(orphaned_sandboxes)
        
        # Optimize memory
        self._optimize_memory_usage()
        
        logger.info("🧹 Forced cleanup completed")
        
        return {
            "stuck_processes_cleaned": len(stuck_processes),
            "sandboxes_cleaned": len(orphaned_sandboxes),
            "memory_optimized": True
        } 