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
        self.api_key = "test_api_key"
        self.model = "test_model"
        self.prompt = "test_prompt"
        self.temperature = 0.5
        self.base_url = "https://api.example.com/v1"

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
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )

        # Assertions
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"{self.base_url}/chat/completions")
        self.assertEqual(kwargs['json']['model'], self.model)
        self.assertEqual(kwargs['json']['messages'][0]['content'], self.prompt)
        self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")

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
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )

        # Assertions
        mock_post.assert_called_once()
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
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )

        # Assertions
        mock_post.assert_called_once()
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("Request failed: Network error", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_choices(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No choices here"} # Missing 'choices'
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response missing 'choices' key", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_empty_choices(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []} # Empty 'choices'
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response missing 'choices' key or 'choices' is empty", error) # Adjusted to match error message

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_message_in_choice(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"no_message_here": "..."}]}
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response 'choices'[0] missing 'message' key", error)


    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_missing_content_in_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"no_content_here": "..."}}]}
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("API response 'message' missing 'content' key", error)

    @patch('agent.utils.llm_client.requests.post')
    def test_call_llm_api_key_error(self, mock_post):
        # Simulate a malformed JSON response that would cause a KeyError
        mock_response = MagicMock()
        mock_response.status_code = 200
        # This malformed structure will cause a KeyError when trying to access response_json["choices"][0]["message"]["content"]
        # if the initial checks for "choices" or "message" were less strict.
        # Given the current strict checks, this specific KeyError might be hard to trigger without
        # also triggering one of the earlier "missing key" errors.
        # Let's assume a case where 'choices' exists, 'message' exists, but 'content' is accessed before check.
        # The current implementation checks for 'content' presence, so this exact path is unlikely.
        # However, a KeyError could occur if `response.json()` itself fails or returns non-dict.
        # For this test, let's assume a more direct KeyError during JSON parsing if that's possible
        # or a key error deeper if the structure is unexpected.

        # To test the KeyError catch specifically, let's imagine the json structure is slightly off
        # in a way not caught by previous checks but leading to an issue.
        # Example: 'choices' is not a list, or 'message' is not a dict.
        mock_response.json.return_value = {
            "choices": [{ # Valid choice
                "message": "this_is_not_a_dict" # Invalid message structure
            }]
        }
        mock_post.return_value = mock_response

        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        self.assertIn("AttributeError", error) # Expect AttributeError due to calling .get on a string

        # Test case for actual KeyError if a deeply nested key is expected but missing,
        # assuming outer structures are dicts.
        # This scenario is now less likely due to comprehensive checks for 'choices', 'message', 'content'.
        # However, if the API returned a valid structure but with an unexpected internal key missing
        # that the code might later try to access (not the case in current call_llm_api),
        # a KeyError could happen.
        # For the current structure of call_llm_api, most "missing key" issues are explicitly handled.
        # A true KeyError might occur if `response.json()` itself fails and that's caught by the generic Exception,
        # or if `response_json` was not a dict.

        # Let's simulate a case where 'choices' is a list, but its elements are not dicts
        mock_response.json.return_value = {"choices": ["not_a_dict_item"]}
        mock_post.return_value = mock_response
        content, error = call_llm_api(
            self.api_key, self.model, self.prompt, self.temperature, self.base_url, self.logger
        )
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        # This would lead to: response_json["choices"][0].get("message") -> 'str' object has no attribute 'get'
        self.assertIn("AttributeError", error) # Error when trying .get("message") on a string

        # To truly test the KeyError for a missing key from a dict:
        # Let's assume a hypothetical scenario where the code expects response_json["choices"][0]["message"]["details"]["text"]
        # and "details" is missing.
        # The current code only goes as far as "content".
        # The existing KeyError catch is more of a fallback.
        # The current structure is well-guarded against KeyErrors for the paths it accesses.
        # The most plausible KeyError would be if `response_json` itself wasn't a dict,
        # or if `response_json['choices']` was attempted on a non-dict `response_json`.
        # But `response.json()` usually ensures a dict or list at the top level or raises error.
        # So, the current KeyError catch is a very broad fallback.
        # The test for "API response missing 'choices' key" already covers cases where 'choices' isn't there.


if __name__ == '__main__':
    unittest.main()
