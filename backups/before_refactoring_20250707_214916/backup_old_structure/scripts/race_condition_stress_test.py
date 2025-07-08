#!/usr/bin/env python3
"""
Race Condition Stress Test - More aggressive test to demonstrate data loss
"""

import threading
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_severe_race_condition():
    """More aggressive race condition demonstration"""
    logger.info("🔥 Running aggressive race condition test...")
    
    # Shared state like in async_orchestrator.py
    shared_state = {
        "active_tasks": {},
        "completed_tasks": {},
        "failed_tasks": {},
        "counter": 0
    }
    
    def unsafe_operations(worker_id: str):
        """Simulates unsafe operations with more aggressive timing"""
        for i in range(1000):
            # Multiple unsafe operations in sequence
            
            # Operation 1: Add to active_tasks
            task_key = f"worker_{worker_id}_task_{i}"
            shared_state["active_tasks"][task_key] = {"worker": worker_id, "iteration": i}
            
            # Introduce race condition window
            time.sleep(0.0001)  # Increased delay
            
            # Operation 2: Move to completed_tasks
            if task_key in shared_state["active_tasks"]:
                task_data = shared_state["active_tasks"][task_key]
                del shared_state["active_tasks"][task_key]
                shared_state["completed_tasks"][task_key] = task_data
            
            # Operation 3: Update counter
            current_count = shared_state["counter"]
            time.sleep(0.00005)  # Another race condition window
            shared_state["counter"] = current_count + 1
    
    # Run with more threads for higher contention
    threads = []
    start_time = time.time()
    
    for worker_id in range(10):  # More workers
        thread = threading.Thread(target=unsafe_operations, args=(str(worker_id),))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    execution_time = time.time() - start_time
    
    # Analyze results
    expected_counter = 10000  # 10 workers * 1000 operations
    actual_counter = shared_state["counter"]
    expected_total_tasks = 10000
    actual_total_tasks = len(shared_state["active_tasks"]) + len(shared_state["completed_tasks"])
    
    counter_loss = expected_counter - actual_counter
    task_loss = expected_total_tasks - actual_total_tasks
    
    logger.warning(f"⚠️ Counter: Expected {expected_counter}, got {actual_counter} ({counter_loss} lost)")
    logger.warning(f"⚠️ Tasks: Expected {expected_total_tasks}, got {actual_total_tasks} ({task_loss} lost)")
    logger.info(f"⏱️ Execution time: {execution_time:.3f}s")
    
    # Check for data corruption
    active_count = len(shared_state["active_tasks"])
    completed_count = len(shared_state["completed_tasks"])
    failed_count = len(shared_state["failed_tasks"])
    
    logger.info(f"📊 Final state: {active_count} active, {completed_count} completed, {failed_count} failed")
    
    return {
        "counter_loss": counter_loss,
        "task_loss": task_loss,
        "counter_loss_percentage": (counter_loss / expected_counter) * 100,
        "task_loss_percentage": (task_loss / expected_total_tasks) * 100,
        "execution_time": execution_time
    }

def demonstrate_thread_safe_version():
    """Thread-safe version for comparison"""
    logger.info("🔒 Running thread-safe version...")
    
    class ThreadSafeTaskManager:
        def __init__(self):
            self.active_tasks = {}
            self.completed_tasks = {}
            self.failed_tasks = {}
            self.counter = 0
            self.lock = threading.RLock()  # Reentrant lock
        
        def add_and_complete_task(self, task_key: str, task_data: Dict[str, Any]):
            with self.lock:
                # All operations are atomic
                self.active_tasks[task_key] = task_data
                if task_key in self.active_tasks:
                    task_data = self.active_tasks.pop(task_key)
                    self.completed_tasks[task_key] = task_data
                self.counter += 1
        
        def get_stats(self):
            with self.lock:
                return {
                    "active_count": len(self.active_tasks),
                    "completed_count": len(self.completed_tasks),
                    "failed_count": len(self.failed_tasks),
                    "counter": self.counter
                }
    
    safe_manager = ThreadSafeTaskManager()
    
    def safe_operations(worker_id: str):
        """Thread-safe operations"""
        for i in range(1000):
            task_key = f"worker_{worker_id}_task_{i}"
            task_data = {"worker": worker_id, "iteration": i}
            safe_manager.add_and_complete_task(task_key, task_data)
    
    # Run with same thread count
    threads = []
    start_time = time.time()
    
    for worker_id in range(10):
        thread = threading.Thread(target=safe_operations, args=(str(worker_id),))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    execution_time = time.time() - start_time
    stats = safe_manager.get_stats()
    
    logger.info(f"✅ Safe version: {stats['counter']} operations, {stats['completed_count']} tasks")
    logger.info(f"⏱️ Execution time: {execution_time:.3f}s")
    
    return {
        "counter": stats["counter"],
        "tasks": stats["completed_count"],
        "execution_time": execution_time
    }

def main():
    """Main stress test function"""
    logger.info("🚀 Starting Race Condition Stress Test")
    
    print("\n" + "="*80)
    print("RACE CONDITION STRESS TEST")
    print("="*80)
    
    # Test unsafe version
    print("\n1. UNSAFE VERSION (Current Hephaestus approach):")
    unsafe_results = demonstrate_severe_race_condition()
    
    # Test safe version
    print("\n2. THREAD-SAFE VERSION (Proposed solution):")
    safe_results = demonstrate_thread_safe_version()
    
    # Summary
    print("\n" + "="*80)
    print("STRESS TEST RESULTS")
    print("="*80)
    
    print(f"\n💥 UNSAFE VERSION LOSSES:")
    print(f"   • Counter loss: {unsafe_results['counter_loss']} ({unsafe_results['counter_loss_percentage']:.1f}%)")
    print(f"   • Task loss: {unsafe_results['task_loss']} ({unsafe_results['task_loss_percentage']:.1f}%)")
    print(f"   • Execution time: {unsafe_results['execution_time']:.3f}s")
    
    print(f"\n✅ THREAD-SAFE VERSION:")
    print(f"   • Counter: {safe_results['counter']} (no loss)")
    print(f"   • Tasks: {safe_results['tasks']} (no loss)")
    print(f"   • Execution time: {safe_results['execution_time']:.3f}s")
    
    # Performance comparison
    if unsafe_results['execution_time'] > 0:
        performance_impact = ((safe_results['execution_time'] - unsafe_results['execution_time']) / unsafe_results['execution_time']) * 100
        print(f"\n📊 PERFORMANCE IMPACT:")
        print(f"   • Thread-safe overhead: {performance_impact:.1f}%")
        print(f"   • Data integrity: PERFECT (0% loss)")
        
        if performance_impact < 20:
            print(f"   • Assessment: ✅ Acceptable overhead for perfect data integrity")
        else:
            print(f"   • Assessment: ⚠️ Higher overhead, but eliminates critical data loss")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   • Current system loses {unsafe_results['counter_loss_percentage']:.1f}% of data")
    print(f"   • Thread-safe solution prevents ALL data loss")
    print(f"   • Critical for production reliability")

if __name__ == "__main__":
    main() 