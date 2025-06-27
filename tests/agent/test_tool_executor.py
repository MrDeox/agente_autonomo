import unittest
from unittest.mock import patch, MagicMock
from agent.tool_executor import web_search

class TestToolExecutor(unittest.TestCase):
    
    @patch('agent.tool_executor.requests.get')
    def test_web_search_success(self, mock_get):
        # Configurar mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Results": [
                {"Text": "Resultado 1", "FirstURL": "https://exemplo.com/1"},
                {"Text": "Resultado 2", "FirstURL": "https://exemplo.com/2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Executar função
        success, results = web_search("test query")
        
        # Verificar resultados
        self.assertTrue(success)
        self.assertIn("Resultado 1", results)
        self.assertIn("https://exemplo.com/1", results)
    
    @patch('agent.tool_executor.requests.get')
    def test_web_search_no_results(self, mock_get):
        # Configurar mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Results": []}
        mock_get.return_value = mock_response
        
        # Executar função
        success, results = web_search("test query")
        
        # Verificar resultados
        self.assertTrue(success)
        self.assertEqual("Nenhum resultado encontrado para a pesquisa.", results)
    
    @patch('agent.tool_executor.requests.get')
    def test_web_search_error(self, mock_get):
        # Configurar mock para lançar exceção
        mock_get.side_effect = Exception("Erro de conexão")
        
        # Executar função
        success, results = web_search("test query")
        
        # Verificar resultados
        self.assertFalse(success)
        self.assertIn("Erro na pesquisa web: Erro de conexão", results)

if __name__ == '__main__':
    unittest.main()
