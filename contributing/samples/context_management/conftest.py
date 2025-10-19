"""
Pytest configuration and fixtures for context management tests

This file provides shared fixtures and configuration for pytest.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from advanced_context_manager import ContextConfig, AdvancedContextManager, SmartAgent


@pytest.fixture
def default_config():
    """Provide default ContextConfig for tests"""
    return ContextConfig(max_tokens=1000, keep_recent_turns=2)


@pytest.fixture
def context_manager(default_config):
    """Provide AdvancedContextManager instance for tests"""
    return AdvancedContextManager(default_config)


@pytest.fixture
def mock_agent():
    """Provide mock agent for testing"""
    agent = Mock()
    agent._llm = AsyncMock()
    agent._before_model_callback = None
    
    # Mock LLM response
    mock_response = Mock()
    mock_response.text = "Test summary response"
    agent._llm.generate_content.return_value = mock_response
    
    return agent


@pytest.fixture
def smart_agent(mock_agent, default_config):
    """Provide SmartAgent instance for testing"""
    return SmartAgent(mock_agent, default_config)


@pytest.fixture
def sample_contents():
    """Provide sample conversation contents for testing"""
    return [
        Mock(role='system', text='You are a helpful assistant.'),
        Mock(role='user', text='Hello, how are you?'),
        Mock(role='assistant', text='I am doing well, thank you for asking!'),
        Mock(role='user', text='Can you help me with Python?'),
        Mock(role='assistant', text='Of course! I would be happy to help you with Python programming.'),
    ]


@pytest.fixture
def mock_llm_request(sample_contents):
    """Provide mock LLM request for testing"""
    request = Mock()
    request.contents = sample_contents
    return request