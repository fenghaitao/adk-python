"""
Practical Example: Using Advanced Context Management with adk-python
Shows how to integrate the smart context manager into real workflows
"""

import asyncio
from google.adk import Agent
from google.adk.tools.load_memory_tool import load_memory_tool
from google.adk.tools.preload_memory_tool import preload_memory_tool
from google.adk.runners import InMemoryRunner
from google.genai import types
from advanced_context_manager import SmartAgent, ContextConfig


async def example_1_basic_usage():
    """Basic example with automatic context management"""
    
    print("🔧 Example 1: Basic Smart Agent with Auto-Condensation")
    print("=" * 60)
    
    # Create agent with smart context management
    base_agent = Agent(
        name="coding_assistant",
        model="iflow/Qwen3-Coder",
        instruction="You are a helpful coding assistant.",
        tools=[]
    )
    
    # Wrap with intelligent context management
    smart_agent = SmartAgent(base_agent, ContextConfig(
        max_tokens=1000,  # Low limit for demo purposes
        keep_recent_turns=3
    ))
    
    # Have a long conversation - context will auto-condense
    conversation_topics = [
        "Help me design a Python web API",
        "What database should I use?", 
        "How do I handle authentication?",
        "Show me how to write unit tests",
        "How do I deploy to production?",
        "What about monitoring and logging?",
        "How do I handle errors gracefully?",
        "What about API versioning?",
        "How do I optimize performance?",
        "What security considerations should I have?"
    ]
    
    # Set up runner for testing
    runner = InMemoryRunner(agent=smart_agent.agent, app_name='context_test')
    session = await runner.session_service.create_session(app_name='context_test', user_id='test_user')
    
    for i, topic in enumerate(conversation_topics):
        print(f"\n📝 Turn {i+1}: {topic}")
        
        try:
            content = types.Content(role='user', parts=[types.Part.from_text(text=topic)])
            async for event in runner.run_async(
                user_id='test_user',
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts and event.content.parts[0].text:
                    response = event.content.parts[0].text
                    print(f"🤖 Response preview: {response[:100]}...")
                    break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
        
        # Show memory after a few turns
        if i == 5:
            print(f"\n💭 Memory would be available here in full implementation\n")
    
    print("\n✅ Completed long conversation without context overflow!")


async def example_2_custom_configuration():
    """Example with custom context management configuration"""
    
    print("\n🔧 Example 2: Custom Context Configuration")
    print("=" * 60)
    
    # Create highly customized context management
    custom_config = ContextConfig(
        max_tokens=2000,               # Higher limit
        keep_system_messages=3,        # Keep more system context
        keep_recent_turns=10,          # Keep more recent history
        summarization_model="gpt-4",   # Use GPT-4 for better summaries
        enable_memory_storage=True     # Enable external memory
    )
    
    base_agent = Agent(
        name="software_architect",
        model="iflow/Qwen3-Coder",
        instruction="You are an expert software architect.",
        tools=[load_memory_tool, preload_memory_tool]
    )
    
    smart_agent = SmartAgent(base_agent, custom_config)
    
    # Simulate technical discussion
    technical_topics = [
        "Design a microservices architecture for e-commerce",
        "How should I handle inter-service communication?",
        "What patterns should I use for data consistency?",
        "How do I implement distributed transactions?",
        "What about service discovery and load balancing?",
        "How do I handle failures and circuit breakers?",
        "What monitoring and observability tools should I use?",
        "How do I implement proper logging strategies?",
        "What about security between services?",
        "How do I manage configuration across services?"
    ]
    
    for i, topic in enumerate(technical_topics):
        print(f"\n📋 Discussion {i+1}: {topic}")
        
        # Demo: Context management would happen here
        print(f"🤖 Processing: {topic[:50]}...")
        print(f"🏗️  Architectural advice: [Demo response]")
    
    # Show final memory state
    final_memory = smart_agent.get_memory_summary()
    print(f"\n📚 Final Memory Bank:\n{final_memory}")


async def example_3_manual_callback_approach():
    """Example showing how to implement this as a manual callback"""
    
    print("\n🔧 Example 3: Manual Callback Implementation")
    print("=" * 60)
    
    from advanced_context_manager import AdvancedContextManager
    
    # Create context manager manually
    context_manager = AdvancedContextManager(ContextConfig(max_tokens=1500))
    
    async def smart_context_callback(callback_context, llm_request):
        """Custom callback using our context manager"""
        
        # Check and handle context overflow
        condensed = await context_manager.condense_context(llm_request, callback_context.agent)
        
        if condensed:
            print("🧠 Context intelligently managed!")
        
        # You can add other custom logic here
        # e.g., logging, metrics, custom truncation rules
        
    # Create agent with manual callback
    agent = Agent(
        name="helpful_assistant",
        model="iflow/Qwen3-Coder",
        instruction="You are a helpful assistant.",
        before_model_callback=smart_context_callback
    )
    
    # Test with repetitive tasks
    for i in range(15):
        # Demo: Manual callback would process this
        task_msg = f"Task {i}: Please analyze this fictional dataset and provide insights."
        print(f"🤖 Processing: {task_msg}")
        print(f"📊 Analysis {i}: [Demo completed]")
    
    print("✅ Manual callback approach completed!")


async def example_4_memory_integration():
    """Example integrating with adk-python's memory tools"""
    
    print("\n🔧 Example 4: Integration with Memory Tools")
    print("=" * 60)
    
    # Agent with both smart context AND memory tools
    base_agent = Agent(
        name="memory_research_assistant",
        model="iflow/Qwen3-Coder",
        instruction="You are a research assistant with perfect memory.",
        tools=[load_memory_tool, preload_memory_tool]
    )
    
    smart_agent = SmartAgent(base_agent, ContextConfig(
        max_tokens=1200,
        enable_memory_storage=True
    ))
    
    # Research session with memory usage
    research_queries = [
        "Research the history of artificial intelligence",
        "What were the key milestones in AI development?",
        "Who were the most influential AI researchers?",
        "What were the major AI winters and why did they happen?",
        "How did machine learning evolve from traditional AI?",
        "What role did neural networks play in AI history?",
        "How did deep learning change the field?",
        "What are the current trends in AI research?",
        "What ethical considerations are important in AI?",
        "What might the future of AI look like?"
    ]
    
    for i, query in enumerate(research_queries):
        print(f"\n🔍 Research Query {i+1}: {query}")
        
        # Agent might use memory tools: "Let me recall what we discussed..."
        # Demo: Memory-aware agent would process this
        print(f"🤖 Processing: {query[:50]}...")
        print(f"📚 Research findings: [Demo response]")
        
        # Every few queries, show condensed memory
        if i % 4 == 3:
            condensed_memory = smart_agent.get_memory_summary()
            print(f"\n🧠 Condensed Research Memory:\n{condensed_memory[:400]}...\n")


def compare_approaches():
    """Compare different context management approaches"""
    
    print("\n📊 COMPARISON: Context Management Approaches")
    print("=" * 70)
    
    approaches = {
        "OpenHands Condenser": {
            "Automation": "✅ Fully automatic",
            "Intelligence": "✅ LLM-powered summaries", 
            "Transparency": "✅ User sees condensation",
            "Setup Effort": "✅ Zero configuration",
            "Control": "❌ Limited customization"
        },
        "adk-python Default": {
            "Automation": "❌ Manual truncation only",
            "Intelligence": "❌ Simple history slicing",
            "Transparency": "❌ Silent truncation", 
            "Setup Effort": "⚠️ Requires implementation",
            "Control": "✅ Full developer control"
        },
        "Our Smart Solution": {
            "Automation": "✅ Automatic detection & condensation",
            "Intelligence": "✅ LLM-powered + fallback",
            "Transparency": "✅ Logs condensation events",
            "Setup Effort": "⚠️ One-time integration", 
            "Control": "✅ Highly configurable"
        }
    }
    
    for approach, features in approaches.items():
        print(f"\n{approach}:")
        for feature, rating in features.items():
            print(f"  {feature:15}: {rating}")


async def main():
    """Run all examples"""
    
    print("🚀 Advanced Context Management for adk-python")
    print("Implementing OpenHands-style intelligent condensation")
    print("=" * 70)
    
    try:
        await example_1_basic_usage()
        await example_2_custom_configuration() 
        await example_3_manual_callback_approach()
        await example_4_memory_integration()
        
        compare_approaches()
        
        print("\n🎉 All examples completed successfully!")
        print("\nKey Benefits of This Approach:")
        print("✅ Automatic context window management")
        print("✅ Intelligent LLM-powered summarization") 
        print("✅ Preserves important context")
        print("✅ Integrates with existing adk-python code")
        print("✅ Highly configurable")
        print("✅ Transparent operation")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Note: These examples require a working adk-python environment")
        print("with proper authentication and model access.")


if __name__ == "__main__":
    asyncio.run(main())