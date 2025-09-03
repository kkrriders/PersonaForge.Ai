"""
User Input Handler - Collects and manages user prerequisites and preferences
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class UserInputHandler:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    async def collect_user_prerequisites(self) -> Dict[str, Any]:
        """Interactive collection of user prerequisites"""
        print("\n🎯 Let's set up your LinkedIn automation profile!")
        print("=" * 50)
        
        user_data = {}
        
        # Basic Information
        print("\n📋 Basic Information:")
        user_data['name'] = input("Your name: ").strip()
        user_data['industry'] = self._get_industry_choice()
        user_data['experience_level'] = self._get_experience_level()
        
        # Current Work/Projects
        print("\n💼 Current Work & Projects:")
        user_data['current_work'] = input("Current role/company: ").strip()
        user_data['current_project'] = input("Main project you're working on: ").strip()
        
        # Skills to Showcase
        print("\n🛠️ Skills to Showcase:")
        print("Enter skills you want to highlight (press Enter twice when done):")
        skills = []
        while True:
            skill = input("- ").strip()
            if not skill:
                break
            skills.append(skill)
        user_data['skills'] = skills or ['Leadership', 'Innovation', 'Problem Solving']
        
        # Career Goals
        print("\n🎯 Career Goals:")
        goals_options = [
            "Thought leadership in my field",
            "Career advancement/promotion", 
            "Building professional network",
            "Showcasing expertise",
            "Finding new opportunities",
            "Building personal brand"
        ]
        
        print("Select your primary career goals (enter numbers separated by commas):")
        for i, goal in enumerate(goals_options, 1):
            print(f"{i}. {goal}")
        
        goal_choices = input("Your choices (e.g., 1,3,4): ").strip()
        selected_goals = []
        try:
            for choice in goal_choices.split(','):
                idx = int(choice.strip()) - 1
                if 0 <= idx < len(goals_options):
                    selected_goals.append(goals_options[idx])
        except:
            selected_goals = ["Building professional network"]
        
        user_data['career_goals'] = ', '.join(selected_goals)
        
        # Content Preferences
        print("\n📝 Content Preferences:")
        user_data['preferred_tone'] = self._get_tone_preference()
        user_data['preferred_length'] = self._get_length_preference()
        user_data['emoji_preference'] = self._get_emoji_preference()
        
        # Posting Strategy
        print("\n📅 Posting Strategy:")
        user_data['posting_strategy'] = self._get_posting_strategy()
        
        # Topics to Avoid
        print("\n🚫 Topics to Avoid (optional):")
        print("Enter topics you'd prefer not to post about (press Enter twice when done):")
        avoid_topics = []
        while True:
            topic = input("- ").strip()
            if not topic:
                break
            avoid_topics.append(topic)
        user_data['avoid_topics'] = avoid_topics
        
        # Set user ID and timestamps
        user_data['user_id'] = 'default'
        user_data['preferences'] = {
            'preferred_tone': user_data['preferred_tone'],
            'preferred_length': user_data['preferred_length'],
            'emoji_preference': user_data['emoji_preference'],
            'posting_strategy': user_data['posting_strategy'],
            'avoid_topics': user_data['avoid_topics']
        }
        
        # Save to database
        success = await self.db_manager.save_user_profile(user_data)
        if success:
            print("\n✅ Profile saved successfully!")
        else:
            print("\n❌ Error saving profile. Please try again.")
        
        return user_data
    
    def _get_industry_choice(self) -> str:
        """Get user's industry selection"""
        industries = [
            "Technology/Software",
            "Finance/Banking",
            "Healthcare",
            "Education",
            "Marketing/Advertising",
            "Consulting",
            "Manufacturing",
            "Retail/E-commerce",
            "Media/Entertainment",
            "Government/Non-profit",
            "Other"
        ]
        
        print("Select your industry:")
        for i, industry in enumerate(industries, 1):
            print(f"{i}. {industry}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-11): ").strip())
                if 1 <= choice <= len(industries):
                    if choice == len(industries):  # "Other"
                        return input("Please specify your industry: ").strip()
                    return industries[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_experience_level(self) -> str:
        """Get user's experience level"""
        levels = [
            "Entry Level (0-2 years)",
            "Mid Level (3-5 years)",
            "Senior Level (6-10 years)",
            "Executive Level (10+ years)",
            "Student/Recent Graduate"
        ]
        
        print("Select your experience level:")
        for i, level in enumerate(levels, 1):
            print(f"{i}. {level}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-5): ").strip())
                if 1 <= choice <= len(levels):
                    return levels[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_tone_preference(self) -> str:
        """Get user's preferred tone"""
        tones = [
            "Professional and formal",
            "Professional but conversational",
            "Enthusiastic and energetic",
            "Thoughtful and analytical",
            "Inspiring and motivational"
        ]
        
        print("Select your preferred posting tone:")
        for i, tone in enumerate(tones, 1):
            print(f"{i}. {tone}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-5): ").strip())
                if 1 <= choice <= len(tones):
                    return tones[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_length_preference(self) -> str:
        """Get user's preferred post length"""
        lengths = [
            "Short (150-400 characters) - Quick insights",
            "Medium (400-800 characters) - Balanced content",
            "Long (800-1500 characters) - Detailed posts"
        ]
        
        print("Select your preferred post length:")
        for i, length in enumerate(lengths, 1):
            print(f"{i}. {length}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-3): ").strip())
                if 1 <= choice <= len(lengths):
                    return ["short", "medium", "long"][choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_emoji_preference(self) -> str:
        """Get user's emoji usage preference"""
        preferences = [
            "No emojis - Professional text only",
            "Minimal emojis - 1-2 strategic emojis",
            "Moderate emojis - 3-5 relevant emojis",
            "Liberal emoji use - Expressive and engaging"
        ]
        
        print("Select your emoji usage preference:")
        for i, pref in enumerate(preferences, 1):
            print(f"{i}. {pref}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-4): ").strip())
                if 1 <= choice <= len(preferences):
                    return ["none", "minimal", "moderate", "liberal"][choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_posting_strategy(self) -> Dict[str, Any]:
        """Get user's preferred posting strategy"""
        print("Configure your 3-month posting strategy:")
        
        strategy = {}
        
        # Mini projects
        print("\n📊 Mini Projects (quick wins, tools, techniques):")
        print("Recommended: Every 15 days")
        frequency = input("How often? (default: every_15_days): ").strip()
        strategy['mini_projects'] = {
            'frequency': frequency or 'every_15_days',
            'enabled': True
        }
        
        # Main projects
        print("\n🚀 Main Projects (significant work, deep dives):")
        print("Recommended: Monthly")
        frequency = input("How often? (default: monthly): ").strip()
        strategy['main_projects'] = {
            'frequency': frequency or 'monthly',
            'enabled': True
        }
        
        # Capstone project
        print("\n🏆 Capstone Project (major achievement):")
        print("Recommended: End of 3 months")
        frequency = input("How often? (default: quarterly): ").strip()
        strategy['capstone_project'] = {
            'frequency': frequency or 'quarterly',
            'enabled': True
        }
        
        # Additional content
        insights_freq = input("\n💡 Industry insights frequency (weekly/biweekly/monthly): ").strip()
        strategy['insights'] = {
            'frequency': insights_freq or 'weekly',
            'enabled': True
        }
        
        return strategy
    
    async def update_user_preferences(self) -> Dict[str, Any]:
        """Update existing user preferences"""
        print("\n⚙️ Update Your Preferences")
        print("=" * 30)
        
        # Get current profile
        current_profile = await self.db_manager.get_user_profile()
        if not current_profile:
            print("No profile found. Let's create one first.")
            return await self.collect_user_prerequisites()
        
        print(f"Current profile for: {current_profile.get('name', 'Unknown')}")
        
        update_options = [
            "Update skills to showcase",
            "Update career goals",
            "Update content preferences",
            "Update posting strategy",
            "Update topics to avoid",
            "Update all preferences"
        ]
        
        print("\nWhat would you like to update?")
        for i, option in enumerate(update_options, 1):
            print(f"{i}. {option}")
        
        choice = input("Enter choice (1-6): ").strip()
        
        updated_data = current_profile.copy()
        
        if choice == "1":
            updated_data['skills'] = self._update_skills(current_profile.get('skills', []))
        elif choice == "2":
            updated_data['career_goals'] = self._update_career_goals()
        elif choice == "3":
            prefs = self._update_content_preferences()
            updated_data['preferences'].update(prefs)
        elif choice == "4":
            updated_data['preferences']['posting_strategy'] = self._get_posting_strategy()
        elif choice == "5":
            updated_data['preferences']['avoid_topics'] = self._update_avoid_topics()
        elif choice == "6":
            return await self.collect_user_prerequisites()
        else:
            print("Invalid choice.")
            return current_profile
        
        # Save updated profile
        success = await self.db_manager.save_user_profile(updated_data)
        if success:
            print("\n✅ Preferences updated successfully!")
        else:
            print("\n❌ Error updating preferences.")
        
        return updated_data
    
    def _update_skills(self, current_skills: List[str]) -> List[str]:
        """Update skills list"""
        print(f"\nCurrent skills: {', '.join(current_skills)}")
        print("Enter new skills (press Enter twice when done):")
        
        new_skills = []
        while True:
            skill = input("- ").strip()
            if not skill:
                break
            new_skills.append(skill)
        
        return new_skills if new_skills else current_skills
    
    def _update_career_goals(self) -> str:
        """Update career goals"""
        return input("Enter your updated career goals: ").strip()
    
    def _update_content_preferences(self) -> Dict[str, Any]:
        """Update content preferences"""
        prefs = {}
        
        update_tone = input("Update tone preference? (y/n): ").lower() == 'y'
        if update_tone:
            prefs['preferred_tone'] = self._get_tone_preference()
        
        update_length = input("Update length preference? (y/n): ").lower() == 'y'
        if update_length:
            prefs['preferred_length'] = self._get_length_preference()
        
        update_emoji = input("Update emoji preference? (y/n): ").lower() == 'y'
        if update_emoji:
            prefs['emoji_preference'] = self._get_emoji_preference()
        
        return prefs
    
    def _update_avoid_topics(self) -> List[str]:
        """Update topics to avoid"""
        print("Enter topics to avoid (press Enter twice when done):")
        avoid_topics = []
        while True:
            topic = input("- ").strip()
            if not topic:
                break
            avoid_topics.append(topic)
        
        return avoid_topics
    
    async def get_post_context(self, post_type: str = "general") -> Dict[str, Any]:
        """Get context for generating a specific post"""
        user_profile = await self.db_manager.get_user_profile()
        if not user_profile:
            print("No user profile found. Please set up your profile first.")
            return {}
        
        print(f"\n📝 Creating {post_type.replace('_', ' ').title()} Post")
        print("=" * 40)
        
        context = {
            'user_id': user_profile['user_id'],
            'post_type': post_type,
            'name': user_profile['name'],
            'industry': user_profile['industry'],
            'experience_level': user_profile['experience_level'],
            'current_work': user_profile['current_work'],
            'skills': user_profile['skills'],
            'career_goals': user_profile['career_goals']
        }
        
        # Add user preferences
        context.update(user_profile.get('preferences', {}))
        
        # Get specific context based on post type
        if post_type == "mini_project":
            context['project_details'] = input("Describe your mini project: ").strip()
            context['key_learnings'] = input("Key learnings/insights: ").strip()
        elif post_type == "main_project":
            context['project_details'] = input("Describe your main project: ").strip()
            context['challenges'] = input("Main challenges overcome: ").strip()
            context['results'] = input("Quantifiable results: ").strip()
        elif post_type == "capstone":
            context['achievement'] = input("Describe your major achievement: ").strip()
            context['impact'] = input("Impact and metrics: ").strip()
            context['journey'] = input("Brief journey description: ").strip()
        elif post_type == "insight":
            context['observation'] = input("Your industry observation: ").strip()
            context['analysis'] = input("Your analysis/perspective: ").strip()
        elif post_type == "achievement":
            context['achievement'] = input("Describe your achievement: ").strip()
            context['acknowledgments'] = input("People to thank/acknowledge: ").strip()
        elif post_type == "general":
            print("✍️ Enter your custom content prompt:")
            print("(Describe what you want to post about, key points, specific topics, etc.)")
            context['custom_prompt'] = input("Your prompt: ").strip()
            if not context['custom_prompt']:
                print("No custom prompt provided, using generic professional post.")
                context['custom_prompt'] = "Create a professional LinkedIn post about current industry trends"
        
        # Ask if they want to include an image
        include_image = input("\nInclude an image with this post? (y/n): ").lower() == 'y'
        context['include_image'] = include_image
        
        if include_image:
            image_types = ["infographic", "chart", "quote", "process", "comparison", "timeline", "achievement"]
            print("Select image type:")
            for i, img_type in enumerate(image_types, 1):
                print(f"{i}. {img_type}")
            
            try:
                choice = int(input("Enter choice (1-7): ").strip())
                if 1 <= choice <= len(image_types):
                    context['image_type'] = image_types[choice - 1]
                else:
                    context['image_type'] = "infographic"
            except:
                context['image_type'] = "infographic"
            
            context['image_style'] = "professional"  # Default style
        
        return context