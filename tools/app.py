from fastapi import FastAPI, HTTPException, Depends, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import threading
import logging
import asyncio
import time
from datetime import datetime
import json
import os

from dotenv import load_dotenv
load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

from agent.queue_manager import QueueManager
from agent.hephaestus_agent import HephaestusAgent
from agent.config_loader import load_config
from agent.arthur_interface_generator import ArthurInterfaceGenerator
from agent.agents.error_detector_agent import ErrorDetectorAgent
from agent.agents.dependency_fixer_agent import DependencyFixerAgent
from agent.agents.cycle_monitor_agent import CycleMonitorAgent
from agent.agents.agent_expansion_coordinator import AgentExpansionCoordinator
from agent.cycle_runner import CycleRunner
from agent.async_orchestrator import AgentType, AgentTask

# Ensure templates directory exists
if not os.path.exists("templates"):
    os.makedirs("templates")

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="Hephaestus Meta-Intelligence API",
    description="""
    🧠 **Advanced Autonomous Agent with Async Orchestration & Auto-Generated Interface**
    
    ### Features:
    - 🚀 **Async Multi-Agent Orchestration**: Parallel processing with up to 8 concurrent agents
    - 🧠 **Meta-Intelligence**: Self-aware and self-improving AI system
    - 🔥 **Turbo Evolution Mode**: 8x performance boost for complex tasks
    - 🎨 **Auto-Generated Interfaces**: Personalized dashboards and controls
    - 📊 **Real-time Monitoring**: Comprehensive system status and metrics
    - 🔍 **Deep Self-Reflection**: Advanced introspection capabilities
    - 🛡️ **Enterprise Security**: Authentication, rate limiting, and CORS support
    
    ### API Categories:
    - **Core Operations**: Basic agent control and objective management
    - **Meta-Intelligence**: Advanced cognitive functions and self-awareness
    - **Orchestration**: Multi-agent coordination and parallel processing
    - **Interface Generation**: Dynamic UI creation and management
    - **Monitoring**: System health, metrics, and performance tracking
    """,
    version="3.1.0",
    contact={
        "name": "Arthur - Project Owner",
        "email": "arthur@hephaestus.ai",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Core Operations",
            "description": "Basic agent control and objective management",
        },
        {
            "name": "Meta-Intelligence",
            "description": "Advanced cognitive functions and self-awareness",
        },
        {
            "name": "Orchestration",
            "description": "Multi-agent coordination and parallel processing",
        },
        {
            "name": "Interface Generation",
            "description": "Dynamic UI creation and management",
        },
        {
            "name": "Monitoring",
            "description": "System health, metrics, and performance tracking",
        },
        {
            "name": "Hot Reload",
            "description": "Real-time code evolution and self-modification",
        },
        {
            "name": "Error Detection",
            "description": "Error detection and monitoring",
        },
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}

# Global instances
queue_manager = QueueManager()
hephaestus_agent_instance = None
hephaestus_worker_thread = None
interface_generator = None
error_detector_agent = None
dependency_fixer_agent = None
cycle_monitor_agent = None
agent_expansion_coordinator = None
log_analyzer_thread = None

# === PYDANTIC MODELS === #

class ObjectiveRequest(BaseModel):
    objective: str = Field(..., description="The objective to be processed by the agent")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5, higher = more important)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the objective")

class DeepReflectionRequest(BaseModel):
    focus_area: str = Field("general", description="Area of focus for deep reflection")
    depth_level: int = Field(3, ge=1, le=5, description="Depth level of reflection (1-5)")
    include_performance_metrics: bool = Field(True, description="Include performance metrics in reflection")

class AsyncEvolutionRequest(BaseModel):
    objective: str = Field(..., description="Primary objective for async evolution")
    enable_turbo: bool = Field(False, description="Enable turbo mode for maximum performance")
    max_concurrent_agents: int = Field(4, ge=1, le=8, description="Maximum number of concurrent agents")
    timeout_seconds: int = Field(300, ge=30, le=3600, description="Timeout for evolution process")

class InterfaceGenerationRequest(BaseModel):
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences for interface generation")
    theme: str = Field("dark", description="Interface theme (dark/light/auto)")
    layout: str = Field("dashboard", description="Interface layout type")
    include_advanced_controls: bool = Field(True, description="Include advanced control panels")

class AgentConfigRequest(BaseModel):
    continuous_mode: bool = Field(False, description="Enable continuous processing mode")
    max_objectives: int = Field(10, ge=1, le=100, description="Maximum objectives in queue")
    evolution_interval: int = Field(3600, ge=300, le=86400, description="Evolution cycle interval in seconds")

class SystemStatusResponse(BaseModel):
    status: str
    timestamp: datetime
    uptime_seconds: int
    version: str
    meta_intelligence_active: bool
    worker_thread_alive: bool
    queue_size: int
    orchestration_status: Dict[str, Any]
    performance_metrics: Dict[str, Any]

