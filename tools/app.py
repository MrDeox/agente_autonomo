from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading
import logging

from agent.queue_manager import QueueManager
from agent.hephaestus_agent import HephaestusAgent # Import HephaestusAgent
from agent.config_loader import load_config

# Configure logging for the FastAPI app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hephaestus Meta-Intelligence API",
    description="Advanced Autonomous Agent with Self-Improving Capabilities",
    version="2.0.0"
)

# Initialize the QueueManager
queue_manager = QueueManager()

# This will hold the HephaestusAgent instance and its worker thread
hephaestus_agent_instance = None
hephaestus_worker_thread = None

class Objective(BaseModel):
    objective: str

class SelfReflectionRequest(BaseModel):
    focus_area: str = "general"

@app.on_event("startup")
async def startup_event():
    global hephaestus_agent_instance, hephaestus_worker_thread
    logger.info("Starting up Hephaestus server...")

    # Initialize HephaestusAgent (without immediately running cycles)
    # The agent's run() method will be called by the worker thread
    hephaestus_agent_instance = HephaestusAgent(
        logger_instance=logger, # Use the app's logger
        continuous_mode=True, # Agent will run continuously in the background
        objective_stack_depth_for_testing=None, # No limit for server mode
        config=load_config(), # Pass the unified config
        queue_manager=queue_manager # Pass the shared queue manager
    )

    # 🧠 ACTIVATE META-INTELLIGENCE - This is where the magic happens!
    logger.info("🧠 ACTIVATING META-INTELLIGENCE SYSTEMS...")
    hephaestus_agent_instance.start_meta_intelligence()
    logger.info("🚀 Meta-Intelligence activated! Agent can now evolve itself!")

    # Start the Hephaestus worker thread
    hephaestus_worker_thread = threading.Thread(
        target=hephaestus_agent_instance.run, 
        daemon=True # Daemon threads exit when the main program exits
    )
    hephaestus_worker_thread.start()
    logger.info("Hephaestus worker thread started.")

@app.post("/submit_objective")
async def submit_objective(obj: Objective):
    """Submit a new objective for the agent to process"""
    logger.info(f"Received new objective: {obj.objective}")
    queue_manager.put_objective(obj.objective)
    return {"message": "Objective submitted successfully", "objective": obj.objective}

@app.get("/status")
async def get_status():
    """Get basic status of the agent and meta-intelligence"""
    meta_intelligence_status = {}
    if hephaestus_agent_instance:
        try:
            meta_intelligence_status = hephaestus_agent_instance.evolution_manager.get_evolution_report()
        except Exception as e:
            meta_intelligence_status = {"error": str(e)}
    
    return {
        "status": "running",
        "queue_size": queue_manager._queue.qsize(),
        "worker_active": hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False,
        "meta_intelligence": meta_intelligence_status,
        "evolution_active": hephaestus_agent_instance.meta_intelligence_active if hephaestus_agent_instance else False
    }

@app.get("/meta_intelligence/comprehensive_status")
async def get_comprehensive_meta_intelligence_status():
    """Get comprehensive status of all meta-intelligence systems"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return hephaestus_agent_instance.get_comprehensive_meta_intelligence_status()

@app.post("/meta_intelligence/deep_reflection")
async def perform_deep_self_reflection(request: SelfReflectionRequest):
    """Trigger deep self-reflection and introspection"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return hephaestus_agent_instance.perform_deep_self_reflection(request.focus_area)

@app.get("/meta_intelligence/self_awareness_report")
async def get_self_awareness_report():
    """Get comprehensive self-awareness report"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return hephaestus_agent_instance.get_self_awareness_report()

@app.get("/knowledge_system/status")
async def get_knowledge_system_status():
    """Get status of the knowledge acquisition system"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        return hephaestus_agent_instance.knowledge_system.get_knowledge_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge system status: {str(e)}")

@app.get("/model_optimizer/status")
async def get_model_optimizer_status():
    """Get status of the model optimization system"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        return hephaestus_agent_instance.model_optimizer.get_optimization_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model optimizer status: {str(e)}")

@app.get("/root_cause_analyzer/status")
async def get_root_cause_analyzer_status():
    """Get status of the root cause analysis system"""
    if not hephaestus_agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        return hephaestus_agent_instance.root_cause_analyzer.get_analysis_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get root cause analyzer status: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "meta_intelligence_active": hephaestus_agent_instance.meta_intelligence_active if hephaestus_agent_instance else False,
        "worker_thread_alive": hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False,
        "queue_size": queue_manager._queue.qsize(),
        "message": "🧠 Hephaestus is evolving and improving itself!"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
