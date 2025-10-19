"""
Context Management Agent Example for ADK-Python

This example demonstrates how to create an agent with intelligent context window management
that automatically condenses conversation history when approaching token limits.

Features:
- Automatic context condensation using LLM-powered summarization
- Smart preservation of system messages and recent conversation
- Memory storage for debugging and analysis
- Production-ready configuration options

Usage:
    python agent.py
"""

import asyncio
import os
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.load_memory_tool import load_memory_tool
from advanced_context_manager import SmartAgent, ContextConfig


async def create_context_managed_agent() -> SmartAgent:
    """Create an agent with intelligent context management"""
    
    # Configure context management
    context_config = ContextConfig(
        max_tokens=8000,                    # Trigger condensation at 8K tokens
        keep_system_messages=2,             # Always preserve first 2 system messages
        keep_recent_turns=8,                # Keep last 8 conversation turns
        summarization_model="gemini-2.0-flash",  # Model for creating summaries
        enable_memory_storage=True          # Store summaries for analysis
    )
    
    # Create base agent
    base_agent = LlmAgent(
        model="gemini-2.0-flash",
        system_instructions="""You are an expert software development assistant with perfect memory management.
        
You help developers with:
- Code analysis and debugging
- Architecture design
- Best practices recommendations
- Technical problem solving

You maintain context across long conversations and can reference previous discussions.""",
        tools=[load_memory_tool]  # Add memory tools for enhanced context
    )
    
    # Wrap with smart context management
    smart_agent = SmartAgent(base_agent, context_config)
    
    print("✅ Created agent with intelligent context management")
    print(f"📊 Configuration: Max {context_config.max_tokens} tokens, "
          f"keep {context_config.keep_recent_turns} recent turns")
    
    return smart_agent


async def demo_long_conversation(agent: SmartAgent):
    """Demonstrate the agent handling a long technical conversation"""
    
    print("\n🚀 Starting long conversation demo...")
    print("This will simulate a multi-session development discussion")
    print("=" * 60)
    
    # Simulate a comprehensive software development discussion
    development_topics = [
        "I'm building a microservices architecture for an e-commerce platform. Where should I start?",
        "What patterns should I use for inter-service communication?",
        "How do I handle distributed transactions across services?",
        "What's the best approach for service discovery and load balancing?",
        "How should I implement authentication and authorization across services?",
        "What monitoring and observability tools do you recommend?",
        "How do I handle database design in a microservices architecture?",
        "What's the best strategy for handling failures and implementing circuit breakers?",
        "How do I manage configuration across multiple services?",
        "What CI/CD practices work best for microservices?",
        "How do I implement proper logging and distributed tracing?",
        "What's the best approach for API versioning in microservices?",
        "How do I handle data consistency across services?",
        "What security considerations are specific to microservices?",
        "How do I optimize performance in a distributed system?",
        "What's the best approach for testing microservices?",
        "How do I manage dependencies between services?",
        "What's the best strategy for deployment and rollbacks?",
        "How do I handle cross-cutting concerns like caching?",
        "What's the best approach for event-driven architecture?"
    ]
    
    conversation_summary = []
    
    for i, topic in enumerate(development_topics, 1):
        print(f"\n📝 Turn {i}/20: {topic[:80]}...")
        
        try:
            response = await agent.send_message(topic)
            conversation_summary.append({
                'turn': i,
                'topic': topic,
                'response_length': len(response),
                'condensed': 'condensed' in agent.get_memory_summary().lower()
            })
            
            print(f"🤖 Response: {len(response)} characters")
            
            # Show condensation events
            if i % 5 == 0:
                memory = agent.get_memory_summary()
                if memory and len(memory) > 50:
                    print(f"\n💭 Memory Bank Status:\n{memory[:200]}...\n")
                    
        except Exception as e:
            print(f"❌ Error on turn {i}: {e}")
            break
    
    # Final summary
    print(f"\n📊 CONVERSATION SUMMARY:")
    print(f"✅ Completed {len(conversation_summary)} turns successfully")
    
    condensation_turns = [s for s in conversation_summary if s['condensed']]
    if condensation_turns:
        print(f"🧠 Context condensed {len(condensation_turns)} times")
        print(f"🔄 First condensation at turn {condensation_turns[0]['turn']}")
    else:
        print("🔄 No condensation occurred (conversation within limits)")
    
    avg_response_length = sum(s['response_length'] for s in conversation_summary) / len(conversation_summary)
    print(f"📏 Average response length: {avg_response_length:.0f} characters")
    
    # Show final memory state
    final_memory = agent.get_memory_summary()
    if final_memory:
        print(f"\n📚 Final Memory Bank:\n{final_memory}")


async def demo_context_recovery(agent: SmartAgent):
    """Demonstrate how the agent maintains context after condensation"""
    
    print("\n🔍 Testing context recovery after condensation...")
    print("=" * 50)
    
    # Add some context to remember
    await agent.send_message("Remember that I'm working on an e-commerce platform called 'ShopFast' using Python and PostgreSQL.")
    await agent.send_message("The main services are: user-service, product-service, order-service, and payment-service.")
    await agent.send_message("We're using Docker containers and Kubernetes for deployment.")
    
    # Fill up context with many messages to trigger condensation
    for i in range(15):
        await agent.send_message(f"Tell me about design pattern number {i} for microservices.")
    
    # Test if early context is preserved
    print("\n🧪 Testing context preservation...")
    recovery_response = await agent.send_message(
        "Can you recall the name of my e-commerce platform and what database I'm using?"
    )
    
    print(f"🔍 Context Recovery Test:")
    print(f"Response: {recovery_response[:300]}...")
    
    if "ShopFast" in recovery_response and "PostgreSQL" in recovery_response:
        print("✅ Context successfully preserved through condensation!")
    else:
        print("⚠️ Some context may have been lost during condensation")


async def main():
    """Main demonstration function"""
    
    print("🎯 ADK-Python Context Management Demo")
    print("Intelligent conversation history management for unlimited sessions")
    print("=" * 70)
    
    try:
        # Create context-managed agent
        agent = await create_context_managed_agent()
        
        # Run demonstrations
        await demo_long_conversation(agent)
        await demo_context_recovery(agent)
        
        print("\n🎉 Context management demo completed successfully!")
        print("\nKey Benefits Demonstrated:")
        print("✅ Unlimited conversation length without token errors")
        print("✅ Intelligent context preservation")
        print("✅ Automatic operation with transparency")
        print("✅ Memory of important information across condensations")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure you have:")
        print("- Proper authentication configured")
        print("- Required models available")
        print("- Network access to Google AI services")


if __name__ == "__main__":
    asyncio.run(main())