import unittest
from unittest.mock import patch, MagicMock
import requests
import logging

# Import the function to be tested
from agent.utils.llm_client import call_llm_api

class TestCallLlmApi(unittest.TestCase):

    def setUp(self):
        # Basic logger setup for tests, if needed
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG) # Or any level
        # You might want to add a handler if you want to see logs during tests,
        # e.g., logging.StreamHandler(sys.stdout)

        # Common test parameters
        self.model_config = {
            "primary": "test_model",
            "fallback": "fallback_model",
            "primary_api_key": "test_api_key",
            "fallback_api_key": "fallback_api_key",
            "primary_base_url": "https://api.example.com/v1",
            "fallback_base_url": "https://fallback.example.com/v1",
        }
        self.prompt = "test_prompt"
        self.temperature = 0.5

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_success(self, mock_post):
        # Configure the mock response for a successful API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test LLM response content"
                }
            }]
        }
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )

        # Assertions
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], self.model_config['primary'])
        self.assertEqual(kwargs['json']['messages'][0]['content'], self.prompt)
        self.assertEqual(content, "Test LLM response content")
        self.assertIsNone(error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_http_error(self, mock_post):
        # Configure the mock response for an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 401 # Unauthorized
        mock_response.text = "Unauthorized access"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )

        # Assertions
        self.assertEqual(mock_post.call_count, 2)
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("HTTP error occurred", error)
        self.assertIn("Status: 401", error)
        self.assertIn("Unauthorized access", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_request_exception(self, mock_post):
        # Configure the mock to raise a RequestException
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )

        # Assertions
        self.assertEqual(mock_post.call_count, 2)
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("Network error", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_choices(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No choices here"} # Missing 'choices'
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response missing or has invalid structure", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_empty_choices(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []} # Empty 'choices'
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("list index out of range", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_message_in_choice(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"no_message_here": "..."}]}
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response missing or has invalid structure", error)


    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_content_in_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"no_content_here": "..."}}]}
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response missing or has invalid structure", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_key_error(self, mock_post):
        # Simulate a malformed JSON response that would cause a KeyError
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{ # Valid choice
                "message": "this_is_not_a_dict" # Invalid message structure
            }]
        }
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("AttributeError", error) # Expect AttributeError due to calling .get on a string

        mock_response.json.return_value = {"choices": ["not_a_dict_item"]}
        mock_post.return_value = mock_response
        content, error = call_llm_api(
            self.model_config, self.prompt, self.temperature, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("AttributeError", error) # Error when trying .get("message") on a string


if __name__ == '__main__':
    unittest.main()