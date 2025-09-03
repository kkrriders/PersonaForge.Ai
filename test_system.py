#!/usr/bin/env python3
"""
Quick system test for PersonaForge.AI
Tests core functionality without full setup
"""

import sys
import asyncio
import traceback

async def test_imports():
    """Test all major imports"""
    print("🔍 Testing imports...")
    
    try:
        from config.settings import settings
        print("✅ Settings import successful")
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False
    
    try:
        from agents.base_agent import BaseAgent
        print("✅ BaseAgent import successful")
    except Exception as e:
        print(f"❌ BaseAgent import failed: {e}")
        return False
    
    try:
        from agents.content_agent import ContentAgent
        agent = ContentAgent()
        print("✅ ContentAgent creation successful")
    except Exception as e:
        print(f"❌ ContentAgent creation failed: {e}")
        return False
    
    try:
        from utils.database import DatabaseManager
        db = DatabaseManager()
        print("✅ DatabaseManager creation successful")
    except Exception as e:
        print(f"❌ DatabaseManager creation failed: {e}")
        return False
    
    return True

async def test_database():
    """Test database initialization"""
    print("\n🗄️  Testing database...")
    
    try:
        from utils.database import DatabaseManager
        db = DatabaseManager()
        await db.initialize()
        print("✅ Database initialization successful")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

async def test_agent_coordination():
    """Test agent coordinator"""
    print("\n🤖 Testing agent coordination...")
    
    try:
        from agents.agent_coordinator import AgentCoordinator
        coordinator = AgentCoordinator()
        await coordinator.initialize()
        print("✅ Agent coordinator initialization successful")
        return True
    except Exception as e:
        print(f"❌ Agent coordinator failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

async def test_user_input():
    """Test user input handler"""
    print("\n👤 Testing user input handler...")
    
    try:
        from utils.user_input import UserInputHandler
        handler = UserInputHandler()
        print("✅ User input handler creation successful")
        return True
    except Exception as e:
        print(f"❌ User input handler failed: {e}")
        return False

async def test_privacy_manager():
    """Test privacy manager"""
    print("\n🔒 Testing privacy manager...")
    
    try:
        from utils.privacy import PrivacyManager
        privacy = PrivacyManager()
        settings_info = privacy.get_privacy_settings()
        print("✅ Privacy manager creation and settings retrieval successful")
        return True
    except Exception as e:
        print(f"❌ Privacy manager failed: {e}")
        return False

async def test_content_generation():
    """Test basic content generation (without Ollama)"""
    print("\n📝 Testing content generation structure...")
    
    try:
        from agents.content_agent import ContentAgent
        
        agent = ContentAgent()
        
        # Test with minimal input
        test_input = {
            "user_context": {
                "post_type": "general",
                "industry": "Technology",
                "skills": ["Python", "AI"],
                "current_work": "Software Development"
            }
        }
        
        # Test system prompt generation
        system_prompt = agent.get_system_prompt()
        if len(system_prompt) > 100:
            print("✅ System prompt generation successful")
        else:
            print("❌ System prompt too short")
            return False
        
        # Test content prompt building
        user_style = agent._analyze_user_style([])
        content_prompt = agent._build_content_prompt(
            test_input["user_context"], 
            user_style, 
            "general"
        )
        
        if len(content_prompt) > 200:
            print("✅ Content prompt building successful")
        else:
            print("❌ Content prompt too short")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

async def test_image_agent():
    """Test image agent structure"""
    print("\n🖼️  Testing image agent...")
    
    try:
        from agents.image_agent import ImageAgent
        
        agent = ImageAgent()
        
        # Test system prompt
        system_prompt = agent.get_system_prompt()
        if len(system_prompt) > 100:
            print("✅ Image agent system prompt successful")
        else:
            print("❌ Image agent system prompt too short")
            return False
        
        # Test fallback content analysis
        test_content = "This is a test post about Python development and AI innovation."
        analysis = agent._fallback_content_analysis(test_content)
        
        if "main_points" in analysis and "suggested_visual_type" in analysis:
            print("✅ Image content analysis successful")
        else:
            print("❌ Image content analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Image agent test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 PersonaForge.AI System Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Agent Coordination", test_agent_coordination),
        ("User Input", test_user_input),
        ("Privacy Manager", test_privacy_manager),
        ("Content Generation", test_content_generation),
        ("Image Agent", test_image_agent)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if await test_func():
                passed += 1
            else:
                print(f"❌ {name} test failed")
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check error messages above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        sys.exit(1)