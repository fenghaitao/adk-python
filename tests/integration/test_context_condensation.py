"""
Unit tests for context condensation improvements.

Tests the multi-pass recursive condensation, tool output truncation,
and guaranteed token limit enforcement.

Run: pytest test_context_condensation.py -v
"""

import asyncio
import json
import os
import sys
sys.path.insert(0, '/nfs/site/disks/ssm_yongzhuo_001/ai_agents/adk-openspec/src')

import pytest
from unittest.mock import Mock, AsyncMock, patch

from google.genai import types
from google.adk.events.event import Event
from google.adk.flows.llm_flows.contents import (
    _condense_session_context,
    _truncate_tool_output,
    _estimate_tokens,
    _find_last_function_call_index,
)

# Mark all tests to use anyio for async support
pytestmark = pytest.mark.anyio


class TestToolOutputTruncation:
    """Test truncation of large tool outputs."""

    def test_short_text_unchanged(self):
        """Short text should not be truncated."""
        short_text = "This is a short message."
        result = _truncate_tool_output(short_text, max_tokens=2000)
        assert result == short_text

    def test_long_text_truncated(self):
        """Long text should be truncated with marker."""
        long_text = "START: " + "x" * 40000 + " :END"
        result = _truncate_tool_output(long_text, max_tokens=100)
        
        assert "[... " in result
        assert "tokens truncated" in result
        assert "START:" in result
        assert ":END" in result


class TestTokenEstimation:
    """Test token counting."""

    def test_empty_content(self):
        """Empty content = 0 tokens."""
        empty = types.Content(role='user', parts=[])
        assert _estimate_tokens([empty]) == 0

    def test_text_content(self):
        """Should count text tokens."""
        text = types.Content(
            role='user',
            parts=[types.Part.from_text(text="Hello world test")]
        )
        tokens = _estimate_tokens([text])
        assert 0 < tokens < 20


class TestFindLastFunctionCall:
    """Test finding last function call."""

    def test_no_function_calls(self):
        """No calls = -1."""
        events = [
            Event(invocation_id='1', author='user',
                  content=types.Content(role='user', parts=[types.Part.from_text(text="Hi")]))
        ]
        assert _find_last_function_call_index(events) == -1

    def test_find_last_call(self):
        """Should find last function call index."""
        events = [
            Event(invocation_id='1', author='user',
                  content=types.Content(role='user', parts=[types.Part.from_text(text="Hi")])),
            Event(invocation_id='2', author='agent',
                  content=types.Content(role='model', parts=[types.Part.from_function_call(name="test", args={})])),
            Event(invocation_id='3', author='user',
                  content=types.Content(role='user', parts=[types.Part.from_text(text="Thanks")])),
        ]
        assert _find_last_function_call_index(events) == 1


class TestBasicCondensation:
    """Test basic condensation behavior."""

    async def test_no_condensation_under_limit(self):
        """Should not condense when under limit."""
        events = [
            Event(invocation_id='1', author='user',
                  content=types.Content(role='user', parts=[types.Part.from_text(text="Short")])),
        ]
        
        os.environ['CONTEXT_MAX_TOKENS'] = '1000000'
        result = await _condense_session_context(events)
        
        assert len(result) == len(events)

    async def test_condensation_disabled(self):
        """Should not condense when disabled."""
        events = [Event(invocation_id=str(i), author='user',
                       content=types.Content(role='user', parts=[types.Part.from_text(text="x" * 10000)]))
                  for i in range(100)]
        
        os.environ['CONTEXT_ENABLE_CONDENSATION'] = 'false'
        result = await _condense_session_context(events)
        
        assert len(result) == len(events)


class TestMultiPassCondensation:
    """Test multi-pass recursive condensation."""

    @patch('google.adk.flows.llm_flows.contents._summarize_events_with_llm')
    async def test_recursive_triggered(self, mock_summarize):
        """Should trigger recursive condensation when first pass exceeds hard limit."""
        # Mock should return small summary
        async def mock_summary(events, model):
            return "Summary of conversation"  # Small summary
        
        mock_summarize.side_effect = mock_summary
        
        # Create events with a function call in the middle to trigger function-call-based logic
        events = []
        for i in range(150):
            events.append(Event(
                invocation_id=str(i),
                author='user' if i % 2 == 0 else 'agent',
                content=types.Content(
                    role='user' if i % 2 == 0 else 'model',
                    parts=[types.Part.from_text(text=f"Msg {i}: " + "x" * 3000)]
                )
            ))
        
        # Add a function call in the middle to ensure we have events to summarize before it
        events.insert(75, Event(
            invocation_id='func_call',
            author='agent',
            content=types.Content(role='model', parts=[types.Part.from_function_call(name="tool", args={})])
        ))
        
        # Add more events after function call
        for i in range(150, 200):
            events.append(Event(
                invocation_id=str(i),
                author='user' if i % 2 == 0 else 'agent',
                content=types.Content(
                    role='user' if i % 2 == 0 else 'model',
                    parts=[types.Part.from_text(text=f"Msg {i}: " + "x" * 3000)]
                )
            ))
        
        # Set limits that will force recursive condensation
        os.environ['CONTEXT_MAX_TOKENS'] = '10000'
        os.environ['CONTEXT_HARD_LIMIT_TOKENS'] = '8000'
        os.environ['CONTEXT_MAX_RECENT_EVENTS'] = '80'  # Will keep many events after function call
        
        result = await _condense_session_context(events)
        
        # The test is that recursive condensation was triggered (printed warning in logs)
        # and the final result is under the hard limit
        final_tokens = sum(_estimate_tokens([e.content]) for e in result
                          if hasattr(e, 'content') and e.content)
        assert final_tokens <= 8000, f"Final {final_tokens} exceeds hard limit 8000"
        
        # Should have called summarize at least once
        assert mock_summarize.call_count >= 1, f"Expected >= 1 calls, got {mock_summarize.call_count}"


class TestGuaranteedLimit:
    """Test that result is always under hard limit."""

    @patch('google.adk.flows.llm_flows.contents._summarize_events_with_llm')
    async def test_always_under_limit(self, mock_summarize):
        """Final result MUST be under hard limit."""
        async def mock_summary(events, model):
            return "Summary"
        
        mock_summarize.side_effect = mock_summary
        
        # Create massive context
        events = []
        for i in range(500):
            events.append(Event(
                invocation_id=str(i),
                author='user' if i % 2 == 0 else 'agent',
                content=types.Content(
                    role='user' if i % 2 == 0 else 'model',
                    parts=[types.Part.from_text(text="x" * 5000)]
                )
            ))
        
        hard_limit = 10000
        os.environ['CONTEXT_MAX_TOKENS'] = '15000'
        os.environ['CONTEXT_HARD_LIMIT_TOKENS'] = str(hard_limit)
        os.environ['CONTEXT_MAX_RECENT_EVENTS'] = '50'
        
        result = await _condense_session_context(events)
        
        # Calculate final tokens
        final_tokens = sum(_estimate_tokens([e.content]) for e in result
                          if hasattr(e, 'content') and e.content)
        
        # MUST be under hard limit
        assert final_tokens <= hard_limit, f"Final {final_tokens} exceeds limit {hard_limit}"
        print(f"✅ Success: {final_tokens} tokens < {hard_limit} limit")


# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_env():
    """Reset environment after each test."""
    original = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original)


if __name__ == '__main__':
    # Run tests
    print("Running context condensation tests...\n")
    pytest.main([__file__, '-v', '--tb=short'])
