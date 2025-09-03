

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PromptAgent(BaseAgent):
    def __init__(self):
        super().__init__("PromptAgent")
        self.prompt_templates = self._load_prompt_templates()
    
    def get_system_prompt(self) -> str:
        return """You are an expert prompt engineer specializing in creating structured, effective prompts for LinkedIn content generation.

        Your responsibilities:
        1. Analyze user context and requirements to create optimal prompts
        2. Structure prompts for maximum clarity and output quality
        3. Include relevant constraints and guidelines
        4. Optimize prompts for the specific AI model being used
        5. Ensure prompts drive consistent, professional content

        Prompt Structure Guidelines:
        - Clear context and background information
        - Specific role definition for the AI
        - Detailed requirements and constraints
        - Output format specifications
        - Examples when helpful
        - Success criteria definition"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured prompt based on user context and requirements
        """
        if not self.validate_input(input_data, ["user_context"]):
            return {"error": "Missing required user_context"}
        
        try:
            user_context = input_data["user_context"]
            post_type = user_context.get("post_type", "general")
            
            # Handle custom prompts directly without using templates
            if post_type == "general" and user_context.get('custom_prompt'):
                custom_content = user_context['custom_prompt']
                structured_prompt = f"""Create a professional LinkedIn post based on this specific request:

USER REQUEST: {custom_content}

REQUIREMENTS:
- Write in a natural, engaging LinkedIn style that gets high engagement
- Start with a compelling hook (question, analogy, or surprising statement)
- Include personal elements ("I've been thinking about...", "In my experience...")
- Focus specifically on the topic mentioned in the request
- Show genuine curiosity and expertise about the subject
- Use storytelling and metaphors to make complex topics accessible
- Structure: Hook → Personal connection → Insights → Benefits → Questions → CTA
- Include thought-provoking questions that encourage comments
- Use strategic emojis (not overwhelming)
- Add relevant, specific hashtags
- End with a clear call-to-action asking for engagement
- Keep paragraphs short for easy mobile reading

IMPORTANT: Address the exact topic and requirements mentioned in the user request above. Do not generate generic content."""
            else:
                # Select appropriate template for structured posts
                template = self._select_template(post_type, user_context)
                
                # Generate structured prompt
                structured_prompt = self._build_structured_prompt(template, user_context)
            
            # Optimize prompt for clarity and effectiveness
            optimized_prompt = await self._optimize_prompt(structured_prompt)
            
            result = {
                "structured_prompt": optimized_prompt,
                "prompt_type": post_type,
                "template_used": template["name"],
                "optimization_applied": True,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated structured prompt for type: {post_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error in prompt generation: {str(e)}")
            return {"error": str(e)}
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """
        Load predefined prompt templates for different content types
        """
        return {
            "mini_project": {
                "name": "Mini Project Showcase",
                "structure": [
                    "context_setting",
                    "project_description", 
                    "methodology_brief",
                    "results_summary",
                    "learnings",
                    "call_to_action"
                ],
                "tone": "enthusiastic_professional",
                "length": "medium",
                "focus": "practical_value"
            },
            "main_project": {
                "name": "Main Project Deep Dive",
                "structure": [
                    "problem_statement",
                    "approach_overview",
                    "implementation_details",
                    "challenges_overcome",
                    "quantified_results",
                    "broader_implications",
                    "community_value"
                ],
                "tone": "authoritative_insightful",
                "length": "long",
                "focus": "thought_leadership"
            },
            "capstone": {
                "name": "Capstone Achievement",
                "structure": [
                    "milestone_announcement",
                    "journey_overview",
                    "key_accomplishments",
                    "impact_metrics",
                    "lessons_learned",
                    "future_vision",
                    "gratitude_acknowledgment"
                ],
                "tone": "celebratory_reflective",
                "length": "long",
                "focus": "inspiration_leadership"
            },
            "insight": {
                "name": "Industry Insight",
                "structure": [
                    "observation_hook",
                    "context_background",
                    "analysis_framework",
                    "personal_perspective",
                    "supporting_evidence",
                    "actionable_takeaways",
                    "discussion_starter"
                ],
                "tone": "thoughtful_analytical",
                "length": "medium",
                "focus": "thought_leadership"
            },
            "achievement": {
                "name": "Achievement Celebration",
                "structure": [
                    "announcement",
                    "journey_context",
                    "support_acknowledgment",
                    "key_milestones",
                    "personal_growth",
                    "inspiration_message",
                    "forward_looking"
                ],
                "tone": "grateful_inspiring",
                "length": "medium",
                "focus": "community_inspiration"
            },
            "general": {
                "name": "General Professional Post",
                "structure": [
                    "engaging_hook",
                    "main_content",
                    "personal_connection",
                    "value_proposition",
                    "call_to_action"
                ],
                "tone": "professional_engaging",
                "length": "medium",
                "focus": "community_value"
            }
        }
    
    def _select_template(self, post_type: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate template based on post type and context
        """
        template = self.prompt_templates.get(post_type, self.prompt_templates["general"])
        
        # Customize template based on user context
        customized_template = template.copy()
        
        # Adjust tone based on user preferences
        user_tone = user_context.get("preferred_tone", "")
        if user_tone:
            customized_template["tone"] = user_tone
        
        # Adjust length based on user preferences
        user_length = user_context.get("preferred_length", "")
        if user_length:
            customized_template["length"] = user_length
        
        return customized_template
    
    def _build_structured_prompt(self, template: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """
        Build a structured prompt using the selected template
        """
        prompt_parts = []
        
        # Add role definition
        prompt_parts.append("ROLE: You are a professional LinkedIn content creator and thought leader.")
        
        # Add context
        context_section = self._build_context_section(user_context)
        prompt_parts.append(context_section)
        
        # Add content structure requirements
        structure_section = self._build_structure_section(template, user_context)
        prompt_parts.append(structure_section)
        
        # Add tone and style guidelines
        style_section = self._build_style_section(template, user_context)
        prompt_parts.append(style_section)
        
        # Add constraints and requirements
        constraints_section = self._build_constraints_section(user_context)
        prompt_parts.append(constraints_section)
        
        # Add output format specification
        format_section = self._build_format_section()
        prompt_parts.append(format_section)
        
        return "\n\n".join(prompt_parts)
    
    def _build_context_section(self, user_context: Dict[str, Any]) -> str:
        """Build the context section of the prompt"""
        context = f"""CONTEXT:
        - Professional: {user_context.get('current_work', 'Professional in technology')}
        - Industry: {user_context.get('industry', 'Technology')}
        - Experience Level: {user_context.get('experience_level', 'Mid-level professional')}
        - Current Project/Focus: {user_context.get('current_project', 'Various professional initiatives')}
        - Skills to Highlight: {', '.join(user_context.get('skills', ['Leadership', 'Innovation', 'Problem-solving']))}
        - Career Goals: {user_context.get('career_goals', 'Professional growth and thought leadership')}
        - Target Audience: {user_context.get('target_audience', 'Professional network and industry peers')}"""
        
        return context
    
    def _build_structure_section(self, template: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Build the structure requirements section"""
        structure = f"""CONTENT STRUCTURE ({template['name']}):
        
        Required Elements:"""
        
        for i, element in enumerate(template['structure'], 1):
            element_description = self._get_element_description(element, user_context)
            structure += f"\n        {i}. {element_description}"
        
        structure += f"\n\n        Focus: {template['focus'].replace('_', ' ').title()}"
        
        return structure
    
    def _get_element_description(self, element: str, user_context: Dict[str, Any]) -> str:
        """Get description for each structural element"""
        descriptions = {
            "context_setting": "Set the scene with relevant background",
            "project_description": "Clearly describe the project and its objectives",
            "methodology_brief": "Explain the approach or methodology used",
            "results_summary": "Highlight key results and outcomes",
            "learnings": "Share key insights and lessons learned",
            "call_to_action": "Engage the audience with a question or request",
            "problem_statement": "Define the problem or challenge addressed",
            "approach_overview": "Outline the strategic approach taken",
            "implementation_details": "Provide relevant implementation insights",
            "challenges_overcome": "Discuss significant challenges and solutions",
            "quantified_results": "Include specific metrics and measurable outcomes",
            "broader_implications": "Connect to larger industry or business implications",
            "community_value": "Explain value and relevance to the professional community",
            "milestone_announcement": "Announce the achievement with impact",
            "journey_overview": "Provide context of the journey to this milestone",
            "key_accomplishments": "List major accomplishments within this achievement",
            "impact_metrics": "Share quantifiable impact and success metrics",
            "lessons_learned": "Reflect on key insights gained",
            "future_vision": "Share vision for future direction",
            "gratitude_acknowledgment": "Acknowledge support from team, mentors, or community",
            "observation_hook": "Start with an engaging industry observation",
            "context_background": "Provide necessary context for the insight",
            "analysis_framework": "Present analytical framework or methodology",
            "personal_perspective": "Add unique personal viewpoint or experience",
            "supporting_evidence": "Include data, examples, or case studies",
            "actionable_takeaways": "Provide concrete actions readers can take",
            "discussion_starter": "End with thought-provoking questions",
            "announcement": "Make the achievement announcement",
            "journey_context": "Provide context of the path to achievement",
            "support_acknowledgment": "Recognize those who supported the journey",
            "key_milestones": "Highlight significant milestones reached",
            "personal_growth": "Reflect on personal/professional development",
            "inspiration_message": "Share inspiring message for others",
            "forward_looking": "Look ahead to future opportunities",
            "engaging_hook": "Start with attention-grabbing opening",
            "main_content": "Deliver the core message or story",
            "personal_connection": "Add personal experience or connection",
            "value_proposition": "Clearly state value to the reader"
        }
        
        return descriptions.get(element, f"Include {element.replace('_', ' ')}")
    
    def _build_style_section(self, template: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Build the style and tone requirements"""
        tone_descriptions = {
            "enthusiastic_professional": "Enthusiastic yet professional, showing passion while maintaining credibility",
            "authoritative_insightful": "Authoritative and insightful, demonstrating deep expertise",
            "celebratory_reflective": "Celebratory yet reflective, balancing achievement with humility",
            "thoughtful_analytical": "Thoughtful and analytical, presenting well-reasoned perspectives",
            "grateful_inspiring": "Grateful and inspiring, acknowledging support while motivating others",
            "professional_engaging": "Professional yet engaging, accessible to a broad professional audience"
        }
        
        style = f"""TONE & STYLE:
        - Tone: {tone_descriptions.get(template['tone'], template['tone'].replace('_', ' ').title())}
        - Length: {template['length'].title()} format ({self._get_length_guidance(template['length'])})
        - Voice: First person, authentic and genuine
        - Emoji Usage: {user_context.get('emoji_preference', 'Strategic and professional')}
        - Hashtag Strategy: 3-5 relevant, industry-specific hashtags
        - Engagement: Design for comments, shares, and meaningful discussion"""
        
        return style
    
    def _get_length_guidance(self, length: str) -> str:
        """Get length guidance based on preference"""
        guidance = {
            "short": "150-400 characters, concise and impactful",
            "medium": "400-800 characters, balanced detail and readability", 
            "long": "800-1500 characters, comprehensive with depth"
        }
        return guidance.get(length, "400-800 characters")
    
    def _build_constraints_section(self, user_context: Dict[str, Any]) -> str:
        """Build the constraints and requirements section"""
        constraints = f"""REQUIREMENTS & CONSTRAINTS:
        - Maximum Length: {user_context.get('max_length', 1500)} characters
        - Professional Standards: Maintain high professional standards throughout
        - Authenticity: Ensure content feels genuine and personal
        - Value-First: Every post must provide clear value to readers
        - LinkedIn Algorithm: Optimize for LinkedIn's engagement patterns
        - Call-to-Action: Include appropriate engagement mechanism
        - Hashtag Limit: Maximum 5 hashtags, all relevant and strategic
        - Accessibility: Use clear, accessible language
        - Brand Consistency: Align with professional brand and expertise areas"""
        
        # Add specific constraints based on user context
        if user_context.get('avoid_topics'):
            constraints += f"\n        - Avoid Topics: {', '.join(user_context['avoid_topics'])}"
        
        if user_context.get('required_elements'):
            constraints += f"\n        - Required Elements: {', '.join(user_context['required_elements'])}"
        
        return constraints
    
    def _build_format_section(self) -> str:
        """Build the output format specification"""
        return """OUTPUT FORMAT:
        Provide the LinkedIn post as a complete, ready-to-publish piece of content that:
        1. Follows the specified structure and includes all required elements
        2. Maintains the appropriate tone and style throughout
        3. Includes strategic hashtags integrated naturally
        4. Ends with an engaging call-to-action
        5. Is optimized for LinkedIn's format and algorithm
        
        The output should be publication-ready without any additional formatting needed."""
    
    async def _optimize_prompt(self, structured_prompt: str) -> str:
        """
        Optimize the structured prompt for clarity and effectiveness
        """
        optimization_request = f"""Analyze and optimize this prompt for maximum clarity and effectiveness:

        ORIGINAL PROMPT:
        {structured_prompt}

        OPTIMIZATION REQUIREMENTS:
        1. Ensure clarity and specificity in all instructions
        2. Remove any ambiguity or conflicting requirements
        3. Optimize for the target AI model's capabilities
        4. Maintain all essential requirements while improving flow
        5. Add any missing critical elements for high-quality output

        Provide the optimized version that will generate the best possible LinkedIn content."""
        
        try:
            optimized = await self.call_ollama(
                prompt=optimization_request,
                system_prompt="You are an expert prompt engineer. Optimize prompts for maximum clarity and effectiveness."
            )
            
            # If optimization is successful, return it; otherwise return original
            if optimized and len(optimized) > 100:
                return optimized
            else:
                return structured_prompt
                
        except Exception as e:
            logger.warning(f"Prompt optimization failed: {str(e)}, using original")
            return structured_prompt
    
    async def generate_custom_prompt(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a completely custom prompt based on specific requirements
        """
        requirements = input_data.get("custom_requirements", {})
        
        custom_prompt_request = f"""Create a custom LinkedIn content generation prompt with these specific requirements:

        CUSTOM REQUIREMENTS:
        {json.dumps(requirements, indent=2)}

        The prompt should be:
        1. Highly specific to these requirements
        2. Structured for optimal AI response
        3. Include all necessary context and constraints
        4. Optimized for high-quality LinkedIn content generation

        Generate a complete, structured prompt that will produce excellent results."""
        
        try:
            custom_prompt = await self.call_ollama(
                prompt=custom_prompt_request,
                system_prompt=self.get_system_prompt()
            )
            
            return {
                "custom_prompt": custom_prompt,
                "requirements_used": requirements,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating custom prompt: {str(e)}")
            return {"error": str(e)}