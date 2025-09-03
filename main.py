#!/usr/bin/env python3
"""
LinkedIn Automation Tool - Local Version
Multi-agent system for automated LinkedIn content generation and posting
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Check requirements first
try:
    from utils.requirements_check import check_requirements
    if not check_requirements():
        print("\n❌ Missing required packages. Please install them before continuing.")
        exit(1)
except ImportError:
    print("⚠️  Requirements checker not available, proceeding anyway...")

from agents.agent_coordinator import AgentCoordinator
from config.settings import settings
from utils.database import DatabaseManager
from utils.user_input import UserInputHandler
from utils.scheduler import ContentScheduler
from utils.privacy import PrivacyManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInAutomationTool:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.agent_coordinator = AgentCoordinator()
        self.user_input_handler = UserInputHandler()
        self.scheduler = ContentScheduler()
        self.privacy_manager = PrivacyManager()
        self.user_profile = None
    
    async def initialize(self):
        """Initialize all components"""
        await self.db_manager.initialize()
        await self.agent_coordinator.initialize()
        await self.scheduler.initialize()
        
        # Load user profile
        self.user_profile = await self.db_manager.get_user_profile()
        
        logger.info("LinkedIn Automation Tool initialized successfully")
    
    async def run_interactive_mode(self):
        """Main interactive loop"""
        print("🚀 Welcome to PersonaForge.AI - LinkedIn Automation Tool")
        print("=" * 60)
        print("🔒 Local-first, privacy-focused LinkedIn content automation")
        
        # Check if user profile exists
        if not self.user_profile:
            print("\n👋 Welcome! Let's set up your profile first.")
            await self.setup_user_profile()
        else:
            print(f"\n👋 Welcome back, {self.user_profile.get('name', 'User')}!")
        
        while True:
            self._display_main_menu()
            
            choice = input("\nSelect an option (1-9): ").strip()
            
            try:
                if choice == "1":
                    await self.generate_post()
                elif choice == "2":
                    await self.manual_content_creation()
                elif choice == "3":
                    await self.schedule_posts()
                elif choice == "4":
                    await self.view_analytics()
                elif choice == "5":
                    await self.manage_user_profile()
                elif choice == "6":
                    await self.view_content_library()
                elif choice == "7":
                    await self.privacy_settings()
                elif choice == "8":
                    await self.system_status()
                elif choice == "9":
                    print("\n👋 Goodbye! Your data remains safely on your local machine.")
                    break
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                logger.error(f"Error in interactive mode: {str(e)}")
    
    def _display_main_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 60)
        print("📋 MAIN MENU")
        print("=" * 60)
        print("1. 📝 Generate LinkedIn Post")
        print("2. ✍️  Manual Content Creation (Posts/Articles/Blogs)")
        print("3. 📅 Schedule Posts")
        print("4. 📊 View Analytics")
        print("5. 👤 Manage User Profile")
        print("6. 📚 View Content Library")
        print("7. 🔒 Privacy Settings")
        print("8. ⚙️  System Status")
        print("9. 🚪 Exit")
    
    async def setup_user_profile(self):
        """Initial user profile setup"""
        try:
            self.user_profile = await self.user_input_handler.collect_user_prerequisites()
            if self.user_profile:
                print("\n✅ Profile setup complete! Setting up your posting schedule...")
                await self.scheduler.setup_user_schedule()
        except Exception as e:
            print(f"❌ Error setting up profile: {str(e)}")
    
    async def generate_post(self):
        """Generate a LinkedIn post"""
        print("\n📝 GENERATE LINKEDIN POST")
        print("=" * 40)
        
        if not self.user_profile:
            print("❌ Please set up your profile first.")
            return
        
        # Select post type
        post_types = [
            ("mini_project", "Mini Project (Quick win, tool, or technique)"),
            ("main_project", "Main Project (Significant work with results)"),
            ("capstone", "Capstone Project (Major achievement)"),
            ("insight", "Industry Insight (Thought leadership)"),
            ("achievement", "Achievement (Milestone celebration)"),
            ("general", "General Professional Post")
        ]
        
        print("Select post type:")
        for i, (post_type, description) in enumerate(post_types, 1):
            print(f"{i}. {description}")
        
        try:
            choice = int(input("\nEnter choice (1-6): ").strip())
            if 1 <= choice <= len(post_types):
                post_type = post_types[choice - 1][0]
                
                # Get specific context for this post
                post_context = await self.user_input_handler.get_post_context(post_type)
                
                if post_context:
                    print("\n🔄 Generating your LinkedIn post...")
                    
                    # Generate the complete post
                    result = await self.agent_coordinator.generate_complete_post(post_context)
                    
                    if 'error' not in result:
                        self._display_generated_post(result)
                        
                        # Ask if user wants to schedule or save as draft
                        action = input("\nWhat would you like to do?\n1. Save as draft\n2. Schedule for later\n3. Copy to clipboard\nChoice: ").strip()
                        
                        if action == "2":
                            await self._schedule_generated_post(result, post_context)
                        elif action == "3":
                            await self._copy_to_clipboard(result)
                        else:
                            print("✅ Post saved as draft in your content library.")
                    else:
                        print(f"❌ Error generating post: {result.get('error', 'Unknown error')}")
                else:
                    print("❌ Failed to collect post context.")
            else:
                print("❌ Invalid choice.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error generating post: {str(e)}")
    
    def _display_generated_post(self, post_result: Dict[str, Any]):
        """Display the generated post"""
        print("\n" + "=" * 60)
        print("📝 GENERATED LINKEDIN POST")
        print("=" * 60)
        print(post_result.get('content', ''))
        
        hashtags = post_result.get('hashtags', [])
        if hashtags:
            print(f"\n🏷️ Hashtags: {' '.join(hashtags)}")
        
        if post_result.get('image_path'):
            print(f"\n🖼️ Image: {post_result['image_path']}")
        
        engagement = post_result.get('engagement_prediction', {})
        if engagement:
            print(f"\n📊 Predicted Engagement:")
            print(f"   Likes: {engagement.get('predicted_likes', 0)}")
            print(f"   Comments: {engagement.get('predicted_comments', 0)}")
            print(f"   Shares: {engagement.get('predicted_shares', 0)}")
            print(f"   Score: {engagement.get('engagement_score', 0)}/100")
        
        print("=" * 60)
    
    async def _schedule_generated_post(self, post_result: Dict[str, Any], post_context: Dict[str, Any]):
        """Schedule a generated post"""
        print("\n📅 Schedule this post:")
        print("1. Next optimal time")
        print("2. Custom date/time")
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            # Get next optimal time
            post_type = post_context.get('post_type', 'general')
            optimal_time = self.scheduler._get_optimal_posting_time(post_type)
            scheduled_for = datetime.now().replace(hour=optimal_time.hour, minute=optimal_time.minute, second=0, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if scheduled_for <= datetime.now():
                scheduled_for += timedelta(days=1)
                
        elif choice == "2":
            try:
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                time_str = input("Enter time (HH:MM): ").strip()
                
                scheduled_for = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                
                if scheduled_for <= datetime.now():
                    print("❌ Cannot schedule for past time.")
                    return
            except ValueError:
                print("❌ Invalid date/time format.")
                return
        else:
            print("❌ Invalid choice.")
            return
        
        result = await self.scheduler.schedule_specific_post(post_context, scheduled_for)
        
        if 'error' not in result:
            print(f"✅ Post scheduled for {scheduled_for.strftime('%Y-%m-%d at %H:%M')}")
        else:
            print(f"❌ Error scheduling post: {result.get('error')}")
    
    async def _copy_to_clipboard(self, post_result: Dict[str, Any]):
        """Copy post content to clipboard"""
        try:
            import pyperclip
            content = post_result.get('content', '')
            hashtags = ' '.join(post_result.get('hashtags', []))
            full_content = f"{content}\n\n{hashtags}" if hashtags else content
            
            pyperclip.copy(full_content)
            print("✅ Post copied to clipboard!")
        except ImportError:
            print("📋 Copy to clipboard functionality requires 'pyperclip' package.")
            print("Install with: pip install pyperclip")
        except Exception as e:
            print(f"❌ Error copying to clipboard: {str(e)}")
    
    async def schedule_posts(self):
        """Manage post scheduling"""
        print("\n📅 POST SCHEDULING")
        print("=" * 40)
        
        print("1. View upcoming posts")
        print("2. Auto-schedule next posts")
        print("3. View schedule analytics")
        print("4. Get schedule recommendations")
        print("5. Manual post generation")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        try:
            if choice == "1":
                upcoming = await self.scheduler.get_upcoming_posts()
                if upcoming:
                    print("\n📅 UPCOMING POSTS:")
                    for post in upcoming:
                        days_until = post['days_until']
                        print(f"• {post['post_type'].replace('_', ' ').title()}")
                        print(f"  Scheduled: {post['scheduled_for']}")
                        print(f"  In {days_until} days")
                        print()
                else:
                    print("📅 No upcoming posts scheduled.")
            
            elif choice == "2":
                print("\n🔄 Auto-scheduling next posts...")
                result = await self.scheduler.auto_schedule_next_posts()
                if 'error' not in result:
                    print(f"✅ Scheduled {result['scheduled_count']} posts")
                else:
                    print(f"❌ Error: {result['error']}")
            
            elif choice == "3":
                analytics = await self.scheduler.get_schedule_analytics()
                if analytics:
                    print("\n📊 SCHEDULE ANALYTICS:")
                    print(f"Total Posts: {analytics.get('total_posts', 0)}")
                    print(f"Scheduled Posts: {analytics.get('scheduled_posts', 0)}")
                    print(f"Posted Posts: {analytics.get('posted_posts', 0)}")
                    print(f"Active Schedules: {analytics.get('active_schedules', 0)}")
                    print(f"Schedule Adherence: {analytics.get('schedule_adherence', 0):.1f}%")
            
            elif choice == "4":
                recommendations = await self.scheduler.get_schedule_recommendations()
                if recommendations:
                    print("\n💡 SCHEDULE RECOMMENDATIONS:")
                    for rec in recommendations.get('engagement_optimization', []):
                        print(f"• {rec}")
            
            elif choice == "5":
                post_type = input("Enter post type (mini_project/main_project/capstone/insight/achievement): ").strip()
                if post_type:
                    result = await self.scheduler.manually_trigger_post_generation(post_type)
                    if 'error' not in result:
                        self._display_generated_post(result)
                    else:
                        print(f"❌ Error: {result['error']}")
            
        except Exception as e:
            print(f"❌ Error in scheduling: {str(e)}")
    
    async def view_analytics(self):
        """View analytics dashboard"""
        print("\n📊 ANALYTICS DASHBOARD")
        print("=" * 40)
        
        try:
            # Get analytics summary
            summary = await self.db_manager.get_analytics_summary()
            
            if summary and summary.get('total_posts', 0) > 0:
                print(f"📈 PERFORMANCE SUMMARY (Last {summary['period_days']} days):")
                print(f"Total Posts: {summary['total_posts']}")
                print(f"Average Likes: {summary['avg_likes']}")
                print(f"Average Comments: {summary['avg_comments']}")
                print(f"Average Shares: {summary['avg_shares']}")
                print(f"Average Engagement Rate: {summary['avg_engagement_rate']}%")
            else:
                print("📊 No analytics data available yet.")
                print("💡 Generate and publish some posts to see analytics here.")
            
            # Get recent posts
            posts = await self.db_manager.get_posts_by_user(limit=5)
            if posts:
                print(f"\n📝 RECENT POSTS:")
                for post in posts:
                    status_emoji = {"draft": "📝", "scheduled": "📅", "posted": "✅"}.get(post['status'], "❓")
                    print(f"{status_emoji} {post['post_type'].replace('_', ' ').title()}")
                    print(f"   Created: {post['created_at'][:10]}")
                    print(f"   Status: {post['status'].title()}")
                    if post['content']:
                        preview = post['content'][:50] + "..." if len(post['content']) > 50 else post['content']
                        print(f"   Preview: {preview}")
                    print()
            
            # Get top themes
            themes = await self.db_manager.get_top_themes(limit=3)
            if themes:
                print("🏷️ TOP PERFORMING THEMES:")
                for theme in themes:
                    print(f"• {theme['theme_name']} (Score: {theme['performance_score']:.1f}, Posts: {theme['post_count']})")
        
        except Exception as e:
            print(f"❌ Error loading analytics: {str(e)}")
    
    async def manage_user_profile(self):
        """Manage user profile"""
        print("\n👤 USER PROFILE MANAGEMENT")
        print("=" * 40)
        
        if self.user_profile:
            print(f"Name: {self.user_profile.get('name', 'Not set')}")
            print(f"Industry: {self.user_profile.get('industry', 'Not set')}")
            print(f"Experience: {self.user_profile.get('experience_level', 'Not set')}")
            print(f"Skills: {', '.join(self.user_profile.get('skills', []))}")
        
        print("\n1. Update preferences")
        print("2. View full profile")
        print("3. Reset profile")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        try:
            if choice == "1":
                updated_profile = await self.user_input_handler.update_user_preferences()
                if updated_profile:
                    self.user_profile = updated_profile
                    print("✅ Preferences updated successfully!")
            
            elif choice == "2":
                if self.user_profile:
                    print("\n👤 FULL PROFILE:")
                    for key, value in self.user_profile.items():
                        if key not in ['user_id', 'created_at', 'updated_at']:
                            print(f"{key.replace('_', ' ').title()}: {value}")
                else:
                    print("❌ No profile found.")
            
            elif choice == "3":
                confirm = input("Are you sure you want to reset your profile? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    await self.setup_user_profile()
        
        except Exception as e:
            print(f"❌ Error managing profile: {str(e)}")
    
    async def view_content_library(self):
        """View content library"""
        print("\n📚 CONTENT LIBRARY")
        print("=" * 40)
        
        try:
            posts = await self.db_manager.get_posts_by_user(limit=20)
            
            if posts:
                # Group by status
                drafts = [p for p in posts if p['status'] == 'draft']
                scheduled = [p for p in posts if p['status'] == 'scheduled']
                posted = [p for p in posts if p['status'] == 'posted']
                
                print(f"📝 Drafts: {len(drafts)}")
                print(f"📅 Scheduled: {len(scheduled)}")
                print(f"✅ Posted: {len(posted)}")
                
                if input("\nView detailed list? (y/n): ").strip().lower() == 'y':
                    for post in posts[:10]:  # Show first 10
                        status_emoji = {"draft": "📝", "scheduled": "📅", "posted": "✅"}.get(post['status'], "❓")
                        print(f"\n{status_emoji} {post['post_type'].replace('_', ' ').title()}")
                        print(f"Created: {post['created_at'][:16]}")
                        if post['content']:
                            preview = post['content'][:100] + "..." if len(post['content']) > 100 else post['content']
                            print(f"Content: {preview}")
            else:
                print("📚 No content in library yet.")
                print("💡 Generate some posts to build your content library!")
        
        except Exception as e:
            print(f"❌ Error loading content library: {str(e)}")
    
    async def privacy_settings(self):
        """Manage privacy settings"""
        print("\n🔒 PRIVACY & SECURITY SETTINGS")
        print("=" * 40)
        
        try:
            privacy_info = self.privacy_manager.get_privacy_settings()
            
            print("🔒 CURRENT SETTINGS:")
            print(f"Local Storage Only: {'✅' if privacy_info['local_storage_only'] else '❌'}")
            print(f"Encryption Enabled: {'✅' if privacy_info['encryption_enabled'] else '❌'}")
            print(f"Data Location: {privacy_info['data_location']}")
            
            print(f"\n🛡️ PRIVACY FEATURES:")
            for feature in privacy_info['privacy_features']:
                print(f"• {feature}")
            
            if privacy_info['recommendations']:
                print(f"\n💡 RECOMMENDATIONS:")
                for rec in privacy_info['recommendations']:
                    print(f"• {rec}")
            
            # Validate storage
            validation = self.privacy_manager.validate_local_storage()
            print(f"\n📊 STORAGE VALIDATION:")
            print(f"Files: {validation['file_count']}")
            print(f"Total Size: {validation['total_size_mb']} MB")
            
            # Cleanup option
            if input("\nClean up temporary files? (y/n): ").strip().lower() == 'y':
                cleaned = self.privacy_manager.cleanup_temporary_files()
                print(f"✅ Cleaned {cleaned} temporary files.")
        
        except Exception as e:
            print(f"❌ Error accessing privacy settings: {str(e)}")
    
    async def system_status(self):
        """Display system status"""
        print("\n⚙️ SYSTEM STATUS")
        print("=" * 40)
        
        try:
            # Check components
            print("🔧 COMPONENT STATUS:")
            print(f"Database: {'✅ Connected' if self.db_manager else '❌ Error'}")
            print(f"Agent Coordinator: {'✅ Ready' if self.agent_coordinator else '❌ Error'}")
            print(f"Scheduler: {'✅ Ready' if self.scheduler else '❌ Error'}")
            print(f"Privacy Manager: {'✅ Ready' if self.privacy_manager else '❌ Error'}")
            
            # Check Ollama connection
            try:
                test_agent = self.agent_coordinator.content_agent
                test_response = await test_agent.call_ollama("test", "respond with 'ok'")
                ollama_status = "✅ Connected" if test_response else "❌ Not responding"
            except:
                ollama_status = "❌ Connection failed"
            
            print(f"Ollama API: {ollama_status}")
            
            # Settings info
            print(f"\n⚙️ CONFIGURATION:")
            print(f"Ollama Host: {settings.ollama_host}")
            print(f"Ollama Model: {settings.ollama_model}")
            print(f"Database Path: {settings.database_path}")
            print(f"Local Storage Only: {settings.local_storage_only}")
            print(f"Encryption: {settings.encrypt_data}")
            
            # File system status
            data_exists = os.path.exists("data")
            print(f"\nData Directory: {'✅ Exists' if data_exists else '❌ Missing'}")
            
            if data_exists:
                dirs = ["images", "posts", "schedules", "analytics"]
                for dir_name in dirs:
                    dir_path = f"data/{dir_name}"
                    status = "✅ Exists" if os.path.exists(dir_path) else "📁 Will be created"
                    print(f"  {dir_name}/: {status}")
        
        except Exception as e:
            print(f"❌ Error checking system status: {str(e)}")
    
    async def manual_content_creation(self):
        """Manual content creation with custom prompts"""
        print("\n✍️ MANUAL CONTENT CREATION")
        print("=" * 50)
        
        # Content type selection
        content_types = [
            ("linkedin_post", "LinkedIn Post", "Professional social media post"),
            ("article", "Article", "Medium to long-form article (800-2000 words)"),
            ("blog_post", "Blog Post", "Detailed blog post (1000-3000 words)"),
            ("newsletter", "Newsletter", "Email newsletter content"),
            ("thread", "Social Media Thread", "Multi-post thread/series")
        ]
        
        print("📝 Select content type:")
        for i, (content_type, name, description) in enumerate(content_types, 1):
            print(f"{i}. {name} - {description}")
        
        try:
            choice = int(input("\nEnter choice (1-5): ").strip())
            if 1 <= choice <= len(content_types):
                content_type, content_name, content_desc = content_types[choice - 1]
                
                print(f"\n📋 Creating {content_name}")
                print("=" * 30)
                
                # Check eligibility
                eligibility = self._check_content_eligibility(content_type)
                if not eligibility["eligible"]:
                    print(f"❌ {eligibility['reason']}")
                    return
                
                # Get manual prompt
                print("✍️ Enter your custom prompt:")
                print("(Describe what you want to create, include key points, tone, etc.)")
                print("Type 'END' on a new line when finished:\n")
                
                prompt_lines = []
                while True:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    prompt_lines.append(line)
                
                custom_prompt = '\n'.join(prompt_lines).strip()
                
                if not custom_prompt:
                    print("❌ No prompt provided.")
                    return
                
                # Additional parameters
                target_length = self._get_target_length(content_type)
                tone = self._get_content_tone()
                
                # Generate content
                content_context = {
                    "content_type": content_type,
                    "custom_prompt": custom_prompt,
                    "target_length": target_length,
                    "tone": tone,
                    "user_profile": self.user_profile
                }
                
                print(f"\n🔄 Generating {content_name}...")
                result = await self._generate_manual_content(content_context)
                
                if 'error' not in result:
                    self._display_manual_content(result, content_type)
                    
                    # Post-generation options
                    await self._handle_manual_content_actions(result, content_context)
                else:
                    print(f"❌ Error generating content: {result.get('error', 'Unknown error')}")
            else:
                print("❌ Invalid choice.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error in manual content creation: {str(e)}")
    
    def _check_content_eligibility(self, content_type: str) -> Dict[str, Any]:
        """Check if user is eligible to create this content type"""
        if not self.user_profile:
            return {"eligible": False, "reason": "Please set up your profile first."}
        
        # Basic eligibility checks
        eligibility_rules = {
            "linkedin_post": {"min_experience": 0, "required_fields": []},
            "article": {"min_experience": 1, "required_fields": ["industry", "skills"]},
            "blog_post": {"min_experience": 2, "required_fields": ["industry", "skills", "specialization"]},
            "newsletter": {"min_experience": 3, "required_fields": ["industry", "skills", "specialization"]},
            "thread": {"min_experience": 1, "required_fields": ["industry"]}
        }
        
        rules = eligibility_rules.get(content_type, {"min_experience": 0, "required_fields": []})
        
        # Check experience level
        experience_years = self.user_profile.get("experience_years", 0)
        if experience_years < rules["min_experience"]:
            return {
                "eligible": False, 
                "reason": f"Minimum {rules['min_experience']} years experience required for {content_type.replace('_', ' ')}."
            }
        
        # Check required profile fields
        missing_fields = []
        for field in rules["required_fields"]:
            if not self.user_profile.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "eligible": False,
                "reason": f"Please complete your profile. Missing: {', '.join(missing_fields)}"
            }
        
        return {"eligible": True, "reason": ""}
    
    def _get_target_length(self, content_type: str) -> str:
        """Get target length for content type"""
        length_options = {
            "linkedin_post": ["Short (1-2 paragraphs)", "Medium (3-4 paragraphs)", "Long (5+ paragraphs)"],
            "article": ["Medium (800-1200 words)", "Long (1200-2000 words)", "Extended (2000+ words)"],
            "blog_post": ["Standard (1000-1500 words)", "Long (1500-2500 words)", "Extended (2500+ words)"],
            "newsletter": ["Brief (300-500 words)", "Standard (500-800 words)", "Detailed (800+ words)"],
            "thread": ["Short (3-5 posts)", "Medium (5-8 posts)", "Long (8+ posts)"]
        }
        
        options = length_options.get(content_type, ["Short", "Medium", "Long"])
        
        print(f"\n📏 Select target length:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = int(input("Choice: ").strip())
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except ValueError:
            pass
        
        return options[1]  # Default to medium
    
    def _get_content_tone(self) -> str:
        """Get desired tone for the content"""
        tones = [
            "Professional", "Conversational", "Educational", "Inspirational", 
            "Thought-provoking", "Casual", "Authoritative", "Storytelling"
        ]
        
        print(f"\n🎭 Select tone:")
        for i, tone in enumerate(tones, 1):
            print(f"{i}. {tone}")
        
        try:
            choice = int(input("Choice: ").strip())
            if 1 <= choice <= len(tones):
                return tones[choice - 1]
        except ValueError:
            pass
        
        return "Professional"  # Default
    
    async def _generate_manual_content(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content based on manual prompt"""
        try:
            # Create enhanced prompt for the agent
            enhanced_context = {
                "post_type": "manual_" + content_context["content_type"],
                "custom_requirements": content_context["custom_prompt"],
                "target_length": content_context["target_length"],
                "tone": content_context["tone"],
                "user_profile": content_context["user_profile"],
                "manual_creation": True
            }
            
            # Use the existing agent coordinator
            result = await self.agent_coordinator.generate_complete_post(enhanced_context)
            return result
            
        except Exception as e:
            return {"error": f"Failed to generate manual content: {str(e)}"}
    
    def _display_manual_content(self, content_result: Dict[str, Any], content_type: str):
        """Display the generated manual content"""
        print("\n" + "=" * 80)
        print(f"✍️ GENERATED {content_type.replace('_', ' ').upper()}")
        print("=" * 80)
        
        content = content_result.get('content', '')
        print(content)
        
        # Show additional elements if present
        if content_result.get('hashtags'):
            print(f"\n🏷️ Suggested Hashtags: {' '.join(content_result['hashtags'])}")
        
        if content_result.get('image_path'):
            print(f"\n🖼️ Generated Image: {content_result['image_path']}")
        
        if content_result.get('word_count'):
            print(f"\n📊 Word Count: {content_result['word_count']}")
        
        print("=" * 80)
    
    async def _handle_manual_content_actions(self, content_result: Dict[str, Any], content_context: Dict[str, Any]):
        """Handle post-generation actions for manual content"""
        print("\n🎯 What would you like to do with this content?")
        print("1. Save as draft")
        print("2. Copy to clipboard") 
        print("3. Export to file")
        print("4. Schedule for posting (LinkedIn posts only)")
        print("5. Regenerate with modifications")
        print("6. Return to main menu")
        
        choice = input("\nChoice: ").strip()
        
        try:
            if choice == "1":
                # Save as draft
                await self._save_manual_content_draft(content_result, content_context)
                print("✅ Content saved as draft.")
                
            elif choice == "2":
                # Copy to clipboard
                await self._copy_to_clipboard(content_result)
                
            elif choice == "3":
                # Export to file
                await self._export_manual_content(content_result, content_context)
                
            elif choice == "4" and content_context["content_type"] == "linkedin_post":
                # Schedule posting
                await self._schedule_generated_post(content_result, content_context)
                
            elif choice == "5":
                # Regenerate
                print("\n🔄 Enter additional requirements or modifications:")
                modifications = input().strip()
                if modifications:
                    content_context["custom_prompt"] += f"\n\nAdditional requirements: {modifications}"
                    result = await self._generate_manual_content(content_context)
                    if 'error' not in result:
                        self._display_manual_content(result, content_context["content_type"])
                        await self._handle_manual_content_actions(result, content_context)
                
            elif choice == "6":
                return
                
        except Exception as e:
            print(f"❌ Error handling content action: {str(e)}")
    
    async def _save_manual_content_draft(self, content_result: Dict[str, Any], content_context: Dict[str, Any]):
        """Save manual content as draft"""
        try:
            draft_data = {
                "content": content_result.get('content', ''),
                "content_type": content_context["content_type"],
                "hashtags": content_result.get('hashtags', []),
                "status": "draft",
                "manual_creation": True,
                "original_prompt": content_context["custom_prompt"]
            }
            
            # Save to database using existing database manager
            await self.db_manager.save_post(
                user_id="default",
                post_type=f"manual_{content_context['content_type']}",
                content=draft_data["content"],
                hashtags=draft_data["hashtags"],
                status="draft"
            )
            
        except Exception as e:
            print(f"❌ Error saving draft: {str(e)}")
    
    async def _export_manual_content(self, content_result: Dict[str, Any], content_context: Dict[str, Any]):
        """Export manual content to file"""
        try:
            import os
            from datetime import datetime
            
            # Create exports directory if it doesn't exist
            os.makedirs("data/exports", exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_type = content_context["content_type"]
            filename = f"data/exports/{content_type}_{timestamp}.txt"
            
            # Prepare content for export
            export_content = f"Content Type: {content_type.replace('_', ' ').title()}\n"
            export_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_content += f"Original Prompt: {content_context['custom_prompt']}\n"
            export_content += "=" * 60 + "\n\n"
            export_content += content_result.get('content', '')
            
            if content_result.get('hashtags'):
                export_content += f"\n\nHashtags: {' '.join(content_result['hashtags'])}"
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            print(f"✅ Content exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting content: {str(e)}")

async def main():
    """Main entry point"""
    try:
        tool = LinkedInAutomationTool()
        await tool.initialize()
        await tool.run_interactive_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        logger.error(f"Critical error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())