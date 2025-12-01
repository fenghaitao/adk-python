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
        os.environ['CONTEXT_MAX_RECENT_EVENTS'] = '20'  # Keep reasonable number to avoid infinite loop
        
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


@pytest.mark.anyio
async def test_orphaned_function_response_removed():
    """
    Test that context condensation doesn't create scenarios where responses exist without calls.
    
    This simulates the production bug where condensation might keep a response
    but its corresponding call gets summarized away.
    """
    invocation_id = 'test_orphan_response'
    
    # Simple scenario: response is kept in recent window, call is not
    events = []
    
    # Add some old events
    for i in range(5):
        events.append(Event(
            invocation_id=invocation_id,
            author='user',
            content=types.Content(
                role='user',
                parts=[types.Part.from_text(text=f"Old message {i}")]
            )
        ))
    
    # Add a function call early on (will be summarized)
    call_id = 'call_Qo7F8nw7c3CERVd7xEEvkHo3'
    events.append(Event(  # Index 5
        invocation_id=invocation_id,
        author='assistant',
        content=types.Content(
            role='model',
            parts=[types.Part(
                function_call=types.FunctionCall(
                    name='run_terminal',
                    args={'command': 'ls'},
                    id=call_id
                )
            )]
        )
    ))
    
    # Add the response right after
    events.append(Event(  # Index 6
        invocation_id=invocation_id,
        author='tool',
        content=types.Content(
            role='function',
            parts=[types.Part(
                function_response=types.FunctionResponse(
                    name='run_terminal',
                    response={'output': 'file1.txt\nfile2.txt'},
                    id=call_id
                )
            )]
        )
    ))
    
    # Add many recent events with large content to trigger condensation
    for i in range(30):
        events.append(Event(
            invocation_id=invocation_id,
            author='user' if i % 2 == 0 else 'assistant',
            content=types.Content(
                role='user' if i % 2 == 0 else 'model',
                parts=[types.Part.from_text(text=f"Recent {i}: " + "x" * 2000)]
            )
        ))
    
    # Total: 37 events
    # Call at index 5, response at index 6
    # With MAX_RECENT_EVENTS=10, we keep indices 27-36
    # Both call and response get summarized - fine
    
    # But what if during summarization, the mock accidentally keeps the response?
    # Let's directly test the condensation logic
    
    hard_limit = 10000
    os.environ['CONTEXT_MAX_TOKENS'] = '5000'
    os.environ['CONTEXT_HARD_LIMIT_TOKENS'] = str(hard_limit)
    os.environ['CONTEXT_MAX_RECENT_EVENTS'] = '10'
    os.environ['CONTEXT_ENABLE_CONDENSATION'] = 'true'
    
    result = await _condense_session_context(events)
    
    # Verify: No orphaned responses (responses without their calls)
    call_ids_present = set()
    response_ids_present = set()
    
    for event in result:
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'function_call') and part.function_call and part.function_call.id:
                    call_ids_present.add(part.function_call.id)
                if hasattr(part, 'function_response') and part.function_response and part.function_response.id:
                    response_ids_present.add(part.function_response.id)
    
    # Every response must have its call
    orphaned_responses = response_ids_present - call_ids_present
    if orphaned_responses:
        pytest.fail(f"FAIL: Orphaned function responses found: {orphaned_responses}. "
                  f"This would cause API error: 'tool_call_id did not have response messages'")
    
    print(f"✅ Success: No orphaned responses. Calls: {call_ids_present}, Responses: {response_ids_present}")
    
    # Verify we're under hard limit
    final_tokens = sum(_estimate_tokens([e.content]) for e in result
                      if hasattr(e, 'content') and e.content)
    assert final_tokens <= hard_limit, f"Final {final_tokens} exceeds limit {hard_limit}"
    
    print(f"✅ Success: Context condensed to {final_tokens} tokens < {hard_limit} limit")


@pytest.mark.anyio
async def test_orphaned_function_call_removed():
    """
    Test that orphaned function calls (calls without responses in kept events) are removed.
    
    This reproduces the wdt_dbg14.3.log bug where context condensation left a function call
    without its response, causing: "An assistant message with 'tool_calls' must be followed
    by tool messages responding to each 'tool_call_id'."
    """
    invocation_id = 'test_orphan'
    
    events = []
    
    # Add some old events that will be summarized
    for i in range(10):
        events.append(Event(
            invocation_id=invocation_id,
            author='user',
            content=types.Content(
                role='user',
                parts=[types.Part.from_text(text=f"Old request {i}")]
            )
        ))
    
    # Add a function call in the middle that will be outside the summary window
    call_id = 'call_orphaned_123'
    events.append(Event(
        invocation_id=invocation_id,
        author='assistant',
        content=types.Content(
            role='model',
            parts=[types.Part(
                function_call=types.FunctionCall(
                    name='read_file',
                    args={'file': 'test.txt'},
                    id=call_id
                )
            )]
        )
    ))
    
    # Add the function response immediately after
    events.append(Event(
        invocation_id=invocation_id,
        author='tool',
        content=types.Content(
            role='function',
            parts=[types.Part(
                function_response=types.FunctionResponse(
                    name='read_file',
                    response={'content': 'file content here' * 100},  # Large response
                    id=call_id
                )
            )]
        )
    ))
    
    # Add many more recent events - the function call will be within recent_start_idx
    # but the response won't be in the final keep set due to STEP 3 logic
    for i in range(40):
        events.append(Event(
            invocation_id=invocation_id,
            author='user',
            content=types.Content(
                role='user',
                parts=[types.Part.from_text(text=f"Recent message {i}")]
            )
        ))
    
    # Set limits to force condensation
    # With max_recent_events=20, we keep events 32-51 (indices), which includes recent messages
    # but the function call at index 10 will be included due to last_func_call_idx logic
    # but response at index 11 won't be in the initial keep set
    hard_limit = 8000
    os.environ['CONTEXT_MAX_TOKENS'] = '10000'
    os.environ['CONTEXT_HARD_LIMIT_TOKENS'] = str(hard_limit)
    os.environ['CONTEXT_MAX_RECENT_EVENTS'] = '20'  # Keep only last 20 events
    
    result = await _condense_session_context(events)
    
    # Verify: If a function call is present, its response must also be present
    # The fix ensures no orphaned calls remain in the condensed context
    for event in result:
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    if part.function_call.id == call_id:
                        # Found the function call - verify its response is also present
                        has_matching_response = False
                        for check_event in result:
                            if hasattr(check_event, 'content') and check_event.content and check_event.content.parts:
                                for check_part in check_event.content.parts:
                                    if hasattr(check_part, 'function_response') and check_part.function_response:
                                        if check_part.function_response.id == call_id:
                                            has_matching_response = True
                                            break
                        
                        assert has_matching_response, f"FAIL: Function call {call_id} found without its response! This would cause API error."
    
    print(f"✅ Success: All function calls have matching responses or were removed during condensation")
    
    # Verify we're under hard limit
    final_tokens = sum(_estimate_tokens([e.content]) for e in result
                      if hasattr(e, 'content') and e.content)
    assert final_tokens <= hard_limit, f"Final {final_tokens} exceeds limit {hard_limit}"
    
    print(f"✅ Success: Orphaned function call removed, {final_tokens} tokens < {hard_limit} limit")


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
