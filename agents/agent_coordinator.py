"""
Agent Coordinator - Manages the multi-agent system workflow
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from .content_agent import ContentAgent
from .image_agent import ImageAgent
from .prompt_agent import PromptAgent
try:
    from utils.database import DatabaseManager
except ImportError:
    DatabaseManager = None

logger = logging.getLogger(__name__)

class AgentCoordinator:
    def __init__(self):
        self.content_agent = ContentAgent()
        self.image_agent = ImageAgent()
        self.prompt_agent = PromptAgent()
        self.db_manager = DatabaseManager() if DatabaseManager else None
    
    async def initialize(self):
        """Initialize all agents"""
        logger.info("Initializing Agent Coordinator and all agents")
        # Agents are initialized in their constructors
    
    async def generate_complete_post(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate all agents to generate a complete LinkedIn post
        """
        try:
            logger.info("Starting complete post generation workflow")
            
            # Step 1: Generate structured prompt
            prompt_input = {
                "user_context": user_context,
                "post_type": user_context.get("post_type", "general")
            }
            
            structured_prompt = await self.prompt_agent.process(prompt_input)
            
            # Step 2: Generate content using structured prompt
            content_input = {
                "user_context": user_context,
                "previous_posts": await self._get_previous_posts(user_context.get("user_id"))
            }
            
            content_result = await self.content_agent.process(content_input)
            
            # Step 3: Generate image if needed
            image_result = {}
            if user_context.get("include_image", False):
                image_input = {
                    "post_content": content_result.get("content", ""),
                    "image_type": user_context.get("image_type", "infographic"),
                    "style": user_context.get("image_style", "professional")
                }
                
                image_result = await self.image_agent.process(image_input)
            
            # Step 4: Combine results
            complete_post = {
                "content": content_result.get("content", ""),
                "hashtags": content_result.get("hashtags", []),
                "image_path": image_result.get("image_path", ""),
                "engagement_prediction": content_result.get("engagement_prediction", {}),
                "created_at": content_result.get("created_at", ""),
                "post_id": content_result.get("post_id", "")
            }
            
            # Step 5: Save to database
            await self._save_generated_post(complete_post, user_context)
            
            logger.info("Complete post generation successful")
            return complete_post
            
        except Exception as e:
            logger.error(f"Error in complete post generation: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze user's posting history and preferences
        """
        try:
            previous_posts = await self._get_previous_posts(user_id)
            
            analysis_input = {
                "posts": previous_posts,
                "user_id": user_id
            }
            
            # Use content agent to analyze patterns
            analysis_result = await self.content_agent.analyze_posting_patterns(analysis_input)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing user profile: {str(e)}")
            return {"error": str(e)}
    
    async def _get_previous_posts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's previous posts from database"""
        try:
            if self.db_manager:
                return await self.db_manager.get_posts_by_user(user_id or 'default', limit=10)
            return []
        except Exception as e:
            logger.error(f"Error getting previous posts: {str(e)}")
            return []
    
    async def _save_generated_post(self, post_data: Dict[str, Any], user_context: Dict[str, Any]):
        """Save generated post to database"""
        try:
            if self.db_manager:
                enhanced_post_data = post_data.copy()
                enhanced_post_data['user_id'] = user_context.get('user_id', 'default')
                enhanced_post_data['post_type'] = user_context.get('post_type', 'general')
                await self.db_manager.save_generated_post(enhanced_post_data)
        except Exception as e:
            logger.error(f"Error saving generated post: {str(e)}")
    
    async def get_posting_recommendations(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendations for optimal posting times and content types
        """
        try:
            user_analysis = await self.analyze_user_profile(user_context.get("user_id", ""))
            
            recommendations = {
                "best_posting_times": ["9:00 AM", "12:00 PM", "5:00 PM"],
                "recommended_post_types": ["project_update", "insight_sharing", "achievement"],
                "hashtag_suggestions": ["#ProjectManagement", "#TechInnovation", "#CareerGrowth"],
                "content_themes": user_analysis.get("preferred_themes", [])
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting posting recommendations: {str(e)}")
            return {"error": str(e)}