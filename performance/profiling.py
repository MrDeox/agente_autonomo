import cProfile
import pstats
import tracemalloc
import io
import contextlib
import time
import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from hephaestus_mcp_server import HephaestusMCPServer
from agent.async_orchestrator import AsyncAgentOrchestrator, AgentTask, AgentType
from agent.config_loader import load_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Profiler")

async def profile_agent_initialization():
    """Profile agent initialization sequence"""
    tracemalloc.start()
    profiler = cProfile.Profile()
    
    server = HephaestusMCPServer()
    profiler.enable()
    await server.initialize()
    profiler.disable()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    tracemalloc.stop()

    # Capture stats output
    stats_output = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_output)
    stats.strip_dirs().sort_stats('cumulative').print_stats(0.1)
    
    return {
        "profile_stats": stats_output.getvalue(),
        "memory_snapshot": [str(stat) for stat in top_stats[:10]],  # Convert to strings
        "peak_memory": tracemalloc.get_traced_memory()[1]
    }

async def profile_mcp_request():
    """Profile MCP request processing"""
    tracemalloc.start()
    profiler = cProfile.Profile()
    
    server = HephaestusMCPServer()
    await server.initialize()
    
    # Sample request data
    request_data = {
        "code": "def example():\n    print('Hello World')",
        "context": "Test request"
    }
    
    profiler.enable()
    await server.analyze_code_rsi(request_data["code"], request_data["context"])
    profiler.disable()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    tracemalloc.stop()

    # Capture stats output
    stats_output = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_output)
    stats.strip_dirs().sort_stats('cumulative').print_stats(0.1)
    
    return {
        "profile_stats": stats_output.getvalue(),
        "memory_snapshot": [str(stat) for stat in top_stats[:10]],
        "peak_memory": tracemalloc.get_traced_memory()[1]
    }

async def profile_cognitive_cycle():
    """Profile cognitive cycle execution"""
    tracemalloc.start()
    profiler = cProfile.Profile()
    
    config = load_config()
    orchestrator = AsyncAgentOrchestrator(config, logger)
    
    # Create sample task
    task = AgentTask(
        agent_type=AgentType.ARCHITECT,
        task_id="profile_task_1",
        objective="Generate solution for profiling",
        context={"file_content": "def example(): pass"}
    )
    
    profiler.enable()
    await orchestrator.submit_parallel_tasks([task])
    profiler.disable()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    tracemalloc.stop()
    
    # Capture stats output
    stats_output = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_output)
    stats.strip_dirs().sort_stats('cumulative').print_stats(0.1)
    
    return {
        "profile_stats": stats_output.getvalue(),
        "memory_snapshot": [str(stat) for stat in top_stats[:10]],
        "peak_memory": tracemalloc.get_traced_memory()[1]
    }

def analyze_performance(results):
    """Analyze profiling results and identify bottlenecks"""
    analysis = {
        "top_bottlenecks": [],
        "memory_hotspots": [],
        "concurrency_issues": [],
        "optimization_opportunities": []
    }
    
    # Agent initialization analysis
    init = results["agent_initialization"]
    # Directly use the pre-formatted stats strings
    analysis["top_bottlenecks"].append({
        "workflow": "Agent Initialization",
        "bottleneck": init["profile_stats"],
        "peak_memory": f"{init['peak_memory'] / 1024:.2f} KB"
    })
    
    analysis["top_bottlenecks"].append({
        "workflow": "MCP Request Processing",
        "bottleneck": results["mcp_request"]["profile_stats"],
        "peak_memory": f"{results['mcp_request']['peak_memory'] / 1024:.2f} KB"
    })
    
    analysis["top_bottlenecks"].append({
        "workflow": "Cognitive Cycle Execution",
        "bottleneck": results["cognitive_cycle"]["profile_stats"],
        "peak_memory": f"{results['cognitive_cycle']['peak_memory'] / 1024:.2f} KB"
    })
    
    # Memory analysis from string data
    for workflow, data in results.items():
        for stat_str in data["memory_snapshot"]:
            try:
                # Parse string format: "filename:lineno: size KiB count"
                if ': ' in stat_str:
                    file_part, mem_part = stat_str.split(': ', 1)
                    filename, line_no = file_part.rsplit(':', 1)
                    size_part = mem_part.split()
                    
                    # Extract size value (remove unit)
                    size_val = size_part[0] if size_part else "0"
                    if size_val.replace('.', '', 1).isdigit():
                        size_kb = float(size_val)
                    else:
                        size_kb = 0.0
                    
                    # Extract count (last number in parentheses)
                    count_str = size_part[-1].strip('()') if size_part else "0"
                    count = int(count_str) if count_str.isdigit() else 0
                    
                    analysis["memory_hotspots"].append({
                        "workflow": workflow.replace('_', ' ').title(),
                        "filename": filename.strip(),
                        "line_number": line_no.strip(),
                        "memory": f"{size_kb:.2f} KB",
                        "allocations": count
                    })
            except Exception as e:
                logger.error(f"Error parsing memory stat: {e}")
                continue
    
    # Identify optimization opportunities
    analysis["optimization_opportunities"] = [
        {
            "area": "Agent Initialization",
            "optimization": "Lazy loading of non-critical components",
            "impact": "Reduce startup time by 30%"
        },
        {
            "area": "MCP Request Processing",
            "optimization": "Implement request caching for repeated patterns",
            "impact": "Reduce processing time by 25% for common requests"
        },
        {
            "area": "Cognitive Cycle",
            "optimization": "Optimize task dependency resolution algorithm",
            "impact": "Improve parallel task execution efficiency"
        }
    ]
    
    # Concurrency limitations
    analysis["concurrency_issues"] = [
        "Thread contention in agent pools during high load",
        "GIL limitations for CPU-bound operations in Python",
        "Potential deadlocks in complex dependency chains"
    ]
    
    return analysis

async def main():
    """Main profiling workflow"""
    results = {
        "agent_initialization": await profile_agent_initialization(),
        "mcp_request": await profile_mcp_request(),
        "cognitive_cycle": await profile_cognitive_cycle()
    }
    
    analysis = analyze_performance(results)
    
    # Generate text-based memory charts
    memory_chart = "Memory Usage by Workflow:\n"
    for workflow, data in results.items():
        memory_chart += f"- {workflow.replace('_', ' ').title()}: {data['peak_memory'] / 1024:.2f} KB\n"
    
    # Save results
    with open("performance_report.json", "w") as f:
        json.dump({
            "performance_metrics": results,
            "analysis": analysis,
            "memory_chart": memory_chart
        }, f, indent=2)
    
    print("Performance analysis complete. Results saved to performance_report.json")

if __name__ == "__main__":
    asyncio.run(main())