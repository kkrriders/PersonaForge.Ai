#!/usr/bin/env python3
"""
Test script for custom prompt functionality
"""

import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agent_coordinator import AgentCoordinator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_custom_prompt():
    """Test custom prompt functionality"""
    logger.info("🧪 Testing custom prompt functionality...")
    
    try:
        # Initialize agent coordinator
        agent_coordinator = AgentCoordinator()
        await agent_coordinator.initialize()
        
        # Test data simulating your Agent Context Protocol prompt
        test_context = {
            "user_id": "test_user",
            "post_type": "general",
            "name": "Test User",
            "industry": "Technology",
            "experience_level": "Mid-level",
            "current_work": "Software Development",
            "skills": ["AI", "Protocols", "System Design"],
            "career_goals": "Thought leadership in emerging tech",
            "custom_prompt": "Agent Context Protocol is a proposed standard that defines how agents communicate their contexts state and capabilities to each other in a interoperable way create a professional linkedin post around this ACP Definition that shows my in depth curiosity around this concept",
            "include_image": False
        }
        
        logger.info("📝 Generating post with custom prompt...")
        logger.info(f"Custom prompt: {test_context['custom_prompt'][:100]}...")
        
        # Generate post
        result = await agent_coordinator.generate_complete_post(test_context)
        
        if "error" in result:
            logger.error(f"❌ Test failed: {result['error']}")
            return False
        
        logger.info("✅ Test successful!")
        logger.info("📄 Generated content:")
        logger.info("=" * 60)
        logger.info(result.get('content', ''))
        logger.info("=" * 60)
        
        # Check if the content mentions Agent Context Protocol
        content = result.get('content', '').lower()
        if 'agent context protocol' in content or 'acp' in content:
            logger.info("✅ Content correctly addresses Agent Context Protocol!")
            return True
        else:
            logger.warning("⚠️  Content may not be addressing the custom prompt properly")
            logger.warning("Content preview: " + result.get('content', '')[:200])
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    async def main():
        logger.info("🚀 Starting custom prompt test...")
        success = await test_custom_prompt()
        
        if success:
            logger.info("🎉 Custom prompt functionality is working!")
        else:
            logger.info("⚠️  Custom prompt test failed. Check the implementation.")
    
    asyncio.run(main())