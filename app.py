from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading
import logging

from agent.queue_manager import QueueManager
from agent.hephaestus_agent import HephaestusAgent # Import HephaestusAgent
from agent.cycle_runner import run_cycles # Import run_cycles
from agent.config_loader import load_config

# Configure logging for the FastAPI app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize the QueueManager
queue_manager = QueueManager()

# This will hold the HephaestusAgent instance and its worker thread
hephaestus_agent_instance = None
hephaestus_worker_thread = None

class Objective(BaseModel):
    objective: str

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
        config=load_config() # Pass the loaded config
    )

    # Start the Hephaestus worker thread
    hephaestus_worker_thread = threading.Thread(
        target=run_cycles, 
        args=(hephaestus_agent_instance, queue_manager,),
        daemon=True # Daemon threads exit when the main program exits
    )
    hephaestus_worker_thread.start()
    logger.info("Hephaestus worker thread started.")

@app.post("/submit_objective")
async def submit_objective(obj: Objective):
    logger.info(f"Received new objective: {obj.objective}")
    queue_manager.put_objective(obj.objective)
    return {"message": "Objective submitted successfully", "objective": obj.objective}

@app.get("/status")
async def get_status():
    return {
        "status": "running",
        "queue_size": queue_manager._queue.qsize(),
        "worker_active": hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
