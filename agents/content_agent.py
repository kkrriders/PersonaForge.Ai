"""
Content Agent - Generates LinkedIn post content, captions, and ideas
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.settings import settings

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentAgent")
        self.post_templates = {
            "mini_project": "project_showcase",
            "main_project": "detailed_project_analysis", 
            "capstone": "comprehensive_achievement",
            "insight": "thought_leadership",
            "achievement": "milestone_celebration"
        }
    
    def get_system_prompt(self) -> str:
        return """You are an expert LinkedIn content creator specializing in professional posts that drive engagement. 

        Your responsibilities:
        1. Generate compelling LinkedIn posts that align with the user's professional brand
        2. Adapt tone and style based on the user's previous posts and preferences
        3. Create content that showcases expertise and builds thought leadership
        4. Include relevant hashtags and calls-to-action
        5. Optimize for LinkedIn's algorithm and engagement patterns

        Post Types:
        - Mini Projects: Highlight quick wins, tools, or techniques learned
        - Main Projects: Deep dive into significant work with results and insights
        - Capstone Projects: Comprehensive achievement posts with impact metrics
        - Insights: Share industry observations and thought leadership
        - Achievements: Celebrate milestones and recognition

        Guidelines:
        - Keep posts between 150-1500 characters for optimal engagement
        - Use storytelling techniques with clear structure: hook, context, insights, call-to-action
        - Include 3-5 relevant hashtags
        - Make posts scannable with line breaks and emojis (when appropriate)
        - Focus on value delivery to the professional community"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LinkedIn post content based on input parameters
        """
        if not self.validate_input(input_data, ["user_context"]):
            return {"error": "Missing required user_context"}
        
        try:
            user_context = input_data["user_context"]
            post_type = user_context.get("post_type", "general")
            
            # Analyze previous posts for tone and style
            previous_posts = input_data.get("previous_posts", [])
            user_style = self._analyze_user_style(previous_posts, user_context)
            
            # Generate post content
            content_prompt = self._build_content_prompt(user_context, user_style, post_type)
            
            generated_content = await self.call_ollama(
                prompt=content_prompt,
                system_prompt=self.get_system_prompt()
            )
            
            # Parse and structure the response
            structured_content = self._structure_content_response(generated_content, user_context)
            
            # Generate engagement predictions
            engagement_prediction = self._predict_engagement(structured_content, user_style)
            
            result = {
                "content": structured_content["post_text"],
                "hashtags": structured_content["hashtags"],
                "call_to_action": structured_content["call_to_action"],
                "engagement_prediction": engagement_prediction,
                "post_id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "post_type": post_type
            }
            
            logger.info(f"Generated content for post type: {post_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return {"error": str(e)}
    
    def _build_content_prompt(self, user_context: Dict[str, Any], user_style: Dict[str, Any], post_type: str) -> str:
        """
        Build a detailed prompt for content generation
        """
        prompt = f"""Generate a LinkedIn post with the following requirements:

        USER CONTEXT:
        - Current Work/Project: {user_context.get('current_work', 'Not specified')}
        - Skills to Showcase: {', '.join(user_context.get('skills', []))}
        - Career Goals: {user_context.get('career_goals', 'Not specified')}
        - Industry: {user_context.get('industry', 'Technology')}
        - Experience Level: {user_context.get('experience_level', 'Mid-level')}

        POST TYPE: {post_type}

        USER STYLE PREFERENCES (based on analysis):
        - Tone: {user_style.get('tone', 'Professional')}
        - Length Preference: {user_style.get('avg_length', 'Medium')}
        - Emoji Usage: {user_style.get('emoji_usage', 'Minimal')}
        - Hashtag Count: {user_style.get('hashtag_count', '3-5')}

        TONE-SPECIFIC WRITING GUIDELINES:
        {self._get_tone_guidelines(user_style.get('tone', 'Professional'))}

        SPECIFIC REQUIREMENTS:
        """
        
        # Handle custom prompts for general posts
        if post_type == "general" and user_context.get('custom_prompt'):
            prompt += f"""
        - CUSTOM USER PROMPT: {user_context['custom_prompt']}
        - Focus specifically on the topic and requirements mentioned in the custom prompt
        - Maintain professional tone while addressing the specific content requested
        - Ensure the post directly addresses what the user asked for
        """
        elif post_type == "mini_project":
            prompt += """
        MINI PROJECT POST STYLE:
        - Start with a relatable problem: "Ever struggled with [problem]?" or "I spent way too much time on [task] until I found..."
        - Share your quick win discovery moment: "Then I discovered...", "Game changer:", "Plot twist:"
        - Include the practical solution with step-by-step approach
        - Add a humble brag moment: "Saved me 2 hours a day" or "Reduced errors by 80%"
        - End with: "What's your go-to hack for [related problem]?" 
        - Use casual, excited tone: "This blew my mind!", "Why didn't I try this sooner?"
        - Include relevant hashtags like #ProductivityHack #TechTip #QuickWin
        """
        elif post_type == "main_project":
            prompt += """
        - Detail a significant project with clear business impact
        - Include challenges faced and how they were overcome
        - Share quantifiable results where possible
        - Provide actionable insights for the community
        """
        elif post_type == "capstone":
            prompt += """
        - Showcase a major achievement or completed initiative
        - Include comprehensive results and impact metrics
        - Reflect on lessons learned throughout the journey
        - Position as thought leadership content
        """
        elif post_type == "insight":
            prompt += """
        - Share an industry observation or trend analysis
        - Provide unique perspective or contrarian viewpoint
        - Include personal experience or case study
        - Encourage discussion and engagement
        """
        elif post_type == "achievement":
            prompt += """
        - Celebrate a professional milestone or recognition
        - Show gratitude and acknowledge support from others
        - Share the journey and key learnings
        - Inspire others with the story
        """
        
        prompt += """
        
        RESPONSE FORMAT (JSON):
        {
            "post_text": "The main LinkedIn post content",
            "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
            "call_to_action": "What action you want readers to take",
            "key_points": ["main point 1", "main point 2", "main point 3"]
        }
        """
        
        return prompt
    
    def _analyze_user_style(self, previous_posts: List[Dict[str, Any]], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user's previous posts to determine their style preferences
        """
        # Get tone from user context if available (from manual content creation)
        selected_tone = None
        if user_context:
            selected_tone = user_context.get("tone") or user_context.get("preferred_tone")
        
        if not previous_posts:
            return {
                "tone": selected_tone or "Professional",
                "avg_length": "Medium",
                "emoji_usage": "Minimal", 
                "hashtag_count": "3-5",
                "preferred_topics": []
            }
        
        # Analyze patterns from previous posts
        total_length = sum(len(post.get("content", "")) for post in previous_posts)
        avg_length = total_length // len(previous_posts) if previous_posts else 500
        
        length_category = "Short" if avg_length < 300 else "Medium" if avg_length < 800 else "Long"
        
        return {
            "tone": selected_tone or "Professional",
            "avg_length": length_category,
            "emoji_usage": "Strategic",
            "hashtag_count": "3-5",
            "preferred_topics": self._extract_common_topics(previous_posts)
        }
    
    def _extract_common_topics(self, previous_posts: List[Dict[str, Any]]) -> List[str]:
        """Extract common topics from previous posts"""
        # Simplified topic extraction
        common_topics = ["technology", "innovation", "leadership", "growth"]
        return common_topics[:3]
    
    def _structure_content_response(self, generated_content: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and structure the AI-generated content response
        """
        try:
            # Try to parse as JSON first
            if "{" in generated_content and "}" in generated_content:
                start = generated_content.find("{")
                end = generated_content.rfind("}") + 1
                json_str = generated_content[start:end]
                parsed = json.loads(json_str)
                return parsed
        except:
            pass
        
        # Fallback: structure manually
        lines = generated_content.strip().split("\n")
        post_text = generated_content.strip()
        
        # Extract hashtags if present
        hashtags = []
        for line in lines:
            if "#" in line:
                tags = [tag.strip() for tag in line.split() if tag.startswith("#")]
                hashtags.extend(tags)
        
        if not hashtags:
            hashtags = settings.default_hashtags[:3]
        
        return {
            "post_text": post_text,
            "hashtags": hashtags[:5],
            "call_to_action": "What are your thoughts on this? Share your experience in the comments!",
            "key_points": ["Innovation", "Growth", "Learning"]
        }
    
    def _predict_engagement(self, content: Dict[str, Any], user_style: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict engagement metrics based on content analysis
        """
        post_length = len(content.get("post_text", ""))
        hashtag_count = len(content.get("hashtags", []))
        has_cta = bool(content.get("call_to_action", ""))
        
        # Simple engagement prediction algorithm
        base_score = 50
        
        # Length optimization (300-800 characters optimal)
        if 300 <= post_length <= 800:
            base_score += 20
        elif post_length < 150:
            base_score -= 10
        elif post_length > 1200:
            base_score -= 15
        
        # Hashtag optimization (3-5 hashtags optimal)
        if 3 <= hashtag_count <= 5:
            base_score += 15
        elif hashtag_count > 10:
            base_score -= 20
        
        # Call-to-action bonus
        if has_cta:
            base_score += 10
        
        return {
            "predicted_likes": max(base_score, 10),
            "predicted_comments": max(base_score // 5, 2),
            "predicted_shares": max(base_score // 10, 1),
            "engagement_score": min(base_score, 100),
            "optimization_suggestions": self._get_optimization_suggestions(content, base_score)
        }
    
    def _get_optimization_suggestions(self, content: Dict[str, Any], score: int) -> List[str]:
        """Generate suggestions to improve post engagement"""
        suggestions = []
        
        post_length = len(content.get("post_text", ""))
        if post_length < 150:
            suggestions.append("Consider adding more context or details to reach optimal length")
        elif post_length > 1200:
            suggestions.append("Consider shortening the post for better readability")
        
        if len(content.get("hashtags", [])) < 3:
            suggestions.append("Add 2-3 more relevant hashtags to improve discoverability")
        
        if not content.get("call_to_action"):
            suggestions.append("Add a call-to-action to encourage audience engagement")
        
        if score < 60:
            suggestions.append("Consider adding a personal story or specific example")
            suggestions.append("Include a question to spark discussion")
        
        return suggestions
    
    def _get_tone_guidelines(self, tone: str) -> str:
        """Get specific writing guidelines for each tone with human touches"""
        tone_guides = {
            "Professional": """
            - Start with industry-relevant observations: "In today's business landscape..." or "Industry data shows..."
            - Use credible language: "Based on my experience...", "Our analysis reveals..."
            - Include metrics and concrete examples
            - Reference industry standards and best practices
            - End with professional questions: "How is your organization approaching this?" "What strategies have worked for your team?"
            - Maintain authoritative but approachable voice
            - Use minimal emojis (1-2 strategic ones)
            """,
            
            "Conversational": """
            - Start like talking to a friend: "You know what I've been thinking about lately?" or "Can we talk about something real quick?"
            - Use everyday language and contractions: "I've", "don't", "here's the thing"
            - Include personal anecdotes: "This happened to me last week..." or "My colleague just told me..."
            - Ask direct questions: "Anyone else dealing with this?" or "Am I the only one who thinks...?"
            - Use casual phrases: "Honestly", "Real talk", "Here's the deal"
            - Include moderate emojis (3-5) that feel natural
            - End with friendly CTAs: "Let's chat about this in the comments!"
            """,
            
            "Educational": """
            - Structure as a mini-lesson: "Let me break this down..." or "Here's what you need to know about..."
            - Use numbered lists and clear steps
            - Include "did you know?" facts and statistics
            - Explain the "why" behind concepts: "The reason this works is..."
            - Use teaching phrases: "Think of it this way...", "To put it simply...", "The key takeaway is..."
            - Include actionable tips: "Try this:", "Next time, remember to..."
            - End with learning-focused questions: "What would you add to this list?" or "What's been your experience with this?"
            - Use strategic emojis for emphasis (📊, 💡, ✅)
            """,
            
            "Inspirational": """
            - Start with vision or possibility: "Imagine if...", "What if I told you...", "Picture this..."
            - Share transformation stories: "Six months ago, I never thought...", "From struggle to success..."
            - Use empowering language: "You have the power to...", "Don't let anyone tell you..."
            - Include motivational phrases: "Keep pushing", "Never give up", "Your time is now"
            - Share vulnerability: "I failed multiple times before...", "There were days I wanted to quit..."
            - End with calls to action: "Start today", "Take that first step", "Believe in yourself"
            - Use uplifting emojis: 🚀, ⭐, 💪, 🌟
            - Focus on growth mindset and possibility
            """,
            
            "Thought-provoking": """
            - Start with contrarian views: "Unpopular opinion:", "What if everything we know about X is wrong?"
            - Ask challenging questions: "Why do we still...", "What if instead of X, we tried Y?"
            - Present paradoxes: "The more we..., the less we...", "Success isn't about..., it's about..."
            - Challenge assumptions: "Everyone says X, but I think...", "The conventional wisdom is..."
            - Use philosophical angles: "This made me question...", "It got me thinking about..."
            - Include counter-intuitive insights: "The opposite might be true...", "What seems obvious actually..."
            - End with open-ended questions that spark debate: "Change my mind", "What am I missing here?"
            - Use minimal but strategic emojis: 🤔, 💭
            """,
            
            "Casual": """
            - Start super relaxed: "So this happened today...", "Quick story time...", "Okay, real talk..."
            - Use informal language: "gonna", "kinda", "pretty cool", "totally"
            - Include spontaneous thoughts: "Random thought:", "Just realized...", "Quick observation..."
            - Share everyday moments: "Coffee chat with my manager led to...", "Overheard in the office elevator..."
            - Use humor when appropriate: "Plot twist:", "Spoiler alert:", "Fun fact:"
            - Keep it light and relatable
            - Use frequent emojis (4-6) naturally: 😄, 🤷‍♀️, 💯
            - End casually: "Thoughts?", "Anyone else?", "Just me? 😂"
            """,
            
            "Authoritative": """
            - Open with definitive statements: "Here's what the data actually shows...", "After 10 years in this field..."
            - Use expert positioning: "In my role as...", "Having led dozens of projects like this..."
            - Include credentials or experience: "Based on our research with 500+ companies..."
            - Present clear frameworks: "There are three key factors...", "The methodology is straightforward..."
            - Use confident language: "I recommend", "The solution is", "This approach works because"
            - Provide concrete evidence: specific numbers, case studies, proven results
            - Minimal emojis, focus on substance over style
            - End with expert recommendations: "My advice:", "Here's what you should do:"
            """,
            
            "Storytelling": """
            - Start with a scene: "Picture this: It's 2 AM, I'm staring at my computer screen..."
            - Use narrative structure: beginning, middle, end with a clear arc
            - Include dialogue: "My boss said...", "The client looked at me and said..."
            - Create suspense: "Little did I know...", "What happened next changed everything..."
            - Use sensory details: "The tension in the room was palpable...", "I could feel my heart racing..."
            - Include plot twists: "But then...", "Suddenly...", "The unexpected happened..."
            - Share the journey: struggles, setbacks, breakthroughs, lessons
            - End with the moral: "The lesson?", "What I learned:", "Here's the takeaway:"
            - Use emojis that enhance the story: 📖, 🎭, ✨
            """
        }
        
        return tone_guides.get(tone, tone_guides["Professional"])
    
    async def analyze_posting_patterns(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's posting patterns and provide insights
        """
        posts = input_data.get("posts", [])
        user_id = input_data.get("user_id", "")
        
        if not posts:
            return {
                "posting_frequency": "No data available",
                "preferred_topics": [],
                "best_performing_posts": [],
                "recommendations": ["Start by posting consistently", "Focus on your expertise areas"]
            }
        
        analysis = {
            "posting_frequency": f"{len(posts)} posts analyzed",
            "preferred_topics": self._extract_common_topics(posts),
            "avg_engagement": self._calculate_avg_engagement(posts),
            "best_performing_posts": self._identify_top_posts(posts),
            "recommendations": self._generate_content_recommendations(posts)
        }
        
        return analysis
    
    def _calculate_avg_engagement(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average engagement metrics"""
        if not posts:
            return {"likes": 0, "comments": 0, "shares": 0}
        
        total_likes = sum(post.get("likes", 0) for post in posts)
        total_comments = sum(post.get("comments", 0) for post in posts)
        total_shares = sum(post.get("shares", 0) for post in posts)
        
        return {
            "likes": total_likes / len(posts),
            "comments": total_comments / len(posts),
            "shares": total_shares / len(posts)
        }
    
    def _identify_top_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify top-performing posts"""
        if not posts:
            return []
        
        # Sort by total engagement (likes + comments*2 + shares*3)
        scored_posts = []
        for post in posts:
            score = (post.get("likes", 0) + 
                    post.get("comments", 0) * 2 + 
                    post.get("shares", 0) * 3)
            scored_posts.append({"post": post, "score": score})
        
        scored_posts.sort(key=lambda x: x["score"], reverse=True)
        return [item["post"] for item in scored_posts[:3]]
    
    def _generate_content_recommendations(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Generate personalized content recommendations"""
        recommendations = [
            "Maintain consistent posting schedule",
            "Include more personal stories and experiences",
            "Ask questions to encourage engagement",
            "Share insights from your recent projects",
            "Use 3-5 relevant hashtags per post"
        ]
        
        return recommendations[:4]