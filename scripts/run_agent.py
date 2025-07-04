import argparse
import json
import logging
import sys
from dotenv import load_dotenv

from agent.hephaestus_agent import HephaestusAgent
from agent.config_loader import load_config

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/hephaestus.log", mode='w')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

agent_logger = logging.getLogger("HephaestusAgent")

load_dotenv()

parser = argparse.ArgumentParser(description="Hephaestus Agent: Autonomous AI for code evolution.")
parser.add_argument(
    "-c", "--continuous-mode",
    action="store_true",
    help="Enable continuous mode, where the agent generates new objectives indefinitely."
)
parser.add_argument(
    "--max-cycles",
    type=int,
    default=None,
    help="Maximum number of evolution cycles to run (for testing or controlled runs). Default: None (runs indefinitely or until stack empty if not continuous)."
)
args = parser.parse_args()

config = load_config()
agent = HephaestusAgent(
    logger_instance=agent_logger,
    config=config,
    continuous_mode=args.continuous_mode,
    objective_stack_depth_for_testing=args.max_cycles,
)
agent.run()
