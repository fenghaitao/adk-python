"""
INTEGRATION GUIDE: Adding Smart Context Management to Existing adk-python Projects
Step-by-step instructions to upgrade your agents with intelligent context handling
"""

from google.adk import Agent

# ============================================================================
# STEP 1: QUICK INTEGRATION (Minimal Changes)
# ============================================================================

def quick_integration_example():
    """
    Easiest way to add context management to existing code
    Just wrap your existing agent!
    """
    
    # Your existing adk-python code:
    # from google.adk import Agent
    agent = Agent(name="my_agent", model="gemini-2.0-flash")
    
    # NEW: Just add these 3 lines:
    from advanced_context_manager import SmartAgent, ContextConfig
    
    # Wrap your existing agent
    smart_agent = SmartAgent(agent, ContextConfig(max_tokens=8000))
    
    # Use exactly the same as before - context management is now automatic!
    # response = await smart_agent.send_message("Long conversation...")
    
    print("✅ 3-line integration: Your agent now has intelligent context management!")


# ============================================================================
# STEP 2: CALLBACK INTEGRATION (For Existing Callbacks)
# ============================================================================

def callback_integration_example():
    """
    If you already have before_model_callback, integrate with it
    """
    
    from advanced_context_manager import AdvancedContextManager, ContextConfig
    
    # Your existing callback
    async def my_existing_callback(callback_context, llm_request):
        # Your existing logic here
        print("Running my custom logic...")
        # e.g., logging, metrics, custom headers, etc.
    
    # Create context manager
    context_manager = AdvancedContextManager(ContextConfig())
    
    # NEW: Enhanced callback that combines your logic + context management
    async def enhanced_callback(callback_context, llm_request):
        # 1. Run your existing logic first
        await my_existing_callback(callback_context, llm_request)
        
        # 2. Add intelligent context management
        condensed = await context_manager.condense_context(llm_request, callback_context.agent)
        if condensed:
            print("🧠 Context intelligently condensed!")
    
    # Use the enhanced callback
    agent = Agent(
        name="enhanced_agent",
        model="gemini-2.0-flash",
        before_model_callback=enhanced_callback
    )
    
    print("✅ Enhanced your existing callback with context management!")


# ============================================================================
# STEP 3: PRODUCTION CONFIGURATION
# ============================================================================

def production_configuration_example():
    """
    Production-ready configuration with proper settings
    """
    
    from advanced_context_manager import SmartAgent, ContextConfig
    
    # Production configuration
    production_config = ContextConfig(
        max_tokens=7500,                    # Conservative limit (leave room for response)
        keep_system_messages=3,             # Preserve system context
        keep_recent_turns=12,               # Keep substantial recent history
        summarization_model="gemini-2.0-flash",  # Fast, cost-effective for summaries
        enable_memory_storage=True          # Enable for debugging/analysis
    )
    
    # Create production agent
    base_agent = Agent(
        name="production_agent",
        model="gemini-2.0-flash",
        instruction="You are a production AI assistant...",
        tools=[],  # Your production tools
    )
    
    production_agent = SmartAgent(base_agent, production_config)
    
    print("✅ Production-ready agent with intelligent context management!")
    return production_agent


# ============================================================================
# STEP 4: MIGRATION FROM EXISTING TRUNCATION
# ============================================================================

def migrate_from_existing_truncation():
    """
    Replace simple truncation with intelligent condensation
    """
    
    # OLD: Simple truncation (loses context)
    def old_truncation_callback(n_recent_turns=5):
        async def callback(callback_context, llm_request):
            user_indexes = [i for i, content in enumerate(llm_request.contents) 
                           if content.role == 'user']
            if len(user_indexes) > n_recent_turns:
                suffix_idx = user_indexes[-n_recent_turns]
                llm_request.contents = llm_request.contents[suffix_idx:]
        return callback
    
    # NEW: Intelligent condensation (preserves context)
    from advanced_context_manager import SmartAgent, ContextConfig
    
    # Replace old agent
    # old_agent = Agent(before_model_callback=old_truncation_callback(5))
    
    new_agent = SmartAgent(
        Agent(name="migrated_agent", model="gemini-2.0-flash"),
        ContextConfig(keep_recent_turns=5)  # Same behavior but smarter
    )
    
    print("✅ Migrated from simple truncation to intelligent condensation!")


# ============================================================================
# STEP 5: DEBUGGING AND MONITORING
# ============================================================================

