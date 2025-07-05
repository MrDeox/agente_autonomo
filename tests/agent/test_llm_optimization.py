import unittest
from unittest.mock import MagicMock, patch
import logging

from agent.agents.code_review_agent import CodeReviewAgent
from agent.agents.maestro_agent import MaestroAgent, StrategyCache


class TestCodeReviewOptimization(unittest.TestCase):
    """Testa otimizações do CodeReviewAgent"""
    
    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)
        self.model_config = {"primary": "test_model"}
        self.agent = CodeReviewAgent(self.model_config, self.logger)
    
    def test_needs_review_trivial_patches(self):
        """Testa que patches triviais não precisam de revisão"""
        trivial_patches = [
            {"content": "import os", "operation": "INSERT"},
            {"content": "from typing import List", "operation": "INSERT"},
            {"content": "# This is a comment", "operation": "INSERT"},
            {"content": "    pass", "operation": "INSERT"},
        ]
        
        self.assertFalse(self.agent.needs_review(trivial_patches))
        self.logger.info.assert_called_with("All 4 patches are trivial - skipping LLM review")
    
    def test_needs_review_critical_patterns(self):
        """Testa que padrões críticos sempre precisam de revisão"""
        critical_patches = [
            {"content": "exec('dangerous code')", "operation": "INSERT"},
            {"content": "result = eval(user_input)", "operation": "INSERT"},
            {"content": "subprocess.run(['rm', '-rf', '/'])", "operation": "INSERT"},
        ]
        
        for patch in critical_patches:
            self.assertTrue(self.agent.needs_review([patch]))
    
    def test_needs_review_delete_operations(self):
        """Testa que operações DELETE sempre precisam de revisão"""
        delete_patch = [{"content": "def old_function():\n    pass", "operation": "DELETE_BLOCK"}]
        
        self.assertTrue(self.agent.needs_review(delete_patch))
        self.logger.debug.assert_called_with("Patch contains DELETE operation - needs review")
    
    def test_needs_review_mixed_patches(self):
        """Testa comportamento com patches mistos"""
        mixed_patches = [
            {"content": "import os", "operation": "INSERT"},  # Trivial
            {"content": "def complex_function():\n    return calculate_value()", "operation": "INSERT"},  # Non-trivial
        ]
        
        self.assertTrue(self.agent.needs_review(mixed_patches))
    
    @patch('agent.utils.llm_client.call_llm_api')
    def test_review_patches_skip_trivial(self, mock_llm):
        """Testa que revisão é pulada para patches triviais"""
        trivial_patches = [{"content": "import os", "operation": "INSERT"}]
        
        passed, feedback = self.agent.review_patches(trivial_patches)
        
        self.assertTrue(passed)
        self.assertEqual(feedback, "Patches are trivial - auto-approved without LLM review.")
        mock_llm.assert_not_called()


class TestMaestroCache(unittest.TestCase):
    """Testa sistema de cache do MaestroAgent"""
    
    def setUp(self):
        self.cache = StrategyCache(maxsize=3, ttl_seconds=60)
    
    def test_cache_basic_operations(self):
        """Testa operações básicas do cache"""
        action_plan = {
            "patches_to_apply": [
                {"file_path": "test.py", "operation": "INSERT"}
            ]
        }
        
        # Cache miss
        self.assertIsNone(self.cache.get(action_plan))
        self.assertEqual(self.cache.misses, 1)
        self.assertEqual(self.cache.hits, 0)
        
        # Add to cache
        self.cache.put(action_plan, "memory", "TEST_STRATEGY")
        
        # Cache hit - precisa passar o mesmo memory_summary
        strategy = self.cache.get(action_plan, "memory")
        self.assertEqual(strategy, "TEST_STRATEGY")
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 1)
    
    def test_cache_expiration(self):
        """Testa expiração do cache"""
        action_plan = {"patches_to_apply": []}
        
        # Cache com TTL curto
        cache = StrategyCache(ttl_seconds=1)  # 1 segundo
        cache.put(action_plan, "", "STRATEGY")
        
        # Espera expirar
        import time
        time.sleep(1.1)
        
        # Deve retornar None após expiração
        self.assertIsNone(cache.get(action_plan))
    
    def test_cache_lru_eviction(self):
        """Testa evicção LRU do cache"""
        # Cache pequeno
        cache = StrategyCache(maxsize=2)
        
        # Adiciona 3 items (deve remover o mais antigo)
        for i in range(3):
            action_plan = {"patches_to_apply": [{"file_path": f"file{i}.py"}]}
            cache.put(action_plan, "", f"STRATEGY_{i}")
        
        # Primeiro deve ter sido removido
        action_plan_0 = {"patches_to_apply": [{"file_path": "file0.py"}]}
        self.assertIsNone(cache.get(action_plan_0))
        
        # Últimos dois devem estar presentes
        action_plan_1 = {"patches_to_apply": [{"file_path": "file1.py"}]}
        action_plan_2 = {"patches_to_apply": [{"file_path": "file2.py"}]}
        self.assertEqual(cache.get(action_plan_1), "STRATEGY_1")
        self.assertEqual(cache.get(action_plan_2), "STRATEGY_2")


class TestMaestroAgentWithCache(unittest.TestCase):
    """Testa MaestroAgent com cache integrado"""
    
    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)
        self.model_config = {"primary": "test_model"}
        self.config = {
            "validation_strategies": {
                "TEST_STRATEGY": {"steps": ["test"]},
                "NO_OP_STRATEGY": {"steps": []}
            }
        }
        self.agent = MaestroAgent(self.model_config, self.config, self.logger)
    
    @patch('agent.utils.llm_client.call_llm_api')
    @patch('agent.llm_performance_booster.optimized_llm_call')
    def test_maestro_uses_cache(self, mock_llm, mock_optimized):
        """Testa que Maestro usa cache quando disponível"""
        action_plan = {"patches_to_apply": [{"file_path": "test.py"}]}
        
        # Primeira chamada - deve chamar LLM
        mock_llm.return_value = ('{"strategy_key": "TEST_STRATEGY"}', None)
        
        result1 = self.agent.choose_strategy(action_plan)
        self.assertTrue(result1[-1]["success"])
        mock_llm.assert_called_once()
        
        # Segunda chamada - deve usar cache
        mock_llm.reset_mock()
        result2 = self.agent.choose_strategy(action_plan)
        
        self.assertTrue(result2[-1]["success"])
        self.assertEqual(result2[-1]["model"], "cache")
        self.assertEqual(result2[-1]["parsed_json"]["strategy_key"], "TEST_STRATEGY")
        mock_llm.assert_not_called()
    
    def test_maestro_cache_stats(self):
        """Testa estatísticas do cache"""
        action_plan = {"patches_to_apply": []}
        
        # Adiciona estratégia ao cache via rule-based
        self.agent.choose_strategy(action_plan)
        
        # Verifica estatísticas
        stats = self.agent.strategy_cache.get_stats()
        self.assertGreater(stats['size'], 0)
        self.assertEqual(stats['maxsize'], 100)


if __name__ == '__main__':
    unittest.main() 