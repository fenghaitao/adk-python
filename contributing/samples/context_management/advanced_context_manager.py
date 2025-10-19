"""
Advanced Context Management for adk-python
Implements intelligent context window management similar to OpenHands condenser
"""

import json
import tiktoken
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.adk import Agent
from google.adk.agents.base_agent import BaseAgent
from google.adk.models.llm_request import LlmRequest


class MockContent:
    """Mock content object for storing conversation summaries"""
    def __init__(self, role: str, text: str):
        self.role = role
        self.text = text
        self.parts = []  # Add parts attribute for compatibility
    
    def model_dump_json(self, **kwargs):
        return f'{{"role": "{self.role}", "text": "{self.text}"}}'


@dataclass
class ContextConfig:
    """Configuration for context management"""
    max_tokens: int = 8000  # Leave room for response
    keep_system_messages: int = 2  # Always preserve first N system messages
    keep_recent_turns: int = 6     # Always preserve last N user-assistant pairs
    summarization_model: str = "iflow/Qwen3-Coder"
    enable_memory_storage: bool = True


class AdvancedContextManager:
    """
    Intelligent context manager that mimics OpenHands condenser behavior
    """
    
    def __init__(self, config: ContextConfig):
        self.config = config
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.conversation_memory = []  # Store summaries
        
    def estimate_tokens(self, contents: List[Any]) -> int:
        """Estimate token count for content list"""
        total_tokens = 0
        for content in contents:
            if hasattr(content, 'text') and content.text:
                total_tokens += len(self.encoding.encode(content.text))
            elif hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'text'):
                        total_tokens += len(self.encoding.encode(part.text))
        return total_tokens
    
    def identify_conversation_turns(self, contents: List[Any]) -> Dict[str, List[int]]:
        """Identify different types of messages"""
        system_indices = []
        user_indices = []
        assistant_indices = []
        
        for i, content in enumerate(contents):
            role = getattr(content, 'role', 'unknown')
            if role == 'system':
                system_indices.append(i)
            elif role == 'user':
                user_indices.append(i)
            elif role == 'assistant':
                assistant_indices.append(i)
                
        return {
            'system': system_indices,
            'user': user_indices, 
            'assistant': assistant_indices
        }
    
    def create_summary_prompt(self, contents_to_summarize: List[Any]) -> str:
        """Create a prompt for summarizing conversation history"""
        conversation_text = ""
        for content in contents_to_summarize:
            role = getattr(content, 'role', 'unknown')
            text = getattr(content, 'text', '') or self._extract_text(content)
            conversation_text += f"\n[{role.upper()}]: {text}"
        
        return f"""You are maintaining a context-aware summary for an ongoing conversation. 
Analyze the conversation history and create a comprehensive summary that preserves:

1. USER_CONTEXT: Essential user requirements, goals, and preferences
2. TASK_TRACKING: Active tasks, their IDs, status, and progress
3. COMPLETED_WORK: What has been accomplished so far
4. PENDING_TASKS: What still needs to be done
5. CURRENT_STATE: Important variables, data, configurations
6. CODE_STATE: File paths, function names, key code changes
7. DECISIONS_MADE: Important choices and their reasoning
8. ERRORS_RESOLVED: Problems encountered and solutions

CONVERSATION HISTORY:
{conversation_text}

Create a structured summary that captures the essential context:"""

    def _extract_text(self, content: Any) -> str:
        """Extract text from various content formats"""
        if hasattr(content, 'text') and content.text:
            return content.text
        elif hasattr(content, 'parts'):
            texts = []
            for part in content.parts:
                if hasattr(part, 'text'):
                    texts.append(part.text)
            return ' '.join(texts)
        return str(content)

    async def summarize_content(self, contents: List[Any], agent: BaseAgent) -> str:
        """Use LLM to create intelligent summary"""
        summary_prompt = self.create_summary_prompt(contents)
        
        # Create a temporary request for summarization using ADK runner pattern
        try:
            # Create a temporary agent for summarization
            from google.adk.runners import InMemoryRunner
            from google.genai import types
            
            # Use the same model as the main agent for summarization
            temp_agent = Agent(
                name="summarizer", 
                model=self.config.summarization_model,
                instruction="You create concise, intelligent summaries of conversations."
            )
            
            # Create runner and session for summarization
            runner = InMemoryRunner(agent=temp_agent, app_name='summarization')
            session = await runner.session_service.create_session(app_name='summarization', user_id='summarizer')
            
            # Send summarization request
            content = types.Content(role='user', parts=[types.Part.from_text(text=summary_prompt)])
            
            async for event in runner.run_async(
                user_id='summarizer',
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    summary_text = event.content.parts[0].text
                    print("✅ LLM-powered intelligent summary created")
                    return summary_text
            
            print("⚠️ LLM summary empty, using fallback")
            return self._create_fallback_summary(contents)
                
        except Exception as e:
            print(f"⚠️ LLM summarization failed ({e}), using fallback")
            return self._create_fallback_summary(contents)

    def _create_fallback_summary(self, contents: List[Any]) -> str:
        """Create a simple summary when LLM summarization fails"""
        summary = "CONVERSATION SUMMARY:\n"
        user_messages = []
        assistant_messages = []
        
        for content in contents:
            role = getattr(content, 'role', 'unknown')
            text = self._extract_text(content)
            
            if role == 'user':
                user_messages.append(text)  # Keep full content, no truncation
            elif role == 'assistant' or role == 'model':  # Some systems use 'model' instead of 'assistant'
                assistant_messages.append(text)  # Keep full content, no truncation
        
        summary += f"USER REQUESTS: {' | '.join(user_messages[-3:])}\n"  # Show last 3, use | separator
        summary += f"ASSISTANT ACTIONS: {' | '.join(assistant_messages[-3:]) if assistant_messages else '[No assistant responses captured]'}\n"
        summary += f"TOTAL EXCHANGES: {len(user_messages)} user messages, {len(assistant_messages)} assistant responses"
        
        return summary

    async def condense_context(self, llm_request: LlmRequest, agent: BaseAgent) -> bool:
        """
        Main condensation logic - returns True if condensation occurred
        """
        contents = llm_request.contents
        current_tokens = self.estimate_tokens(contents)
        
        # Check if condensation is needed
        if current_tokens <= self.config.max_tokens:
            return False
            
        print(f"🔄 Context condensation triggered. Current tokens: {current_tokens}, Max: {self.config.max_tokens}")
        
        # Identify message types
        indices = self.identify_conversation_turns(contents)
        
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
        all_indices = set(range(len(contents)))
        summarize_indices = sorted(all_indices - keep_indices)
        
        if not summarize_indices:
            return False  # Nothing to summarize
            
        # 4. Create summary of middle content
        contents_to_summarize = [contents[i] for i in summarize_indices]
        summary_text = await self.summarize_content(contents_to_summarize, agent)
        
        # 5. Store summary in memory for later retrieval
        if self.config.enable_memory_storage:
            self.conversation_memory.append({
                'timestamp': str(len(self.conversation_memory)),
                'summary': summary_text,
                'condensed_turns': len(summarize_indices)
            })
        
        # 6. Reconstruct the content list
        new_contents = []
        
        # Add kept system messages
        for i in sorted(system_to_keep):
            new_contents.append(contents[i])
            
        # Add summary as a system message (create mock content object)
        summary_content = MockContent(
            role='system',
            text=f"[CONVERSATION SUMMARY - {len(summarize_indices)} messages condensed]\n{summary_text}"
        )
        new_contents.append(summary_content)
        
        # Add kept recent messages
        recent_indices = sorted(set(recent_user_msgs + recent_assistant_msgs))
        for i in recent_indices:
            new_contents.append(contents[i])
        
        # 7. Update the request
        llm_request.contents = new_contents
        
        # Log the condensation
        new_tokens = self.estimate_tokens(new_contents)
        print(f"✅ Context condensed: {current_tokens} → {new_tokens} tokens")
        print(f"📝 Summarized {len(summarize_indices)} messages, kept {len(keep_indices)} messages")
        
        return True


class SmartAgent:
    """
    Wrapper around adk-python Agent with built-in intelligent context management
    """
    
    def __init__(self, agent: BaseAgent, context_config: ContextConfig = None):
        self.agent = agent
        self.context_manager = AdvancedContextManager(context_config or ContextConfig())
        
        # Replace the agent's before_model_callback
        self.original_callback = getattr(agent, 'before_model_callback', None)
        agent.before_model_callback = self._smart_context_callback
        
    async def _smart_context_callback(self, callback_context, llm_request: LlmRequest):
        """Enhanced callback with intelligent context management"""
        
        # Run original callback if it exists
        if self.original_callback:
            await self.original_callback(callback_context, llm_request)
        
        # Apply intelligent context management
        condensed = await self.context_manager.condense_context(llm_request, self.agent)
        
        if condensed:
            print("🧠 Context intelligently condensed - conversation can continue indefinitely!")
    
    def get_memory_summary(self) -> str:
        """Get a summary of all stored conversation memories"""
        if not self.context_manager.conversation_memory:
            return "No conversation memories stored yet."
            
        summary = "📚 CONVERSATION MEMORY BANK:\n\n"
        for i, memory in enumerate(self.context_manager.conversation_memory):
            summary += f"Memory {i+1}:\n{memory['summary']}\n"
            summary += f"(Condensed {memory['condensed_turns']} turns)\n\n"
        
        return summary
    
    # Delegate other methods to the wrapped agent
    def __getattr__(self, name):
        return getattr(self.agent, name)


# Example Usage Functions
def create_smart_agent_with_context_management():
    """Example of how to create an agent with advanced context management"""
    
    # Configure context management
    config = ContextConfig(
        max_tokens=8000,           # Trigger condensation at 8K tokens
        keep_system_messages=2,    # Always preserve first 2 system messages
        keep_recent_turns=8,       # Always preserve last 8 conversation turns
        summarization_model="gemini-2.0-flash",  # Use for summarization
        enable_memory_storage=True # Store summaries for later retrieval
    )
    
    # Create base agent (replace with your actual agent creation)
    base_agent = Agent(
        name="smart_agent_base",
        model="iflow/Qwen3-Coder",
        tools=[],  # Your tools here
        instruction="You are a helpful AI assistant."
    )
    
    # Wrap with smart context management
    smart_agent = SmartAgent(base_agent, config)
    
    return smart_agent


async def demo_long_conversation():
    """Demo showing how the smart agent handles long conversations"""
    
    agent = create_smart_agent_with_context_management()
    
    # Simulate a very long conversation
    for i in range(100):  # This would normally exceed context limits
        
        response = await agent.send_message(
            f"Task {i}: Please help me with step {i} of my project. "
            f"This is building on all our previous work."
        )
        
        print(f"Turn {i}: Response length: {len(response)}")
        
        # Every 20 turns, check memory
        if i % 20 == 0 and i > 0:
            memory_summary = agent.get_memory_summary()
            print(f"\n💭 Memory at turn {i}:\n{memory_summary[:200]}...\n")
    
    print("🎉 Completed 100-turn conversation without context limits!")


if __name__ == "__main__":
    # Example usage
    print("Advanced Context Management for adk-python")
    print("This implements OpenHands-style intelligent condensation")
    
    # Run the demo
    # asyncio.run(demo_long_conversation())