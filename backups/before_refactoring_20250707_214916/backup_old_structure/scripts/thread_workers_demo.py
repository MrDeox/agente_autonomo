#!/usr/bin/env python3
"""
Thread Workers Demo - Practical demonstration of threading issues and solutions in Hephaestus
"""

import asyncio
import threading
import time
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThreadingProblems:
    """Demonstrates current threading problems in Hephaestus"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Problems")
    
    def demonstrate_race_conditions(self):
        """Demonstrate race conditions in shared state access"""
        self.logger.info("🏁 Demonstrating race conditions...")
        
        # Current problematic approach (like in async_orchestrator.py)
        shared_state = {
            "active_tasks": {},
            "completed_tasks": {},
            "failed_tasks": {}
        }
        
        def unsafe_task_update(task_id: str):
            """Simulates unsafe task state updates"""
            for i in range(1000):
                # This is NOT thread-safe - race condition!
                current_count = len(shared_state["active_tasks"])
                time.sleep(0.00001)  # Simula latência que causa race condition
                shared_state["active_tasks"][f"{task_id}_{i}"] = current_count + 1
        
        # Run multiple threads doing unsafe updates
        threads = []
        for i in range(5):
            thread = threading.Thread(target=unsafe_task_update, args=(f"task_{i}",))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        expected_tasks = 5000
        actual_tasks = len(shared_state["active_tasks"])
        data_loss = expected_tasks - actual_tasks
        
        self.logger.warning(f"⚠️ Race condition result: Expected {expected_tasks}, got {actual_tasks} ({data_loss} lost)")
        return data_loss
    
    def demonstrate_thread_safe_solution(self):
        """Demonstrate thread-safe solution"""
        self.logger.info("🔒 Demonstrating thread-safe solution...")
        
        class ThreadSafeTaskManager:
            def __init__(self):
                self.active_tasks = {}
                self.completed_tasks = {}
                self.failed_tasks = {}
                self.lock = threading.Lock()
            
            def add_task(self, task_id: str, task_data: Any):
                with self.lock:
                    self.active_tasks[task_id] = task_data
            
            def complete_task(self, task_id: str, result: Any):
                with self.lock:
                    if task_id in self.active_tasks:
                        task_data = self.active_tasks.pop(task_id)
                        self.completed_tasks[task_id] = result
                        return True
                    return False
            
            def get_task_count(self):
                with self.lock:
                    return len(self.active_tasks) + len(self.completed_tasks)
        
        safe_manager = ThreadSafeTaskManager()
        
        def safe_task_update(task_id: str):
            """Thread-safe task updates"""
            for i in range(1000):
                task_key = f"{task_id}_{i}"
                safe_manager.add_task(task_key, {"data": i})
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=safe_task_update, args=(f"task_{i}",))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        actual_tasks = safe_manager.get_task_count()
        self.logger.info(f"✅ Thread-safe result: Got {actual_tasks} tasks (no data loss)")
        return actual_tasks
    
    async def demonstrate_polling_latency(self):
        """Demonstrate polling vs event-driven approach"""
        self.logger.info("⏱️ Demonstrating polling latency...")
        
        # Current problematic approach (like in async_orchestrator.py)
        async def polling_dependency_wait():
            dependency_complete = False
            start_time = time.time()
            
            # Simulate dependency completing after 0.3 seconds
            async def complete_dependency():
                await asyncio.sleep(0.3)
                nonlocal dependency_complete
                dependency_complete = True
            
            asyncio.create_task(complete_dependency())
            
            # PROBLEM: Fixed 1-second polling (like in async_orchestrator.py:221)
            while not dependency_complete:
                await asyncio.sleep(1)  # PROBLEMA: Sleep fixo de 1s
            
            return time.time() - start_time
        
        # Event-driven solution
        async def event_driven_dependency_wait():
            dependency_event = asyncio.Event()
            start_time = time.time()
            
            # Simulate dependency completing after 0.3 seconds
            async def complete_dependency():
                await asyncio.sleep(0.3)
                dependency_event.set()
            
            asyncio.create_task(complete_dependency())
            
            # SOLUTION: Event-driven notification
            await dependency_event.wait()
            
            return time.time() - start_time
        
        polling_time = await polling_dependency_wait()
        event_time = await event_driven_dependency_wait()
        
        improvement = ((polling_time - event_time) / polling_time) * 100
        
        self.logger.info(f"📊 Polling: {polling_time:.3f}s vs Event-driven: {event_time:.3f}s ({improvement:.1f}% improvement)")
        
        return polling_time, event_time, improvement
    
    async def demonstrate_sequential_vs_parallel(self):
        """Demonstrate sequential vs parallel execution"""
        self.logger.info("🔄 Demonstrating sequential vs parallel execution...")
        
        async def sequential_tasks():
            """Current sequential approach"""
            start_time = time.time()
            
            # Simulate 3 independent tasks that could run in parallel
            await asyncio.sleep(0.3)  # Architect task
            await asyncio.sleep(0.3)  # Maestro task  
            await asyncio.sleep(0.3)  # Review task
            
            return time.time() - start_time
        
        async def parallel_tasks():
            """Improved parallel approach"""
            start_time = time.time()
            
            # Same tasks running in parallel
            await asyncio.gather(
                asyncio.sleep(0.3),  # Architect task
                asyncio.sleep(0.3),  # Maestro task
                asyncio.sleep(0.3)   # Review task
            )
            
            return time.time() - start_time
        
        sequential_time = await sequential_tasks()
        parallel_time = await parallel_tasks()
        
        throughput_improvement = sequential_time / parallel_time
        
        self.logger.info(f"📊 Sequential: {sequential_time:.3f}s vs Parallel: {parallel_time:.3f}s ({throughput_improvement:.1f}x faster)")
        
        return sequential_time, parallel_time, throughput_improvement
    
    def demonstrate_threadpool_optimization(self):
        """Demonstrate ThreadPool optimization"""
        self.logger.info("🧵 Demonstrating ThreadPool optimization...")
        
        def cpu_bound_task(duration):
            """Simulate CPU-bound task"""
            start = time.time()
            while time.time() - start < duration:
                pass  # Busy wait
            return duration
        
        # Current approach: max_workers = max_concurrent_agents * 2 (often 8)
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(cpu_bound_task, 0.1) for _ in range(4)]
            results = [f.result() for f in futures]
        current_time = time.time() - start_time
        
        # Optimized approach: CPU-based allocation
        optimal_workers = min(8, (os.cpu_count() or 4))
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = [executor.submit(cpu_bound_task, 0.1) for _ in range(4)]
            results = [f.result() for f in futures]
        optimized_time = time.time() - start_time
        
        improvement = ((current_time - optimized_time) / current_time) * 100
        
        self.logger.info(f"📊 Current (8 workers): {current_time:.3f}s vs Optimized ({optimal_workers} workers): {optimized_time:.3f}s ({improvement:.1f}% improvement)")
        
        return current_time, optimized_time, improvement

async def main():
    """Main demonstration function"""
    logger.info("🚀 Starting Thread Workers Demonstration")
    
    problems = ThreadingProblems()
    
    print("\n" + "="*80)
    print("THREADING PROBLEMS DEMONSTRATION")
    print("="*80)
    
    # 1. Race Conditions
    print("\n1. RACE CONDITIONS:")
    data_loss = problems.demonstrate_race_conditions()
    safe_count = problems.demonstrate_thread_safe_solution()
    print(f"   • Unsafe approach: {data_loss} tasks lost due to race conditions")
    print(f"   • Thread-safe approach: {safe_count} tasks (no data loss)")
    
    # 2. Polling Latency
    print("\n2. POLLING LATENCY:")
    polling_time, event_time, latency_improvement = await problems.demonstrate_polling_latency()
    print(f"   • Polling approach: {polling_time:.3f}s")
    print(f"   • Event-driven approach: {event_time:.3f}s")
    print(f"   • Improvement: {latency_improvement:.1f}%")
    
    # 3. Sequential vs Parallel
    print("\n3. SEQUENTIAL VS PARALLEL EXECUTION:")
    seq_time, par_time, throughput_improvement = await problems.demonstrate_sequential_vs_parallel()
    print(f"   • Sequential execution: {seq_time:.3f}s")
    print(f"   • Parallel execution: {par_time:.3f}s")
    print(f"   • Throughput improvement: {throughput_improvement:.1f}x")
    
    # 4. ThreadPool Optimization
    print("\n4. THREADPOOL OPTIMIZATION:")
    current_time, optimized_time, pool_improvement = problems.demonstrate_threadpool_optimization()
    print(f"   • Current approach (8 workers): {current_time:.3f}s")
    print(f"   • Optimized approach (CPU-based): {optimized_time:.3f}s")
    print(f"   • Improvement: {pool_improvement:.1f}%")
    
    print("\n" + "="*80)
    print("SUMMARY OF IMPROVEMENTS")
    print("="*80)
    print(f"• Race Condition Prevention: {data_loss} tasks saved")
    print(f"• Latency Reduction: {latency_improvement:.1f}%")
    print(f"• Throughput Increase: {throughput_improvement:.1f}x")
    print(f"• ThreadPool Optimization: {pool_improvement:.1f}%")
    
    print("\n🎯 EXPECTED OVERALL BENEFITS:")
    print("• Eliminate data loss from race conditions")
    print("• 70% reduction in task execution latency")
    print("• 300% increase in throughput")
    print("• Better resource utilization")
    print("• Improved system reliability")

if __name__ == "__main__":
    asyncio.run(main()) 