"""
Context Management Plugin for Spec Kit Integration
Implements intelligent context window management using before_agent_callback
"""

import json
import tiktoken
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.genai import types
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext


@dataclass
class ContextConfig:
    """Configuration for context management"""
    max_tokens: int = 1000000  # Leave room for response
    keep_system_messages: int = 2  # Always preserve first N system messages
    keep_recent_turns: int = 6     # Always preserve last N user-assistant pairs
    summarization_model: str = "gemini-2.0-flash"
    enable_memory_storage: bool = False
    prompt_style: str = "spec_kit"  # "spec_kit" or "openhands"


class ContextManagement:
    """
    Plugin that provides intelligent context management using before_agent_callback
    This allows context condensing before the agent even starts processing
    """
    
    def __init__(self, config: ContextConfig = None):
        super().__init__(name="context_management")
        self.config = config or ContextConfig()
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.conversation_memory = []  # Store summaries
        
    def estimate_tokens(self, contents: List[Any]) -> int:
        """Estimate token count for content list"""
        total_tokens = 0
        for content in contents:
            if hasattr(content, 'parts') and content.parts:
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        total_tokens += len(self.encoding.encode(part.text))
            elif hasattr(content, 'text') and content.text:
                total_tokens += len(self.encoding.encode(content.text))
        return total_tokens
    
    def identify_conversation_turns(self, events: List[Any]) -> Dict[str, List[int]]:
        """Identify different types of messages from session events"""
        system_indices = []
        user_indices = []
        assistant_indices = []
        
        for i, event in enumerate(events):
            if hasattr(event, 'content') and event.content:
                role = getattr(event.content, 'role', 'unknown')
                if role == 'system':
                    system_indices.append(i)
                elif role == 'user':
                    user_indices.append(i)
                elif role in ['assistant', 'model']:
                    assistant_indices.append(i)
                    
        return {
            'system': system_indices,
            'user': user_indices, 
            'assistant': assistant_indices
        }
    
    def create_summary_prompt(self, events_to_summarize: List[Any]) -> str:
        """Create a prompt for summarizing conversation history"""
        if self.config.prompt_style == "openhands":
            return self._create_openhands_style_prompt(events_to_summarize)
        else:
            return self._create_spec_kit_style_prompt(events_to_summarize)
    
    def _create_spec_kit_style_prompt(self, events_to_summarize: List[Any]) -> str:
        """Create spec-kit style prompt optimized for task-oriented conversations"""
        conversation_text = ""
        for event in events_to_summarize:
            if hasattr(event, 'content') and event.content:
                role = getattr(event.content, 'role', 'unknown')
                text = self._extract_text_from_content(event.content)
                conversation_text += f"\n[{role.upper()}]: {text}"
        
        return f"""You are maintaining a context-aware summary for a task-oriented conversation with a spec-kit integrated agent.
Focus on preserving essential information for task completion and specification management:

1. TASK_SPECIFICATIONS: Requirements, constraints, and acceptance criteria
2. SPEC_REFERENCES: Referenced specification files, sections, and versions
3. IMPLEMENTATION_PROGRESS: What has been built, tested, or validated
4. PENDING_WORK: Outstanding tasks, blockers, and next steps
5. DECISIONS_MADE: Architecture choices, trade-offs, and rationale
6. CODE_ARTIFACTS: File paths, function signatures, key implementations
7. VALIDATION_RESULTS: Test outcomes, spec compliance checks
8. CONTEXT_STATE: Current working directory, active files, configurations

CONVERSATION HISTORY:
{conversation_text}

Create a structured summary that maintains task continuity and spec compliance context:"""

    def _create_openhands_style_prompt(self, events_to_summarize: List[Any]) -> str:
        """Create OpenHands-style prompt for compatibility"""
        
        # Get previous summary from memory if available
        previous_summary = ""
        if self.conversation_memory:
            previous_summary = self.conversation_memory[-1]['summary']
        
        # Format events in OpenHands style
        events_text = ""
        for i, event in enumerate(events_to_summarize):
            if hasattr(event, 'content') and event.content:
                role = getattr(event.content, 'role', 'unknown')
                text = self._extract_text_from_content(event.content)
                # Truncate long content like OpenHands does
                truncated_text = text[:500] + "..." if len(text) > 500 else text
                events_text += f"<EVENT id={i}>\n[{role.upper()}]: {truncated_text}\n</EVENT>\n"
        
        prompt = """You are maintaining a context-aware state summary for an interactive software agent. This summary is critical because it:
1. Preserves essential context when conversation history grows too large
2. Prevents lost work when the session length exceeds token limits
3. Helps maintain continuity across multiple interactions

You will be given:
- A list of events (actions taken by the agent)
- The most recent previous summary (if one exists)

Capture all relevant information, especially:
- User requirements that were explicitly stated
- Work that has been completed
- Tasks that remain pending
- Current state of code, variables, and data structures
- The status of any version control operations"""

        # Add previous summary if exists
        if previous_summary:
            prompt += f"\n\n<PREVIOUS SUMMARY>\n{previous_summary}\n</PREVIOUS SUMMARY>\n"
        
        # Add events
        prompt += f"\n\n{events_text}"
        
        prompt += "\nCreate a comprehensive state summary that maintains continuity and preserves all essential context."
        
        return prompt

    def _extract_text_from_content(self, content: Any) -> str:
        """Extract text from content object"""
        if hasattr(content, 'parts') and content.parts:
            texts = []
            for part in content.parts:
                if hasattr(part, 'text') and part.text:
                    texts.append(part.text)
            return ' '.join(texts)
        elif hasattr(content, 'text') and content.text:
            return content.text
        return str(content)

    async def summarize_events(self, events: List[Any]) -> str:
        """Use LLM to create intelligent summary of events"""
        summary_prompt = self.create_summary_prompt(events)
        
        try:
            # Create a temporary agent for summarization
            from google.adk import Agent
            from google.adk.runners import InMemoryRunner
            
            # Use the configured summarization model
            temp_agent = Agent(
                name="context_summarizer", 
                model=self.config.summarization_model,
                instruction="You create concise, intelligent summaries of task-oriented conversations."
            )
            
            # Create runner and session for summarization
            runner = InMemoryRunner(agent=temp_agent, app_name='context_summarization')
            session = await runner.session_service.create_session(
                app_name='context_summarization', 
                user_id='context_manager'
            )
            
            # Send summarization request
            content = types.Content(
                role='user', 
                parts=[types.Part.from_text(text=summary_prompt)]
            )
            
            async for event in runner.run_async(
                user_id='context_manager',
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    summary_text = event.content.parts[0].text
                    print("✅ Context summary created using LLM")
                    return summary_text
            
            print("⚠️ LLM summary empty, using fallback")
            return self._create_fallback_summary(events)
                
        except Exception as e:
            print(f"⚠️ LLM summarization failed ({e}), using fallback")
            return self._create_fallback_summary(events)

    def _create_fallback_summary(self, events: List[Any]) -> str:
        """Create a simple summary when LLM summarization fails"""
        summary = "CONVERSATION SUMMARY:\n"
        user_messages = []
        assistant_messages = []
        
        for event in events:
            if hasattr(event, 'content') and event.content:
                role = getattr(event.content, 'role', 'unknown')
                text = self._extract_text_from_content(event.content)
                
                if role == 'user':
                    user_messages.append(text)
                elif role in ['assistant', 'model']:
                    assistant_messages.append(text)
        
        summary += f"USER REQUESTS: {' | '.join(user_messages[-3:])}\n"
        summary += f"ASSISTANT ACTIONS: {' | '.join(assistant_messages[-3:]) if assistant_messages else '[No responses]'}\n"
        summary += f"TOTAL EXCHANGES: {len(user_messages)} user messages, {len(assistant_messages)} assistant responses"
        
        return summary

    async def condense_session_context(self, callback_context: CallbackContext) -> bool:
        """
        Main condensation logic - operates on session events before agent runs
        Returns True if condensation occurred
        """
        session = callback_context.session
        if not session or not session.events:
            return False
            
        # Estimate tokens from session events
        current_tokens = 0
        for event in session.events:
            if hasattr(event, 'content') and event.content:
                current_tokens += self.estimate_tokens([event.content])
        
        # Check if condensation is needed
        if current_tokens <= self.config.max_tokens:
            return False
            
        print(f"🔄 Context condensation triggered. Current tokens: {current_tokens}, Max: {self.config.max_tokens}")
        
        # Identify message types
        indices = self.identify_conversation_turns(session.events)
        
        # Determine what to keep
        keep_indices = set()
        
        # 1. Always keep system messages (first N)
        system_to_keep = indices['system'][:self.config.keep_system_messages]
        keep_indices.update(system_to_keep)
        
        # 2. Always keep recent conversation turns
        recent_user_msgs = indices['user'][-self.config.keep_recent_turns:]
        recent_assistant_msgs = indices['assistant'][-self.config.keep_recent_turns:]
        keep_indices.update(recent_user_msgs)
        keep_indices.update(recent_assistant_msgs)
        
        # 3. Identify content to summarize (everything else)
        all_indices = set(range(len(session.events)))
        summarize_indices = sorted(all_indices - keep_indices)
        
        if not summarize_indices:
            return False  # Nothing to summarize
            
        # 4. Create summary of middle content
        events_to_summarize = [session.events[i] for i in summarize_indices]
        summary_text = await self.summarize_events(events_to_summarize)
        
        # 5. Store summary in memory for later retrieval
        if self.config.enable_memory_storage:
            self.conversation_memory.append({
                'timestamp': str(len(self.conversation_memory)),
                'summary': summary_text,
                'condensed_events': len(summarize_indices)
            })
        
        # 6. Reconstruct the events list
        new_events = []
        
        # Add kept system events
        for i in sorted(system_to_keep):
            new_events.append(session.events[i])
            
        # Add summary as a system event
        from google.adk.events.event import Event
        summary_content = types.Content(
            role='system',
            parts=[types.Part.from_text(
                text=f"[CONTEXT SUMMARY - {len(summarize_indices)} events condensed]\n{summary_text}"
            )]
        )
        summary_event = Event(
            invocation_id=callback_context.invocation_context.invocation_id,
            author='context_manager',
            content=summary_content,
        )
        new_events.append(summary_event)
        
        # Add kept recent events
        recent_indices = sorted(set(recent_user_msgs + recent_assistant_msgs))
        for i in recent_indices:
            new_events.append(session.events[i])
        
        # 7. Update the session
        session.events = new_events
        
        # Log the condensation
        new_tokens = 0
        for event in new_events:
            if hasattr(event, 'content') and event.content:
                new_tokens += self.estimate_tokens([event.content])
                
        print(f"✅ Context condensed: {current_tokens} → {new_tokens} tokens")
        print(f"📝 Summarized {len(summarize_indices)} events, kept {len(keep_indices)} events")
        
        return True

    async def before_agent_callback(
        self, 
        *, 
        agent: BaseAgent, 
        callback_context: CallbackContext
    ) -> Optional[types.Content]:
        """
        Before agent callback that performs context condensation
        This runs before the agent starts processing, allowing us to manage context
        """
        try:
            # Perform context condensation if needed
            condensed = await self.condense_session_context(callback_context)
            
            if condensed:
                print("🧠 Context intelligently condensed before agent execution!")
                # Update state to indicate condensation occurred
                callback_context.state.set('context_condensed', True)
                callback_context.state.set('condensation_count', 
                    callback_context.state.get('condensation_count', 0) + 1)
            
            # Don't return content - let the agent proceed normally
            return None
            
        except Exception as e:
            print(f"⚠️ Context management error: {e}")
            # Don't block agent execution on context management errors
            return None
    
    def get_memory_summary(self) -> str:
        """Get a summary of all stored conversation memories"""
        if not self.conversation_memory:
            return "No conversation memories stored yet."
            
        summary = "📚 CONVERSATION MEMORY BANK:\n\n"
        for i, memory in enumerate(self.conversation_memory):
            summary += f"Memory {i+1}:\n{memory['summary']}\n"
            summary += f"(Condensed {memory['condensed_events']} events)\n\n"
        
        return summary


# Factory function for easy integration
def create_context_management(
    max_tokens: int = 8000,
    keep_system_messages: int = 2,
    keep_recent_turns: int = 6,
    summarization_model: str = "gemini-2.0-flash",
    enable_memory_storage: bool = True,
    prompt_style: str = "spec_kit"
) -> ContextManagement:
    """
    Factory function to create a context management instance with custom configuration
    
    This provides a convenient way to create and configure a ContextManagement instance
    with commonly used settings for different scenarios.
    
    Args:
        max_tokens: Maximum tokens before triggering condensation (default: 8000)
            - For short conversations: 4000-6000
            - For implementation tasks: 8000-12000
            - For long research sessions: 15000+
        keep_system_messages: Number of system messages to always preserve (default: 2)
            - Usually 1-3 is sufficient for most use cases
        keep_recent_turns: Number of recent conversation turns to preserve (default: 6)
            - For quick tasks: 4-6 turns
            - For complex implementations: 8-12 turns
            - For debugging sessions: 10-15 turns
        summarization_model: Model to use for creating summaries (default: "gemini-2.0-flash")
            - Fast models: "gemini-2.0-flash", "gpt-4o-mini"
            - Quality models: "gemini-2.0-pro", "gpt-4o"
            - Code-focused: "iflow/Qwen3-Coder", "claude-3-5-sonnet"
        enable_memory_storage: Whether to store summaries for later retrieval (default: True)
            - True: Keeps history of all condensations for debugging
            - False: Saves memory, only keeps current state
        prompt_style: Style of summarization prompt (default: "spec_kit")
            - "spec_kit": Optimized for task-oriented development conversations
            - "openhands": Compatible with OpenHands-style summarization
    
    Returns:
        Configured ContextManagement instance ready for integration
        
    Example Usage:
        >>> # Basic usage with sensible defaults
        >>> context_mgmt = create_context_management()
        
        >>> # For long implementation sessions
        >>> context_mgmt = create_context_management(
        ...     max_tokens=12000,
        ...     keep_recent_turns=10,
        ...     summarization_model="iflow/Qwen3-Coder"
        ... )
        
        >>> # For memory-constrained environments
        >>> context_mgmt = create_context_management(
        ...     max_tokens=6000,
        ...     enable_memory_storage=False
        ... )
        
        >>> # Integration with agent
        >>> agent.context_management = create_context_management()
        >>> # The before_agent_callback will be automatically integrated
    """
    config = ContextConfig(
        max_tokens=max_tokens,
        keep_system_messages=keep_system_messages,
        keep_recent_turns=keep_recent_turns,
        summarization_model=summarization_model,
        enable_memory_storage=enable_memory_storage,
        prompt_style=prompt_style
    )
    
    return ContextManagement(config)


# Preset configurations for common use cases
def create_context_management_for_implementation() -> ContextManagement:
    """
    Create context management optimized for implementation tasks
    
    Returns:
        ContextManagement configured for long implementation sessions
    """
    return create_context_management(
        max_tokens=12000,  # Higher limit for complex implementations
        keep_recent_turns=10,  # Keep more context for implementation continuity
        summarization_model="iflow/Qwen3-Coder",  # Code-focused model
        enable_memory_storage=True,
        prompt_style="spec_kit"
    )


def create_context_management_for_debugging() -> ContextManagement:
    """
    Create context management optimized for debugging sessions
    
    Returns:
        ContextManagement configured for debugging workflows
    """
    return create_context_management(
        max_tokens=10000,  # Medium-high limit for debugging context
        keep_recent_turns=15,  # Keep lots of recent context for debugging
        summarization_model="gemini-2.0-flash",  # Fast model for quick summaries
        enable_memory_storage=True,
        prompt_style="spec_kit"
    )


def create_context_management_lightweight() -> ContextManagement:
    """
    Create lightweight context management for resource-constrained environments
    
    Returns:
        ContextManagement configured for minimal resource usage
    """
    return create_context_management(
        max_tokens=6000,  # Lower limit to trigger condensation sooner
        keep_recent_turns=4,  # Keep minimal recent context
        summarization_model="gemini-2.0-flash",  # Fast, efficient model
        enable_memory_storage=False,  # Don't store history to save memory
        prompt_style="spec_kit"
    )


# Example usage
if __name__ == "__main__":
    print("Context Management for Spec Kit Integration")
    print("This provides intelligent context condensation using before_agent_callback")
    
    # Example of creating different configurations
    print("\n🔧 Available Configurations:")
    
    # Basic configuration
    basic = create_context_management()
    print(f"Basic: max_tokens={basic.config.max_tokens}, recent_turns={basic.config.keep_recent_turns}")
    
    # Implementation configuration
    impl = create_context_management_for_implementation()
    print(f"Implementation: max_tokens={impl.config.max_tokens}, recent_turns={impl.config.keep_recent_turns}")
    
    # Debugging configuration
    debug = create_context_management_for_debugging()
    print(f"Debugging: max_tokens={debug.config.max_tokens}, recent_turns={debug.config.keep_recent_turns}")
    
    # Lightweight configuration
    light = create_context_management_lightweight()
    print(f"Lightweight: max_tokens={light.config.max_tokens}, recent_turns={light.config.keep_recent_turns}")

