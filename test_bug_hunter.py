#!/usr/bin/env python3
"""
Script de teste para o Bug Hunter Agent (paralelo)
"""

import logging
import sys
import asyncio
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agent.agents.bug_hunter_agent import BugHunterAgent
from agent.config_loader import load_config

def setup_logging():
    """Configura logging para o teste"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bug_hunter_test.log')
        ]
    )
    return logging.getLogger(__name__)

async def run_bug_scan(agent_id, model_config, config, logger):
    logger = logger.getChild(f"Agent{agent_id}")
    bug_hunter = BugHunterAgent(model_config, config, logger)
    logger.info(f"[Agent {agent_id}] Iniciando scan de bugs...")
    bugs = bug_hunter.scan_for_bugs()
    logger.info(f"[Agent {agent_id}] Bugs encontrados: {len(bugs)}")
    return len(bugs)

async def main():
    """Função principal do teste"""
    logger = setup_logging()
    logger.info("🔍 Iniciando teste paralelo do Bug Hunter Agent...")
    config = load_config()
    model_config = config.get("models", {})

    num_agents = 3  # Simular 3 agentes em paralelo
    start = time.time()
    results = await asyncio.gather(*[
        run_bug_scan(i+1, model_config, config, logger)
        for i in range(num_agents)
    ])
    elapsed = time.time() - start
    logger.info(f"⏱️ Tempo total para {num_agents} scans paralelos: {elapsed:.2f}s")
    for i, bugs in enumerate(results, 1):
        logger.info(f"[Agent {i}] Bugs encontrados: {bugs}")
    logger.info("✅ Teste paralelo concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 