def debugging_and_monitoring_example():
    """
    Add logging and monitoring to track context management
    """
    
    import logging
    from advanced_context_manager import SmartAgent, ContextConfig
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("context_management")
    
    # Enhanced config with monitoring
    class MonitoredContextConfig(ContextConfig):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.condensation_count = 0
            self.total_tokens_saved = 0
    
    # Custom context manager with monitoring
    class MonitoredSmartAgent(SmartAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logger
            
        async def _smart_context_callback(self, callback_context, llm_request):
            original_tokens = self.context_manager.estimate_tokens(llm_request.contents)
            
            # Run condensation
            await super()._smart_context_callback(callback_context, llm_request)
            
            # Log metrics
            new_tokens = self.context_manager.estimate_tokens(llm_request.contents)
            if new_tokens < original_tokens:
                tokens_saved = original_tokens - new_tokens
                self.logger.info(f"Context condensed: {original_tokens} → {new_tokens} tokens (saved {tokens_saved})")
    
    # Use monitored agent
    config = MonitoredContextConfig(max_tokens=8000)
    agent = MonitoredSmartAgent(Agent(name="monitored_agent", model="gemini-2.0-flash"), config)
    
    print("✅ Added comprehensive monitoring to context management!")


# ============================================================================
# STEP 6: TESTING FRAMEWORK
# ============================================================================

def testing_framework_example():
    """
    Test framework to validate context management behavior
    """
    
    import asyncio
    from advanced_context_manager import SmartAgent, ContextConfig
    
    async def test_context_management():
        """Test that context management works correctly"""
        
        # Create agent with very low token limit for testing
        test_agent = SmartAgent(
            Agent(model="gemini-2.0-flash"),
            ContextConfig(max_tokens=500, keep_recent_turns=2)
        )
        
        # Test 1: Normal conversation (should not condense)
        response1 = await test_agent.send_message("Hello")
        assert len(response1) > 0, "Agent should respond normally"
        
        # Test 2: Long conversation (should trigger condensation)
        long_messages = ["Tell me about " + topic for topic in [
            "artificial intelligence", "machine learning", "deep learning",
            "neural networks", "computer vision", "natural language processing",
            "robotics", "data science", "statistics", "mathematics"
        ]]
        
        condensation_occurred = False
        for msg in long_messages:
            response = await test_agent.send_message(msg)
            if "condensed" in test_agent.get_memory_summary().lower():
                condensation_occurred = True
                break
        
        assert condensation_occurred, "Condensation should have occurred"
        
        # Test 3: Memory preservation
        memory_summary = test_agent.get_memory_summary()
        assert len(memory_summary) > 0, "Memory should be preserved"
        
        print("✅ All context management tests passed!")
    
    # Run tests
    # asyncio.run(test_context_management())


# ============================================================================
# STEP 7: COMPLETE EXAMPLE - BEFORE & AFTER
# ============================================================================

def complete_before_after_example():
    """
    Complete example showing before and after integration
    """
    
    print("📋 BEFORE & AFTER COMPARISON")
    print("=" * 50)
    
    # BEFORE: Standard adk-python (context overflow risk)
    print("\n❌ BEFORE (Standard adk-python):")
    print("""
    from google.adk.agent import Agent
    
    agent = Agent(
        model="gemini-2.0-flash",
        system_message="You are a helpful assistant.",
        tools=[my_tools]
    )
    
    # Risk: Long conversations will eventually fail
    for i in range(100):  # This will break at some point!
        response = await agent.send_message(f"Task {i}")
    """)
    
    # AFTER: With smart context management
    print("\n✅ AFTER (With Smart Context Management):")
    print("""
    from google.adk.agent import Agent
    from advanced_context_manager import SmartAgent, ContextConfig
    
    base_agent = Agent(
        model="gemini-2.0-flash", 
        system_message="You are a helpful assistant.",
        tools=[my_tools]
    )
    
    # Wrap with intelligent context management
    agent = SmartAgent(base_agent, ContextConfig(max_tokens=8000))
    
    # Benefit: Infinite conversations with preserved context
    for i in range(1000):  # This works indefinitely!
        response = await agent.send_message(f"Task {i}")
        # Context automatically managed behind the scenes
    """)
    
    print("\n🎯 KEY BENEFITS:")
    print("✅ Zero context overflow errors")
    print("✅ Intelligent context preservation") 
    print("✅ Automatic operation")
    print("✅ Memory of important information")
    print("✅ Minimal code changes required")


# ============================================================================
# MAIN INTEGRATION CHECKLIST
# ============================================================================

def integration_checklist():
    """Checklist for integrating context management"""
    
    print("\n📋 INTEGRATION CHECKLIST")
    print("=" * 40)
    print("□ Copy context management files to your project")
    print("□ Install required dependencies (tiktoken)")
    print("□ Choose integration approach (wrapper vs callback)")
    print("□ Configure ContextConfig for your use case")
    print("□ Test with a long conversation")
    print("□ Add logging/monitoring if needed")
    print("□ Update your documentation")
    print("□ Deploy and monitor in production")
    
    print("\n🚀 QUICK START (Copy-Paste Ready):")
    print("""
# 1. Add to your imports:
from advanced_context_manager import SmartAgent, ContextConfig

# 2. Wrap your existing agent:
smart_agent = SmartAgent(your_existing_agent, ContextConfig(max_tokens=8000))

# 3. Use exactly as before:
response = await smart_agent.send_message("Your message...")

# That's it! Context management is now automatic.
""")


if __name__ == "__main__":
    print("🔧 ADK-PYTHON CONTEXT MANAGEMENT INTEGRATION GUIDE")
    print("=" * 60)
    
    quick_integration_example()
    callback_integration_example()
    production_configuration_example()
    migrate_from_existing_truncation()
    debugging_and_monitoring_example()
    testing_framework_example()
    complete_before_after_example()
    integration_checklist()
    
    print("\n🎉 Integration guide complete!")
    print("Your adk-python agents now have OpenHands-style intelligent context management!")
