import typer
from dotenv import load_dotenv
from hephaestus.core.agent import HephaestusAgent
import logging
from hephaestus.utils.config_loader import load_config

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def run(
    continuous: bool = typer.Option(False, "--continuous", "-c", help="Run in continuous mode"),
    max_cycles: int = typer.Option(None, "--max-cycles", "-m", help="Maximum number of evolution cycles")
):
    """Run the Hephaestus agent"""
    config = load_config()
    agent = HephaestusAgent(
        logger_instance=logger,
        config=config,
        continuous_mode=continuous,
        objective_stack_depth_for_testing=max_cycles
    )
    agent.run()

@app.command()
def submit(objective: str):
    """Submit a new objective to the agent"""
    # Implementation will be added after we refactor the agent to support this
    typer.echo(f"Objective submitted: {objective}")
    typer.echo("This functionality will be implemented in the next version")

@app.command()
def status():
    """Check agent status"""
    # Implementation will be added after we refactor the agent to support this
    typer.echo("Agent status: Running")
    typer.echo("This functionality will be implemented in the next version")

if __name__ == "__main__":
    app()