# === MIDDLEWARE === #

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Forcing a reload to apply new model configurations
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Simple rate limiting (in production, use proper rate limiting)
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    # Clean old requests (older than 1 minute)
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip] 
        if current_time - req_time < 60
    ]
    
    # Check rate limit (max 100 requests per minute)
    if len(rate_limit_storage[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Max 100 requests per minute."}
        )
    
    rate_limit_storage[client_ip].append(current_time)
    response = await call_next(request)
    return response

# === DEPENDENCY INJECTION === #

def get_auth_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, validate JWT token here
    # For now, just check if token is present
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user": "arthur", "authenticated": True}

# === STARTUP/SHUTDOWN === #

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global hephaestus_agent_instance, hephaestus_worker_thread, interface_generator, error_detector_agent, log_analyzer_thread, dependency_fixer_agent, cycle_monitor_agent, agent_expansion_coordinator
    
    logger.info("🚀 Starting Hephaestus Meta-Intelligence API Server...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize the HephaestusAgent
        hephaestus_agent_instance = HephaestusAgent(
            logger_instance=logger,
            config=config,
            continuous_mode=False,
            queue_manager=queue_manager
        )
        
        # Initialize interface generator
        interface_generator = ArthurInterfaceGenerator(config, logger)
        
        # Initialize Error Detector Agent
        model_config = config.get("models", {}).get("architect_default", {})
        error_detector_agent = ErrorDetectorAgent(model_config, logger)
        error_detector_agent.start_monitoring()
        
        # Initialize Dependency Fixer Agent
        dependency_fixer_agent = DependencyFixerAgent(config)
        
        # Initialize Cycle Monitor Agent
        cycle_monitor_agent = CycleMonitorAgent(config)
        cycle_monitor_agent.start_monitoring()
        
        # Initialize Agent Expansion Coordinator
        agent_expansion_coordinator = AgentExpansionCoordinator(config, logger)
        
        # Start meta-intelligence
        hephaestus_agent_instance.start_meta_intelligence()
        
        # Start the worker thread
        hephaestus_worker_thread = threading.Thread(target=worker_thread, daemon=True)
        hephaestus_worker_thread.start()

        # Start the periodic log analysis thread
        log_analyzer_thread = threading.Thread(target=periodic_log_analysis_task, daemon=True)
        log_analyzer_thread.start()
        
        logger.info("✅ Hephaestus Meta-Intelligence API Server initialized successfully!")
        logger.info("🌐 API Documentation available at: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global hephaestus_agent_instance, hephaestus_worker_thread, log_analyzer_thread
    
    logger.info("🔄 Shutting down Hephaestus Meta-Intelligence API Server...")
    
    try:
        if hephaestus_agent_instance:
            hephaestus_agent_instance.stop_meta_intelligence()
        
        # Note: Worker thread will stop automatically as it's a daemon thread
        
        logger.info("✅ Hephaestus system shutdown complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

def periodic_log_analysis_task():
    """A background task that periodically queues system monitoring tasks."""
    logger.info("📊 Periodic System Monitoring Task started.")
    analysis_interval_seconds = 300 # 5 minutes

    # Initial delay
    time.sleep(30)

    while True:
        try:
            logger.info(f"Monitoring task sleeping for {analysis_interval_seconds} seconds.")
            time.sleep(analysis_interval_seconds)

            if hephaestus_agent_instance and queue_manager:
                # --- Queue Log Analysis Task ---
                logger.info("Queuing periodic log analysis task...")
                log_analysis_objective = {
                    "objective": "Periodically analyze system logs for errors and improvement opportunities.",
                    "is_log_analysis_task": True,
                }
                queue_manager.put_objective(log_analysis_objective)
                logger.info("Log analysis task queued successfully.")
                
                time.sleep(10)

                # --- Queue Debt Hunter Task ---
                logger.info("Queuing periodic debt hunter task...")
                debt_hunter_objective = {
                    "objective": "Proactively hunt for and prioritize technical debt.",
                    "is_debt_hunter_task": True,
                }
                queue_manager.put_objective(debt_hunter_objective)
                logger.info("Debt hunter task queued successfully.")

                time.sleep(10)

                # --- Queue Model Sommelier Task ---
                logger.info("Queuing periodic model sommelier task...")
                model_sommelier_objective = {
                    "objective": "Proactively analyze agent performance and optimize model configurations.",
                    "is_model_sommelier_task": True,
                }
                queue_manager.put_objective(model_sommelier_objective)
                logger.info("Model sommelier task queued successfully.")

                time.sleep(10)

                # --- Queue Linter Task ---
                logger.info("Queuing periodic linter task...")
                linter_objective = {
                    "objective": "Proactively run linter to find and fix code quality issues.",
                    "is_linter_task": True,
                }
                queue_manager.put_objective(linter_objective)
                logger.info("Linter task queued successfully.")

        except Exception as e:
            logger.error(f"❌ Error in periodic monitoring task: {e}", exc_info=True)
            # Wait a bit longer after an error before retrying
            time.sleep(60)

def worker_thread():
    """Starts the agent's main execution loop."""
    global hephaestus_agent_instance
    logger.info("🔄 Worker Thread started, preparing to launch agent loop...")
    
    # It's crucial to wait for the app to be fully started,
    # otherwise the agent instance might not be ready.
    time.sleep(2) 

    if hephaestus_agent_instance:
        try:
            # The CycleRunner contains the main loop that handles both
            # queued and continuously generated objectives. We just need to start it.
            cycle_runner = CycleRunner(hephaestus_agent_instance, hephaestus_agent_instance.queue_manager)
            cycle_runner.run()
        except Exception as e:
            logger.error(f"❌ Critical error in agent's main run loop: {e}", exc_info=True)
    else:
        logger.error("❌ Agent not initialized. Worker thread cannot start.")

def process_objective(objective_data: Any):
    """DEPRECATED: This logic is now handled by the CycleRunner.run() loop."""
    logger.warning("process_objective is deprecated and should not be called.")
    pass

# === CORE OPERATIONS ENDPOINTS === #

@app.get("/", response_class=HTMLResponse, tags=["Core Operations"])
async def root():
    """API Root - Welcome page with navigation"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hephaestus Meta-Intelligence API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .nav-links { display: flex; justify-content: center; gap: 20px; margin: 20px 0; }
            .nav-links a { padding: 10px 20px; background: #007acc; color: white; text-decoration: none; border-radius: 5px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature { padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 Hephaestus Meta-Intelligence API</h1>
            <p>Advanced Autonomous Agent with Async Orchestration</p>
        </div>
        
        <div class="nav-links">
            <a href="/docs">📚 API Documentation</a>
            <a href="/health">🏥 Health Check</a>
            <a href="/arthur_interface">🎨 Arthur Interface</a>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 Async Orchestration</h3>
                <p>Parallel processing with up to 8 concurrent agents</p>
            </div>
            <div class="feature">
                <h3>🧠 Meta-Intelligence</h3>
                <p>Self-aware and self-improving AI system</p>
            </div>
            <div class="feature">
                <h3>🔥 Turbo Mode</h3>
                <p>8x performance boost for complex tasks</p>
            </div>
            <div class="feature">
                <h3>🎨 Auto-Generated UI</h3>
                <p>Personalized dashboards and controls</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health", response_model=SystemStatusResponse, tags=["Core Operations"])
async def health_check():
    """Enhanced health check with comprehensive system status"""
    start_time = time.time()
    
    orchestration_status = {}
    performance_metrics = {}
    
    if hephaestus_agent_instance:
        try:
            orchestration_status = hephaestus_agent_instance.get_async_orchestration_status()
            performance_metrics = {
                "meta_intelligence_cycles": getattr(hephaestus_agent_instance, 'meta_intelligence_cycles', 0),
                "objectives_processed": getattr(hephaestus_agent_instance, 'objectives_processed', 0),
                "avg_processing_time": getattr(hephaestus_agent_instance, 'avg_processing_time', 0),
                "system_efficiency": getattr(hephaestus_agent_instance, 'system_efficiency', 0)
            }
        except Exception as e:
            orchestration_status = {"error": str(e)}
            performance_metrics = {"error": str(e)}
    
    return SystemStatusResponse(
        status="healthy",
        timestamp=datetime.now(),
        uptime_seconds=int(time.time() - start_time),
        version="3.1.0",
        meta_intelligence_active=hephaestus_agent_instance.meta_intelligence_active if hephaestus_agent_instance else False,
        worker_thread_alive=hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False,
        queue_size=queue_manager._queue.qsize(),
        orchestration_status=orchestration_status,
        performance_metrics=performance_metrics
    )

@app.get("/status", tags=["Core Operations"])
async def get_status():
    """Get detailed system status including all subsystems and current cycle/goal info"""
    meta_intelligence_status = {}
    current_cycle_info = {}
    pipeline_metrics = {}
    if hephaestus_agent_instance:
        try:
            meta_intelligence_status = hephaestus_agent_instance.evolution_manager.get_evolution_report()
        except Exception as e:
            meta_intelligence_status = {"error": str(e)}
        # --- NOVO: Info detalhada do ciclo/objetivo atual ---
        try:
            state = hephaestus_agent_instance.state
            current_cycle_info = {
                "current_objective": state.current_objective,
                "current_phase": getattr(state, "current_phase", None),
                "strategy_key": state.strategy_key,
                "validation_result": state.validation_result,
                "is_self_modifying": state.is_self_modifying,
                "action_plan_summary": (state.action_plan_data or {}).get("analysis", None),
                "patches_to_apply": len(state.get_patches_to_apply()),
                "applied_files_report": state.applied_files_report,
            }
        except Exception as e:
            current_cycle_info = {"error": f"Failed to extract current cycle info: {e}"}
        
        # --- NOVO: Métricas do pipeline otimizado ---
        try:
            if hasattr(hephaestus_agent_instance, 'optimized_pipeline') and hephaestus_agent_instance.optimized_pipeline:
                pipeline_metrics = {
                    "enabled": True,
                    "metrics": hephaestus_agent_instance.optimized_pipeline.get_pipeline_metrics(),
                    "cache_stats": hephaestus_agent_instance.optimized_pipeline.get_cache_stats()
                }
            else:
                pipeline_metrics = {"enabled": False}
        except Exception as e:
            pipeline_metrics = {"error": str(e)}
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "queue_size": queue_manager._queue.qsize(),
            "worker_active": hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False,
            "evolution_active": hephaestus_agent_instance.meta_intelligence_active if hephaestus_agent_instance else False
        },
        "current_cycle": current_cycle_info,
        "meta_intelligence": meta_intelligence_status,
        "pipeline_metrics": pipeline_metrics,
        "performance_metrics": {
            "rate_limit_storage_size": len(rate_limit_storage),
            "active_connections": "dynamic",
            "memory_usage": "monitoring_enabled"
        }
    }

@app.post("/objectives", tags=["Core Operations"])
async def submit_objective(request: ObjectiveRequest, auth_user: dict = Depends(get_auth_user)):
    """Submit a new objective to the agent with priority and metadata"""
    try:
        # Enhanced objective with metadata
        enhanced_objective = {
            "objective": request.objective,
            "priority": request.priority,
            "metadata": request.metadata or {},
            "submitted_by": auth_user["user"],
            "submitted_at": datetime.now().isoformat()
        }
        
        queue_manager.put_objective(enhanced_objective)
        
        return {
            "status": "success",
            "message": f"Objective '{request.objective}' added to queue with priority {request.priority}",
            "objective_id": str(hash(request.objective)),
            "queue_position": queue_manager._queue.qsize(),
            "estimated_processing_time": queue_manager._queue.qsize() * 30  # Rough estimate
        }
    except Exception as e:
        logger.error(f"Error submitting objective: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/objectives/queue", tags=["Core Operations"])
async def get_queue_status(auth_user: dict = Depends(get_auth_user)):
    """Get current queue status and pending objectives"""
    try:
        return {
            "status": "success",
            "queue_size": queue_manager._queue.qsize(),
            "queue_empty": queue_manager._queue.empty(),
            "processing_active": hephaestus_worker_thread.is_alive() if hephaestus_worker_thread else False,
            "message": "📋 Queue status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ORCHESTRATION ENDPOINTS === #

@app.post("/orchestration/turbo-mode", tags=["Orchestration"])
async def enable_turbo_mode(auth_user: dict = Depends(get_auth_user)):
    """Enable turbo evolution mode with maximum parallelism"""
    try:
        if hephaestus_agent_instance:
            hephaestus_agent_instance.enable_turbo_evolution_mode()
            return {
                "status": "success",
                "message": "🔥 Turbo Evolution Mode Activated!",
                "concurrent_agents": hephaestus_agent_instance.async_orchestrator.max_concurrent_agents,
                "performance_multiplier": f"{hephaestus_agent_instance.async_orchestrator.max_concurrent_agents}x",
                "estimated_performance_gain": "800%",
                "activation_timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error enabling turbo mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orchestration/async-evolution", tags=["Orchestration"])
async def start_async_evolution(request: AsyncEvolutionRequest, auth_user: dict = Depends(get_auth_user)):
    """Start async evolution with parallel multi-agent orchestration"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Enable turbo mode if requested
        if request.enable_turbo:
            hephaestus_agent_instance.enable_turbo_evolution_mode()
        
        # Start async evolution
        start_time = time.time()
        evolution_results = await hephaestus_agent_instance.run_async_evolution_cycle(request.objective)
        execution_time = time.time() - start_time
        
        return {
            "status": "success",
            "message": f"🚀 Async Evolution Completed for: {request.objective}",
            "results": evolution_results,
            "execution_time": execution_time,
            "parallel_efficiency": evolution_results.get("parallel_efficiency", 0),
            "successful_tasks": evolution_results.get("successful_tasks", 0),
            "failed_tasks": evolution_results.get("failed_tasks", 0),
            "performance_metrics": {
                "turbo_mode_active": request.enable_turbo,
                "max_concurrent_agents": request.max_concurrent_agents,
                "timeout_seconds": request.timeout_seconds
            }
        }
    except Exception as e:
        logger.error(f"Error starting async evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestration/status", tags=["Orchestration"])
async def get_orchestration_status(auth_user: dict = Depends(get_auth_user)):
    """Get detailed async orchestration status"""
    try:
        if hephaestus_agent_instance:
            status = hephaestus_agent_instance.get_async_orchestration_status()
            return {
                "status": "success",
                "orchestration_status": status,
                "timestamp": datetime.now().isoformat(),
                "message": "📊 Orchestration status retrieved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting orchestration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === SWARM COMMUNICATION ENDPOINTS === #

@app.get("/swarm/status", tags=["Swarm Communication"])
async def get_swarm_status(auth_user: dict = Depends(get_auth_user)):
    """Get swarm communication and coordination status"""
    try:
        if hephaestus_agent_instance:
            status = hephaestus_agent_instance.get_swarm_communication_status()
            return {
                "status": "success",
                "swarm_status": status,
                "timestamp": datetime.now().isoformat(),
                "message": "🐝 Swarm status retrieved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting swarm status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/start-conversation", tags=["Swarm Communication"])
async def start_swarm_conversation(request: dict, auth_user: dict = Depends(get_auth_user)):
    """Start a conversation between agents"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        initiator = request.get("initiator")
        participants = request.get("participants", [])
        topic = request.get("topic")
        initial_message = request.get("initial_message")
        
        if not all([initiator, participants, topic, initial_message]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        conversation_id = await hephaestus_agent_instance.inter_agent_communication.start_conversation(
            initiator, participants, topic, initial_message
        )
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message": f"💬 Conversation started: {topic}",
            "participants": participants
        }
    except Exception as e:
        logger.error(f"Error starting swarm conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/coordinate-task", tags=["Swarm Communication"])
async def coordinate_swarm_task(request: dict, auth_user: dict = Depends(get_auth_user)):
    """Coordinate a complex task using swarm intelligence"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        task_description = request.get("task_description")
        required_capabilities = request.get("required_capabilities", [])
        
        if not task_description:
            raise HTTPException(status_code=400, detail="Task description required")
        
        result = await hephaestus_agent_instance.inter_agent_communication.coordinate_complex_task(
            task_description, required_capabilities
        )
        
        return {
            "status": "success",
            "coordination_result": result,
            "message": f"🎯 Task coordinated: {task_description}"
        }
    except Exception as e:
        logger.error(f"Error coordinating swarm task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/resolve-conflict", tags=["Swarm Communication"])
async def resolve_swarm_conflict(request: dict, auth_user: dict = Depends(get_auth_user)):
    """Resolve conflicts between agents using negotiation"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        problem = request.get("problem")
        conflicting_agents = request.get("conflicting_agents", [])
        
        if not all([problem, conflicting_agents]):
            raise HTTPException(status_code=400, detail="Problem and conflicting agents required")
        
        result = await hephaestus_agent_instance.inter_agent_communication.negotiate_solution(
            problem, conflicting_agents
        )
        
        return {
            "status": "success",
            "negotiation_result": result,
            "message": f"⚖️ Conflict resolution initiated: {problem}"
        }
    except Exception as e:
        logger.error(f"Error resolving swarm conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/collective-problem-solving", tags=["Swarm Communication"])
async def start_collective_problem_solving(request: dict, auth_user: dict = Depends(get_auth_user)):
    """Start collective problem solving session"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        problem = request.get("problem")
        agent_perspectives = request.get("agent_perspectives", {})
        
        if not problem:
            raise HTTPException(status_code=400, detail="Problem description required")
        
        result = await hephaestus_agent_instance.inter_agent_communication.collective_problem_solving(
            problem, agent_perspectives
        )
        
        return {
            "status": "success",
            "problem_solving_result": result,
            "message": f"🧠 Collective problem solving started: {problem}"
        }
    except Exception as e:
        logger.error(f"Error starting collective problem solving: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/knowledge-sharing", tags=["Swarm Communication"])
async def start_knowledge_sharing(request: dict, auth_user: dict = Depends(get_auth_user)):
    """Start knowledge sharing session between agents"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        topic = request.get("topic")
        knowledge_providers = request.get("knowledge_providers", [])
        
        if not all([topic, knowledge_providers]):
            raise HTTPException(status_code=400, detail="Topic and knowledge providers required")
        
        result = await hephaestus_agent_instance.inter_agent_communication.knowledge_sharing_session(
            topic, knowledge_providers
        )
        
        return {
            "status": "success",
            "knowledge_sharing_result": result,
            "message": f"📚 Knowledge sharing started: {topic}"
        }
    except Exception as e:
        logger.error(f"Error starting knowledge sharing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === META-INTELLIGENCE ENDPOINTS === #

@app.post("/meta-intelligence/deep-reflection", tags=["Meta-Intelligence"])
async def perform_deep_reflection(request: DeepReflectionRequest, auth_user: dict = Depends(get_auth_user)):
    """Perform deep self-reflection and introspection"""
    try:
        if hephaestus_agent_instance:
            reflection_results = hephaestus_agent_instance.perform_deep_self_reflection(request.focus_area)
            return {
                "status": "success",
                "message": f"🔍 Deep Self-Reflection Complete for: {request.focus_area}",
                "results": reflection_results,
                "insights_generated": len(reflection_results.get("new_insights", [])),
                "meta_awareness_score": reflection_results.get("meta_awareness", 0),
                "reflection_metadata": {
                    "depth_level": request.depth_level,
                    "include_performance_metrics": request.include_performance_metrics,
                    "focus_area": request.focus_area,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error performing deep reflection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meta-intelligence/status", tags=["Meta-Intelligence"])
async def get_comprehensive_meta_intelligence_status(auth_user: dict = Depends(get_auth_user)):
    """Get comprehensive meta-intelligence status"""
    try:
        if hephaestus_agent_instance:
            status = hephaestus_agent_instance.get_comprehensive_meta_intelligence_status()
            return {
                "status": "success",
                "comprehensive_status": status,
                "timestamp": datetime.now().isoformat(),
                "message": "🧠 Comprehensive meta-intelligence status retrieved"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting comprehensive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meta-intelligence/evolution-cycle", tags=["Meta-Intelligence"])
async def trigger_evolution_cycle(auth_user: dict = Depends(get_auth_user)):
    """Manually trigger a meta-intelligence evolution cycle"""
    try:
        if hephaestus_agent_instance:
            # Trigger evolution cycle
            evolution_results = hephaestus_agent_instance.evolution_manager.run_evolution_cycle()
            return {
                "status": "success",
                "message": "🔄 Evolution cycle triggered successfully",
                "results": evolution_results,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error triggering evolution cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === INTERFACE GENERATION ENDPOINTS === #

@app.post("/interface/generate", tags=["Interface Generation"])
async def generate_arthur_interface(request: InterfaceGenerationRequest, auth_user: dict = Depends(get_auth_user)):
    """Generate personalized interface for Arthur"""
    try:
        if not interface_generator or not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        # Get current system state
        system_state = {
            "meta_intelligence_active": hephaestus_agent_instance.meta_intelligence_active,
            "orchestration_status": hephaestus_agent_instance.get_async_orchestration_status(),
            "evolution_status": hephaestus_agent_instance.evolution_manager.get_evolution_report(),
            "self_awareness": hephaestus_agent_instance.get_self_awareness_report(),
            "user_preferences": request.user_preferences or {},
            "theme": request.theme,
            "layout": request.layout,
            "include_advanced_controls": request.include_advanced_controls
        }
        
        # Generate interface
        interface_data = interface_generator.generate_personalized_interface(system_state)
        
        # Save to file
        interface_file = interface_generator.save_interface_to_file(interface_data)
        
        return {
            "status": "success",
            "message": "🎨 Personalized interface generated for Arthur!",
            "interface_id": interface_data["interface_id"],
            "interface_file": interface_file,
            "elements_count": len(interface_data["elements"]),
            "generated_at": interface_data["generated_at"],
            "theme": request.theme,
            "layout": request.layout,
            "interface_preview": interface_data["interface_code"][:500] + "..." if len(interface_data["interface_code"]) > 500 else interface_data["interface_code"]
        }
    except Exception as e:
        logger.error(f"Error generating interface: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interface/arthur", response_class=HTMLResponse, tags=["Interface Generation"])
async def serve_arthur_interface():
    """Serve the latest generated interface for Arthur"""
    try:
        if not interface_generator or not hephaestus_agent_instance:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        # Get system state and generate interface
        system_state = {
            "meta_intelligence_active": hephaestus_agent_instance.meta_intelligence_active,
            "orchestration_status": hephaestus_agent_instance.get_async_orchestration_status(),
            "evolution_status": hephaestus_agent_instance.evolution_manager.get_evolution_report(),
            "timestamp": datetime.now().isoformat()
        }
        
        interface_data = interface_generator.generate_personalized_interface(system_state)
        
        # Return HTML directly
        return HTMLResponse(content=interface_data["interface_code"])
        
    except Exception as e:
        logger.error(f"Error serving interface: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interface/list", tags=["Interface Generation"])
async def list_generated_interfaces(auth_user: dict = Depends(get_auth_user)):
    """List all generated interfaces"""
    try:
        interfaces_dir = "generated_interfaces"
        if not os.path.exists(interfaces_dir):
            return {"status": "success", "interfaces": [], "message": "No interfaces generated yet"}
        
        interfaces = []
        for filename in os.listdir(interfaces_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(interfaces_dir, filename)
                stat = os.stat(filepath)
                interfaces.append({
                    "filename": filename,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size_bytes": stat.st_size,
                    "url": f"/interface/view/{filename}"
                })
        
        return {
            "status": "success",
            "interfaces": interfaces,
            "total_count": len(interfaces),
            "message": "📋 Interface list retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error listing interfaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === MONITORING ENDPOINTS === #

@app.get("/monitoring/metrics", tags=["Monitoring"])
async def get_system_metrics(auth_user: dict = Depends(get_auth_user)):
    """Get comprehensive system metrics"""
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "status": "healthy",
                "uptime_seconds": time.time(),
                "memory_usage": "monitoring_enabled",
                "cpu_usage": "monitoring_enabled"
            },
            "agent_metrics": {
                "objectives_processed": getattr(hephaestus_agent_instance, 'objectives_processed', 0),
                "meta_intelligence_cycles": getattr(hephaestus_agent_instance, 'meta_intelligence_cycles', 0),
                "evolution_cycles": getattr(hephaestus_agent_instance, 'evolution_cycles', 0),
                "self_reflection_count": getattr(hephaestus_agent_instance, 'self_reflection_count', 0)
            },
            "performance_metrics": {
                "avg_processing_time": getattr(hephaestus_agent_instance, 'avg_processing_time', 0),
                "system_efficiency": getattr(hephaestus_agent_instance, 'system_efficiency', 0),
                "turbo_mode_usage": getattr(hephaestus_agent_instance, 'turbo_mode_usage', 0)
            },
            "queue_metrics": {
                "current_size": queue_manager._queue.qsize(),
                "processing_rate": "dynamic",
                "avg_wait_time": "calculated"
            }
        }
        
        return {
            "status": "success",
            "metrics": metrics,
            "message": "📊 System metrics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/logs", tags=["Monitoring"])
async def get_recent_logs(limit: int = 50, auth_user: dict = Depends(get_auth_user)):
    """Get recent system logs"""
    try:
        # In a real implementation, you'd read from log files
        # For now, return a sample structure
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Sample log entry",
                "component": "hephaestus_agent"
            }
        ]
        
        return {
            "status": "success",
            "logs": logs[:limit],
            "total_entries": len(logs),
            "message": f"📋 Retrieved {min(limit, len(logs))} recent log entries"
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse, tags=["Monitoring"])
async def get_dashboard_page():
    """Serves the main evolution dashboard HTML page."""
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard HTML not found. Please ensure 'templates/dashboard.html' exists.")

@app.get("/api/dashboard-data", tags=["Monitoring"])
async def get_dashboard_data(auth_user: dict = Depends(get_auth_user)):
    """Provides real-time data for the evolution dashboard."""
    if hephaestus_agent_instance:
        return hephaestus_agent_instance.get_evolution_dashboard_data()
    else:
        raise HTTPException(status_code=503, detail="Agent not initialized")

# === CONFIGURATION ENDPOINTS === #

@app.post("/config/agent", tags=["Configuration"])
async def update_agent_config(request: AgentConfigRequest, auth_user: dict = Depends(get_auth_user)):
    """Update agent configuration and persist it"""
    try:
        if hephaestus_agent_instance:
            hephaestus_agent_instance.continuous_mode = request.continuous_mode
            
            # Persist the configuration to a file
            config_path = "hephaestus_config.json"
            current_config = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    current_config = json.load(f)
            
            current_config.update({
                "continuous_mode": request.continuous_mode,
                "max_objectives": request.max_objectives,
                "evolution_interval": request.evolution_interval
            })
            
            with open(config_path, "w") as f:
                json.dump(current_config, f, indent=4)

            logger.info(f"Updating agent configuration: {request.dict()}")
            
            return {
                "status": "success",
                "message": "⚙️ Agent configuration updated and saved successfully",
                "updated_config": request.dict(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error updating agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/current", tags=["Configuration"])
async def get_current_config(auth_user: dict = Depends(get_auth_user)):
    """Get current agent configuration"""
    try:
        if hephaestus_agent_instance:
            config = {
                "meta_intelligence_active": hephaestus_agent_instance.meta_intelligence_active,
                "continuous_mode": getattr(hephaestus_agent_instance, 'continuous_mode', False),
                "max_concurrent_agents": getattr(hephaestus_agent_instance.async_orchestrator, 'max_concurrent_agents', 4),
                "turbo_mode_active": getattr(hephaestus_agent_instance, 'turbo_mode_active', False),
                "evolution_interval": getattr(hephaestus_agent_instance, 'evolution_interval', 3600)
            }
            
            return {
                "status": "success",
                "config": config,
                "message": "⚙️ Current configuration retrieved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting current config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === LEGACY ENDPOINTS (for backwards compatibility) === #

@app.get("/api/orchestration_status", tags=["Legacy"])
async def legacy_orchestration_status():
    """Legacy endpoint for orchestration status"""
    return await get_orchestration_status()

@app.post("/api/enable_turbo_mode", tags=["Legacy"])
async def legacy_enable_turbo_mode():
    """Legacy endpoint for enabling turbo mode"""
    return await enable_turbo_mode()

@app.post("/api/start_async_evolution", tags=["Legacy"])
async def legacy_start_async_evolution(request: AsyncEvolutionRequest):
    """Legacy endpoint for async evolution"""
    return await start_async_evolution(request)

@app.get("/arthur_interface", response_class=HTMLResponse, tags=["Legacy"])
async def legacy_arthur_interface():
    """Legacy endpoint for Arthur interface"""
    return await serve_arthur_interface()

# === HOT RELOAD ENDPOINTS === #

@app.post("/hot-reload/enable", tags=["Hot Reload"])
async def enable_hot_reload(auth_user: dict = Depends(get_auth_user)):
    """Habilitar hot reload para evolução em tempo real"""
    try:
        if hephaestus_agent_instance:
            success = hephaestus_agent_instance.enable_real_time_evolution()
            return {
                "status": "success",
                "message": "🔄 Hot Reload enabled!" if success else "Hot Reload already active",
                "real_time_evolution": success,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error enabling hot reload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hot-reload/disable", tags=["Hot Reload"])
async def disable_hot_reload(auth_user: dict = Depends(get_auth_user)):
    """Desabilitar hot reload"""
    try:
        if hephaestus_agent_instance:
            success = hephaestus_agent_instance.disable_real_time_evolution()
            return {
                "status": "success",
                "message": "⏸️ Hot Reload disabled!" if success else "Hot Reload already inactive",
                "real_time_evolution": not success,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error disabling hot reload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hot-reload/status", tags=["Hot Reload"])
async def get_hot_reload_status(auth_user: dict = Depends(get_auth_user)):
    """Obter status do hot reload"""
    try:
        if hephaestus_agent_instance:
            status = hephaestus_agent_instance.get_real_time_evolution_status()
            return {
                "status": "success",
                "hot_reload_status": status,
                "timestamp": datetime.now().isoformat(),
                "message": "🔄 Hot reload status retrieved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting hot reload status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SelfModificationRequest(BaseModel):
    module_name: str = Field(..., description="Nome do módulo a ser modificado")
    new_code: str = Field(..., description="Novo código para o módulo")
    backup_enabled: bool = Field(True, description="Fazer backup antes da modificação")

@app.post("/hot-reload/self-modify", tags=["Hot Reload"])
async def self_modify_code(request: SelfModificationRequest, auth_user: dict = Depends(get_auth_user)):
    """Permitir que o sistema modifique seu próprio código"""
    try:
        if hephaestus_agent_instance:
            success = hephaestus_agent_instance.self_modify_code(
                request.module_name, 
                request.new_code
            )
            
            return {
                "status": "success" if success else "failed",
                "message": f"🧬 Self-modification {'completed' if success else 'failed'} for {request.module_name}",
                "module_name": request.module_name,
                "backup_enabled": request.backup_enabled,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error in self-modification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DynamicImportRequest(BaseModel):
    code: str = Field(..., description="Código Python para importar dinamicamente")
    module_name: Optional[str] = Field(None, description="Nome opcional para o módulo")

@app.post("/hot-reload/dynamic-import", tags=["Hot Reload"])
async def dynamic_import_code(request: DynamicImportRequest, auth_user: dict = Depends(get_auth_user)):
    """Importar código dinamicamente em tempo de execução"""
    try:
        if hephaestus_agent_instance:
            module = hephaestus_agent_instance.dynamic_import_code(
                request.code, 
                request.module_name
            )
            
            success = module is not None
            
            return {
                "status": "success" if success else "failed",
                "message": f"🔧 Dynamic import {'successful' if success else 'failed'}",
                "module_name": request.module_name or f"dynamic_module_{int(time.time())}",
                "module_created": success,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error in dynamic import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hot-reload/trigger-evolution", tags=["Hot Reload"])
async def trigger_self_evolution(auth_user: dict = Depends(get_auth_user)):
    """Disparar auto-evolução baseada em performance"""
    try:
        if hephaestus_agent_instance:
            success = hephaestus_agent_instance.trigger_self_evolution()
            
            return {
                "status": "success" if success else "failed",
                "message": f"🧬 Self-evolution {'completed' if success else 'failed'}",
                "evolution_triggered": success,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error triggering self-evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hot-reload/evolution-history", tags=["Hot Reload"])
async def get_evolution_history(limit: int = 20, auth_user: dict = Depends(get_auth_user)):
    """Obter histórico de evoluções em tempo real"""
    try:
        if hephaestus_agent_instance:
            status = hephaestus_agent_instance.get_real_time_evolution_status()
            evolution_history = status.get("hot_reload_status", {}).get("evolution_history", [])
            
            # Limitar resultados
            limited_history = evolution_history[-limit:] if evolution_history else []
            
            return {
                "status": "success",
                "evolution_history": limited_history,
                "total_evolutions": len(limited_history),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "message": "📚 Evolution history retrieved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error getting evolution history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS DO ORGANIZER AGENT =====

@app.get("/api/organizer/analyze-structure", tags=["Project Organization"])
async def analyze_project_structure(auth_user: dict = Depends(get_auth_user)):
    """Analisa a estrutura atual do projeto"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        result = await hephaestus_agent_instance.analyze_project_structure()
        return result
    except Exception as e:
        logger.error(f"Erro na análise da estrutura: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/organizer/generate-plan", tags=["Project Organization"])
async def generate_organization_plan(auth_user: dict = Depends(get_auth_user)):
    """Gera plano de reorganização do projeto"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        result = await hephaestus_agent_instance.generate_organization_plan()
        return result
    except Exception as e:
        logger.error(f"Erro na geração do plano: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/organizer/execute-plan", tags=["Project Organization"])
async def execute_organization_plan(
    dry_run: bool = Body(True, description="Se True, apenas simula a execução"),
    auth_user: dict = Depends(get_auth_user)
):
    """Executa o plano de reorganização"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        result = await hephaestus_agent_instance.execute_organization_plan(dry_run=dry_run)
        return result
    except Exception as e:
        logger.error(f"Erro na execução da reorganização: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/organizer/report", tags=["Project Organization"])
async def get_organization_report(auth_user: dict = Depends(get_auth_user)):
    """Gera relatório completo da organização"""
    try:
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        result = await hephaestus_agent_instance.get_organization_report()
        return result
    except Exception as e:
        logger.error(f"Erro na geração do relatório: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# === ERROR DETECTION ENDPOINTS === #

@app.get("/error-detector/status", tags=["Error Detection"])
async def get_error_detector_status(auth_user: dict = Depends(get_auth_user)):
    """Get current status of the error detector agent"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        status = error_detector_agent.get_monitoring_status()
        return {
            "status": "success",
            "error_detector": status,
            "message": "🛡️ Error detector status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting detector status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/error-detector/report", tags=["Error Detection"])
async def get_error_report(auth_user: dict = Depends(get_auth_user)):
    """Get detailed error analysis report"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        report = error_detector_agent.get_error_report()
        return {
            "status": "success",
            "error_report": report,
            "message": "📊 Error analysis report generated"
        }
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/error-detector/inject-test-error", tags=["Error Detection"])
async def inject_test_error(
    error_message: str = Body(..., description="Error message to inject for testing"),
    auth_user: dict = Depends(get_auth_user)
):
    """Inject a test error for testing the error detection system"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        result = error_detector_agent.inject_error_for_testing(error_message)
        return {
            "status": "success",
            "test_result": result,
            "message": f"🧪 Test error injected and processed"
        }
    except Exception as e:
        logger.error(f"Error injecting test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/error-detector/start", tags=["Error Detection"])
async def start_error_monitoring(auth_user: dict = Depends(get_auth_user)):
    """Start error monitoring"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        if error_detector_agent.start_monitoring():
            return {
                "status": "success",
                "message": "🛡️ Error monitoring started"
            }
        else:
            return {
                "status": "info",
                "message": "🛡️ Error monitoring was already active"
            }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/error-detector/stop", tags=["Error Detection"])
async def stop_error_monitoring(auth_user: dict = Depends(get_auth_user)):
    """Stop error monitoring"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        if error_detector_agent.stop_monitoring():
            return {
                "status": "success",
                "message": "🛡️ Error monitoring stopped"
            }
        else:
            return {
                "status": "info", 
                "message": "🛡️ Error monitoring was not active"
            }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/error-detector/real-time-analysis", tags=["Error Detection"])
async def get_real_time_analysis(auth_user: dict = Depends(get_auth_user)):
    """Get real-time analysis of system errors and health"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        analysis = error_detector_agent.get_real_time_analysis()
        return {
            "status": "success",
            "real_time_analysis": analysis,
            "message": "⚡ Real-time error analysis completed"
        }
    except Exception as e:
        logger.error(f"Error in real-time analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/error-detector/capture-agent-error", tags=["Error Detection"])
async def capture_agent_error(
    agent_name: str = Body(..., description="Name of the agent that generated the error"),
    error_message: str = Body(..., description="Error message from the agent"),
    context: Optional[Dict[str, Any]] = Body(None, description="Additional error context"),
    auth_user: dict = Depends(get_auth_user)
):
    """Capture and analyze an error from a specific agent"""
    try:
        if not error_detector_agent:
            raise HTTPException(status_code=503, detail="Error detector not initialized")
        
        result = error_detector_agent.capture_agent_error(agent_name, error_message, context)
        return {
            "status": "success",
            "error_analysis": result,
            "message": f"🛡️ Agent error captured and analyzed for {agent_name}"
        }
    except Exception as e:
        logger.error(f"Error capturing agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === BUG HUNTER ENDPOINTS === #

@app.post("/bug-hunter/start", tags=["Bug Hunter"])
async def start_bug_hunter(auth_user: dict = Depends(get_auth_user)):
    """Start bug hunting monitoring"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'bug_hunter'):
            success = hephaestus_agent_instance.bug_hunter.start_monitoring()
            return {
                "status": "success" if success else "already_running",
                "message": "Bug Hunter monitoring started" if success else "Bug Hunter already running"
            }
        else:
            raise HTTPException(status_code=503, detail="Bug Hunter Agent not available")
    except Exception as e:
        logger.error(f"Error starting bug hunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bug-hunter/stop", tags=["Bug Hunter"])
async def stop_bug_hunter(auth_user: dict = Depends(get_auth_user)):
    """Stop bug hunting monitoring"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'bug_hunter'):
            success = hephaestus_agent_instance.bug_hunter.stop_monitoring()
            return {
                "status": "success" if success else "not_running",
                "message": "Bug Hunter monitoring stopped" if success else "Bug Hunter not running"
            }
        else:
            raise HTTPException(status_code=503, detail="Bug Hunter Agent not available")
    except Exception as e:
        logger.error(f"Error stopping bug hunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bug-hunter/status", tags=["Bug Hunter"])
async def get_bug_hunter_status(auth_user: dict = Depends(get_auth_user)):
    """Get bug hunter status and report"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'bug_hunter'):
            report = hephaestus_agent_instance.bug_hunter.get_bug_report()
            priority_bugs = hephaestus_agent_instance.bug_hunter.get_priority_bugs()
            
            return {
                "status": "success",
                "bug_hunter_status": report,
                "priority_bugs": [
                    {
                        "id": bug.bug_id,
                        "type": bug.bug_type,
                        "severity": bug.severity,
                        "file": bug.file_path,
                        "description": bug.description,
                        "confidence": bug.confidence
                    }
                    for bug in priority_bugs
                ]
            }
        else:
            raise HTTPException(status_code=503, detail="Bug Hunter Agent not available")
    except Exception as e:
        logger.error(f"Error getting bug hunter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bug-hunter/scan", tags=["Bug Hunter"])
async def trigger_bug_scan(auth_user: dict = Depends(get_auth_user)):
    """Trigger immediate bug scan"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'bug_hunter'):
            bugs_found = hephaestus_agent_instance.bug_hunter.scan_for_bugs()
            return {
                "status": "success",
                "bugs_found": len(bugs_found),
                "scan_completed": True,
                "message": f"Bug scan completed: {len(bugs_found)} bugs found"
            }
        else:
            raise HTTPException(status_code=503, detail="Bug Hunter Agent not available")
    except Exception as e:
        logger.error(f"Error triggering bug scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add custom exception handler to capture all API errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that reports errors to the detector"""
    error_message = str(exc)
    error_context = {
        "source": "api_request",
        "path": str(request.url.path),
        "method": request.method,
        "timestamp": datetime.now().isoformat()
    }
    
    # Report to error detector
    if error_detector_agent:
        try:
            error_detector_agent.process_error(error_message, error_context)
        except Exception as detector_error:
            logger.error(f"Error detector failed: {detector_error}")
    
    # Log the error
    logger.error(f"API Error on {request.method} {request.url.path}: {error_message}")
    
    # Return appropriate error response
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": error_message,
            "timestamp": datetime.now().isoformat()
        }
    )

# Modify the worker function to capture errors automatically
def worker():
    try:
        if hephaestus_agent_instance:
            hephaestus_agent_instance.run_continuous()
    except Exception as e:
        logger.error(f"Worker thread error: {e}")
        # Report error to detector with enhanced context
        if error_detector_agent:
            try:
                error_detector_agent.capture_agent_error(
                    "HephaestusAgent", 
                    str(e), 
                    {
                        "source": "worker_thread",
                        "thread_name": "HephaestusWorker",
                        "error_type": "runtime_exception"
                    }
                )
            except Exception as detector_error:
                logger.error(f"Error detector failed: {detector_error}")

@app.post("/api/activate-maximum-evolution", tags=["Evolution"])
async def activate_maximum_evolution(auth_user: dict = Depends(get_auth_user)):
    """Ativa o modo de evolução máxima para desenvolvimento autônomo"""
    try:
        global hephaestus_agent_instance
        
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        # Configurar modo de evolução máxima
        hephaestus_agent_instance.continuous_mode = True
        hephaestus_agent_instance.evolution_mode = "maximum"
        hephaestus_agent_instance.max_evolution_cycles = 100  # Muitos ciclos
        hephaestus_agent_instance.evolution_interval = 30  # Ciclos rápidos
        
        # Ativar todos os sistemas de evolução
        if hasattr(hephaestus_agent_instance, 'meta_intelligence'):
            hephaestus_agent_instance.meta_intelligence.active = True
            hephaestus_agent_instance.meta_intelligence.evolution_mode = "aggressive"
        
        # Ativar monitor de performance
        if hasattr(hephaestus_agent_instance, 'performance_monitor'):
            hephaestus_agent_instance.performance_monitor.start_monitoring()
        
        # Configurar objetivos de evolução
        evolution_objectives = [
            "Implementar sistema de auto-aprimoramento completo",
            "Desenvolver planejamento estratégico avançado",
            "Criar gerador tático inteligente",
            "Implementar integração de conhecimento externo",
            "Otimizar algoritmos de seleção de estratégias",
            "Desenvolver sistema de criação automática de agentes",
            "Implementar análise de causas raiz avançada",
            "Criar sistema de otimização de prompts genético",
            "Desenvolver capacidades de auto-modificação",
            "Implementar arquitetura de agentes dinâmica"
        ]
        
        # Adicionar objetivos à fila
        for objective in evolution_objectives:
            if hasattr(hephaestus_agent_instance, 'queue_manager'):
                hephaestus_agent_instance.queue_manager.add_objective(objective)
        
        logger.info("🚀 MODO DE EVOLUÇÃO MÁXIMA ATIVADO!")
        logger.info("🧠 Sistema configurado para evolução autônoma durante a noite")
        logger.info(f"📋 {len(evolution_objectives)} objetivos de evolução adicionados")
        
        return {
            "status": "success",
            "message": "🚀 Modo de evolução máxima ativado!",
            "evolution_mode": "maximum",
            "continuous_mode": True,
            "objectives_queued": len(evolution_objectives),
            "evolution_cycles": 100,
            "cycle_interval": 30,
            "estimated_completion": "8-12 hours",
            "features_to_evolve": evolution_objectives
        }
        
    except Exception as e:
        logger.error(f"Error activating maximum evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/protected-processes", tags=["System"])
async def get_protected_processes(auth_user: dict = Depends(get_auth_user)):
    """Lista processos protegidos que não serão mortos pelo CycleMonitorAgent"""
    try:
        global cycle_monitor_agent
        
        if not cycle_monitor_agent:
            raise HTTPException(status_code=503, detail="Cycle monitor agent not initialized")
        
        return {
            "protected_processes": cycle_monitor_agent.protected_processes,
            "total_protected": len(cycle_monitor_agent.protected_processes)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter processos protegidos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/protected-processes", tags=["System"])
async def add_protected_process(process_name: str, auth_user: dict = Depends(get_auth_user)):
    """Adiciona um processo à lista de protegidos"""
    try:
        global cycle_monitor_agent
        
        if not cycle_monitor_agent:
            raise HTTPException(status_code=503, detail="Cycle monitor agent not initialized")
        
        if process_name.lower() not in cycle_monitor_agent.protected_processes:
            cycle_monitor_agent.protected_processes.append(process_name.lower())
            logger.info(f"✅ Processo '{process_name}' adicionado à lista de protegidos")
        
        return {
            "success": True,
            "message": f"Processo '{process_name}' protegido",
            "protected_processes": cycle_monitor_agent.protected_processes
        }
        
    except Exception as e:
        logger.error(f"Erro ao adicionar processo protegido: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/activate-features", tags=["System"])
async def activate_system_features(auth_user: dict = Depends(get_auth_user)):
    """Ativa funcionalidades não utilizadas do sistema"""
    try:
        global hephaestus_agent_instance
        
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        # Ativar funcionalidades através do system activator
        from agent.system_activator import get_system_activator
        activator = get_system_activator(logger, hephaestus_agent_instance.config)
        results = activator.activate_all_features()
        
        # Gerar relatório
        report = activator.get_activation_report()
        active_features = activator.get_active_features()
        
        return {
            "success": True,
            "message": "Funcionalidades ativadas com sucesso",
            "activated_features": active_features,
            "total_activated": len(active_features),
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Erro ao ativar funcionalidades: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/start-night-evolution", tags=["Evolution"])
async def start_night_evolution(auth_user: dict = Depends(get_auth_user)):
    """Inicia evolução noturna autônoma para desenvolvimento contínuo"""
    try:
        global hephaestus_agent_instance
        
        if not hephaestus_agent_instance:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
        
        # Configurar para evolução noturna
        hephaestus_agent_instance.continuous_mode = True
        hephaestus_agent_instance.night_mode = True
        hephaestus_agent_instance.evolution_aggressiveness = "maximum"
        
        # Configurar intervalos otimizados para evolução noturna
        hephaestus_agent_instance.evolution_interval = 60  # 1 minuto entre ciclos
        hephaestus_agent_instance.max_evolution_cycles = 200  # Muitos ciclos
        hephaestus_agent_instance.auto_restart = True  # Reiniciar se falhar
        
        # Ativar todos os sistemas
        systems_to_activate = [
            "meta_intelligence",
            "performance_monitor", 
            "error_detector",
            "knowledge_system",
            "model_optimizer",
            "cognitive_evolution"
        ]
        
        activated_systems = []
        for system_name in systems_to_activate:
            if hasattr(hephaestus_agent_instance, system_name):
                system = getattr(hephaestus_agent_instance, system_name)
                if hasattr(system, 'start_monitoring'):
                    system.start_monitoring()
                if hasattr(system, 'activate'):
                    system.activate()
                activated_systems.append(system_name)
        
        logger.info("🌙 EVOLUÇÃO NOTURNA INICIADA!")
        logger.info("🧠 Sistema configurado para evolução autônoma durante a noite")
        logger.info(f"⚙️ Sistemas ativados: {', '.join(activated_systems)}")
        
        return {
            "status": "success",
            "message": "🌙 Evolução noturna iniciada!",
            "night_mode": True,
            "continuous_mode": True,
            "evolution_aggressiveness": "maximum",
            "cycle_interval": 60,
            "max_cycles": 200,
            "auto_restart": True,
            "activated_systems": activated_systems,
            "estimated_evolution_time": "8-12 hours",
            "expected_improvements": [
                "Auto-aprimoramento completo",
                "Planejamento estratégico avançado",
                "Gerador tático inteligente",
                "Integração de conhecimento externo",
                "Otimização de algoritmos",
                "Criação automática de agentes",
                "Análise de causas raiz avançada",
                "Otimização de prompts genético",
                "Auto-modificação de código",
                "Arquitetura de agentes dinâmica"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error starting night evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dependency-fixer/analyze", tags=["Dependency Fixer"])
async def analyze_dependencies(
    error_logs: str = Body(..., description="Error logs to analyze for import issues"),
    auth_user: dict = Depends(get_auth_user)
):
    """Analyze and fix import/dependency issues"""
    try:
        global dependency_fixer_agent
        
        if not dependency_fixer_agent:
            raise HTTPException(status_code=503, detail="Dependency Fixer Agent not initialized")
        
        # Run dependency analysis
        result = dependency_fixer_agent.run_analysis(error_logs)
        
        return {
            "status": "success",
            "message": f"Found {result['issues_found']} issues, applied {result['fixes_applied']} fixes",
            "analysis_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in dependency analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze dependencies: {str(e)}")

@app.get("/dependency-fixer/status", tags=["Dependency Fixer"])
async def get_dependency_fixer_status(auth_user: dict = Depends(get_auth_user)):
    """Get Dependency Fixer Agent status"""
    try:
        global dependency_fixer_agent
        
        if not dependency_fixer_agent:
            raise HTTPException(status_code=503, detail="Dependency Fixer Agent not initialized")
        
        return {
            "status": "active",
            "agent_type": "DependencyFixerAgent",
            "capabilities": [
                "import_error_detection",
                "missing_class_fixing", 
                "missing_module_creation",
                "automatic_code_generation"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting dependency fixer status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/cycle-monitor/status", tags=["Cycle Monitor"])
async def get_cycle_monitor_status(auth_user: dict = Depends(get_auth_user)):
    """Get cycle monitor status and system health"""
    try:
        global cycle_monitor_agent
        
        if not cycle_monitor_agent:
            raise HTTPException(status_code=503, detail="Cycle Monitor Agent not initialized")
        
        status = cycle_monitor_agent.get_system_status()
        
        return {
            "status": "success",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting cycle monitor status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cycle-monitor/force-cleanup", tags=["Cycle Monitor"])
async def force_cycle_cleanup(auth_user: dict = Depends(get_auth_user)):
    """Force immediate cleanup of all detected issues"""
    try:
        global cycle_monitor_agent
        
        if not cycle_monitor_agent:
            raise HTTPException(status_code=503, detail="Cycle Monitor Agent not initialized")
        
        cleanup_result = cycle_monitor_agent.force_cleanup()
        
        return {
            "status": "success",
            "message": "Forced cleanup completed",
            "data": cleanup_result
        }
        
    except Exception as e:
        logger.error(f"Error during forced cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === AGENT EXPANSION COORDINATOR ENDPOINTS === #

@app.get("/agent-expansion/status", tags=["Agent Expansion"])
async def get_agent_expansion_status(auth_user: dict = Depends(get_auth_user)):
    """Get status of agent expansion coordination"""
    try:
        global agent_expansion_coordinator
        
        if not agent_expansion_coordinator:
            raise HTTPException(status_code=503, detail="Agent Expansion Coordinator not initialized")
        
        status = agent_expansion_coordinator.get_expansion_status()
        
        return {
            "status": "success",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting agent expansion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-expansion/analysis", tags=["Agent Expansion"])
async def get_agent_utilization_analysis(auth_user: dict = Depends(get_auth_user)):
    """Get detailed analysis of agent utilization"""
    try:
        global agent_expansion_coordinator
        
        if not agent_expansion_coordinator:
            raise HTTPException(status_code=503, detail="Agent Expansion Coordinator not initialized")
        
        analysis = agent_expansion_coordinator.analyze_agent_utilization()
        
        return {
            "status": "success",
            "data": analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting utilization analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-expansion/plan", tags=["Agent Expansion"])
async def get_agent_activation_plan(auth_user: dict = Depends(get_auth_user)):
    """Get plan for activating underutilized agents"""
    try:
        global agent_expansion_coordinator
        
        if not agent_expansion_coordinator:
            raise HTTPException(status_code=503, detail="Agent Expansion Coordinator not initialized")
        
        plan = agent_expansion_coordinator.create_agent_activation_plan()
        
        return {
            "status": "success",
            "data": plan
        }
        
    except Exception as e:
        logger.error(f"Error getting activation plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-expansion/objectives", tags=["Agent Expansion"])
async def get_agent_objectives(auth_user: dict = Depends(get_auth_user)):
    """Get objectives for underutilized agents"""
    try:
        global agent_expansion_coordinator
        
        if not agent_expansion_coordinator:
            raise HTTPException(status_code=503, detail="Agent Expansion Coordinator not initialized")
        
        objectives = agent_expansion_coordinator.generate_agent_objectives()
        
        return {
            "status": "success",
            "data": objectives
        }
        
    except Exception as e:
        logger.error(f"Error getting agent objectives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-expansion/activate", tags=["Agent Expansion"])
async def activate_underutilized_agents(auth_user: dict = Depends(get_auth_user)):
    """Ativa agentes subutilizados com objetivos específicos"""
    try:
        if hephaestus_agent_instance:
            # Add objectives for all agents to ensure they're active
            all_agents_objectives = [
                "Procurar e documentar technical debt no projeto atual",
                "Analisar performance e otimizar chamadas LLM",
                "Revisar código e identificar melhorias",
                "Detectar e corrigir bugs automaticamente",
                "Monitorar e resolver ciclos travados",
                "Otimizar prompts e estratégias de agentes",
                "Coordenar comunicação entre agentes",
                "Analisar logs e identificar padrões",
                "Gerenciar conhecimento e aprendizado",
                "Planejar estratégias de evolução",
                "Detectar gaps de capacidade",
                "Otimizar arquitetura do sistema",
                "Gerenciar meta-cognição e auto-reflexão",
                "Integrar componentes e funcionalidades",
                "Analisar performance do sistema",
                "Detectar e corrigir erros automaticamente",
                "Otimizar experiência do usuário",
                "Gerenciar validação e testes",
                "Organizar estrutura do projeto",
                "Coordenar swarm de agentes",
                "Gerenciar aprendizado contínuo",
                "Planejar evolução estratégica"
            ]
            
            for objective in all_agents_objectives:
                hephaestus_agent_instance.queue_manager.put_objective({
                    "objective": objective,
                    "priority": 3,
                    "is_agent_activation": True
                })
            
            return {
                "status": "success",
                "message": f"🚀 Todos os 22 agentes ativados com objetivos específicos!",
                "objectives_added": len(all_agents_objectives),
                "total_agents": 22,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error activating all agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/activate-all-agents", tags=["Agent Management"])
async def activate_all_agents_in_main_cycle(auth_user: dict = Depends(get_auth_user)):
    """Ativa todos os agentes no ciclo principal automaticamente"""
    try:
        if hephaestus_agent_instance:
            # Add a high-priority objective to activate all agents in swarm mode
            activation_objective = """
            **ATIVAÇÃO COMPLETA DE TODOS OS AGENTES**
            
            Objetivo: Ativar todos os 22 agentes disponíveis no ciclo principal para maximizar o potencial do sistema.
            
            Agentes a serem ativados:
            1. Architect Agent - Planejamento arquitetural
            2. Maestro Agent - Orquestração principal
            3. Code Review Agent - Revisão de código
            4. Bug Hunter Agent - Detecção de bugs
            5. Debt Hunter Agent - Detecção de technical debt
            6. Error Analyzer Agent - Análise de erros
            7. Error Correction Agent - Correção automática
            8. Error Detector Agent - Detecção de erros
            9. Frontend Artisan Agent - Melhorias de UI/UX
            10. Integrator Agent - Integração de componentes
            11. Linter Agent - Análise de qualidade
            12. Log Analysis Agent - Análise de logs
            13. Model Sommelier Agent - Otimização de modelos
            14. Organizer Agent - Organização do projeto
            15. Performance Analyzer Agent - Análise de performance
            16. Prompt Optimizer Agent - Otimização de prompts
            17. Self Reflection Agent - Auto-reflexão
            18. Swarm Coordinator Agent - Coordenação de swarm
            19. Capability Gap Detector Agent - Detecção de gaps
            20. Learning Strategist Agent - Estratégias de aprendizado
            21. Meta Cognitive Controller Agent - Controle meta-cognitivo
            22. Strategic Planner Agent - Planejamento estratégico
            
            Ação: Distribuir tarefas específicas para cada agente e garantir que todos estejam ativos no ciclo principal.
            """
            
            hephaestus_agent_instance.queue_manager.put_objective({
                "objective": activation_objective,
                "priority": 1,
                "is_agent_activation": True
            })
            
            return {
                "status": "success",
                "message": "🚀 Todos os 22 agentes serão ativados no ciclo principal!",
                "total_agents": 22,
                "activation_objective_added": True,
                "priority": 1,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Agent not initialized")
    except Exception as e:
        logger.error(f"Error activating all agents in main cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def get_system_health():
    """Endpoint para verificar a saúde do sistema"""
    try:
        # Obter relatório de saúde do agente
        health_report = hephaestus_agent_instance.get_system_health_report()
        
        return {
            "status": "success",
            "health": health_report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/detailed")
async def get_detailed_health():
    """Endpoint para relatório detalhado de saúde"""
    try:
        # Relatório de prevenção de erros
        error_report = hephaestus_agent_instance.error_prevention.generate_error_report()
        
        # Relatório de monitoramento
        monitoring_report = hephaestus_agent_instance.continuous_monitor.generate_monitoring_report()
        
        return {
            "status": "success",
            "error_prevention_report": error_report,
            "monitoring_report": monitoring_report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# === AUTONOMOUS MONITOR ENDPOINTS === #

@app.get("/autonomous-monitor/status", tags=["Autonomous Monitor"])
async def get_autonomous_monitor_status(auth_user: dict = Depends(get_auth_user)):
    """Get autonomous monitor status and current issues"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'autonomous_monitor'):
            status = hephaestus_agent_instance.get_autonomous_monitor_status()
            return {
                "status": "success",
                "data": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Autonomous monitor not initialized")
    except Exception as e:
        logger.error(f"Error getting autonomous monitor status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/autonomous-monitor/issues", tags=["Autonomous Monitor"])
async def get_autonomous_monitor_issues(auth_user: dict = Depends(get_auth_user)):
    """Get current issues detected by autonomous monitor"""
    try:
        if hephaestus_agent_instance and hasattr(hephaestus_agent_instance, 'autonomous_monitor'):
            issues = hephaestus_agent_instance.autonomous_monitor.get_current_issues()
            return {
                "status": "success",
                "data": issues,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Autonomous monitor not initialized")
    except Exception as e:
        logger.error(f"Error getting autonomous monitor issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-monitor/start", tags=["Autonomous Monitor"])
async def start_autonomous_monitoring(auth_user: dict = Depends(get_auth_user)):
    """Start autonomous monitoring system"""
    try:
        if hephaestus_agent_instance:
            await hephaestus_agent_instance.start_autonomous_monitoring()
            return {
                "status": "success",
                "message": "🚀 Autonomous monitoring started successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
    except Exception as e:
        logger.error(f"Error starting autonomous monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-monitor/stop", tags=["Autonomous Monitor"])
async def stop_autonomous_monitoring(auth_user: dict = Depends(get_auth_user)):
    """Stop autonomous monitoring system"""
    try:
        if hephaestus_agent_instance:
            await hephaestus_agent_instance.stop_autonomous_monitoring()
            return {
                "status": "success",
                "message": "🛑 Autonomous monitoring stopped successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
    except Exception as e:
        logger.error(f"Error stopping autonomous monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/autonomous-monitor/prevention-report", tags=["Autonomous Monitor"])
async def get_prevention_report(auth_user: dict = Depends(get_auth_user)):
    """Get error prevention and monitoring report"""
    try:
        if hephaestus_agent_instance:
            # Relatório de prevenção de erros
            error_report = hephaestus_agent_instance.error_prevention.generate_error_report()
            
            # Relatório de monitoramento
            monitoring_report = hephaestus_agent_instance.continuous_monitor.generate_monitoring_report()
            
            return {
                "status": "success",
                "error_prevention_report": error_report,
                "monitoring_report": monitoring_report,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Hephaestus agent not initialized")
    except Exception as e:
        logger.error(f"Error getting prevention report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "tools.app:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
