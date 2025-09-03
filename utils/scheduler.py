"""
Content Scheduler - Manages content scheduling for optimal visibility
Supports the 3-month posting strategy: Mini projects (15 days), Main projects (Monthly), Capstone (Quarterly)
"""

import asyncio
import schedule
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Callable
import json
from utils.database import DatabaseManager
from agents.agent_coordinator import AgentCoordinator

logger = logging.getLogger(__name__)

class ContentScheduler:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.agent_coordinator = AgentCoordinator()
        self.is_running = False
        self.scheduled_jobs = []
        
        # Optimal posting times for LinkedIn (based on research)
        self.optimal_times = {
            'weekday_morning': time(9, 0),   # 9:00 AM
            'weekday_lunch': time(12, 0),    # 12:00 PM  
            'weekday_evening': time(17, 0),  # 5:00 PM
            'tuesday_peak': time(10, 0),     # Tuesday 10:00 AM (best day)
            'wednesday_peak': time(14, 0),   # Wednesday 2:00 PM
            'thursday_peak': time(11, 0)     # Thursday 11:00 AM
        }
        
        # Frequency mapping
        self.frequency_mapping = {
            'every_15_days': 15,
            'monthly': 30,
            'quarterly': 90,
            'weekly': 7,
            'biweekly': 14,
            'daily': 1
        }
    
    async def initialize(self):
        """Initialize the scheduler"""
        await self.agent_coordinator.initialize()
        logger.info("Content Scheduler initialized")
    
    async def setup_user_schedule(self, user_id: str = 'default') -> Dict[str, Any]:
        """Set up posting schedule based on user preferences"""
        try:
            user_profile = await self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            posting_strategy = user_profile.get('preferences', {}).get('posting_strategy', {})
            
            schedules_created = []
            
            # Create schedules for each post type
            for post_type, config in posting_strategy.items():
                if config.get('enabled', True):
                    frequency = config.get('frequency', 'weekly')
                    
                    # Calculate next post date
                    days_interval = self.frequency_mapping.get(frequency, 7)
                    next_post_date = datetime.now() + timedelta(days=days_interval)
                    
                    # Optimize posting time
                    optimized_time = self._get_optimal_posting_time(post_type)
                    next_post_date = next_post_date.replace(
                        hour=optimized_time.hour,
                        minute=optimized_time.minute,
                        second=0,
                        microsecond=0
                    )
                    
                    schedule_data = {
                        'user_id': user_id,
                        'post_type': post_type,
                        'frequency': frequency,
                        'next_post_date': next_post_date.isoformat(),
                        'is_active': True
                    }
                    
                    success = await self.db_manager.save_posting_schedule(schedule_data)
                    if success:
                        schedules_created.append(schedule_data)
            
            return {
                'schedules_created': len(schedules_created),
                'schedules': schedules_created,
                'message': f"Created {len(schedules_created)} posting schedules"
            }
            
        except Exception as e:
            logger.error(f"Error setting up user schedule: {str(e)}")
            return {"error": str(e)}
    
    def _get_optimal_posting_time(self, post_type: str) -> time:
        """Get optimal posting time based on post type and LinkedIn best practices"""
        time_preferences = {
            'mini_project': 'weekday_morning',    # Morning engagement for quick wins
            'main_project': 'tuesday_peak',       # Tuesday peak for detailed content
            'capstone': 'wednesday_peak',         # Wednesday for major announcements
            'insight': 'weekday_lunch',           # Lunch time for thought leadership
            'achievement': 'thursday_peak',       # Thursday for celebrations
            'general': 'weekday_morning'          # Default to morning
        }
        
        preferred_time = time_preferences.get(post_type, 'weekday_morning')
        return self.optimal_times[preferred_time]
    
    async def get_upcoming_posts(self, user_id: str = 'default', days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming scheduled posts"""
        try:
            schedules = await self.db_manager.get_active_schedules(user_id)
            upcoming_posts = []
            
            cutoff_date = datetime.now() + timedelta(days=days_ahead)
            
            for schedule in schedules:
                next_post = datetime.fromisoformat(schedule['next_post_date'])
                if next_post <= cutoff_date:
                    upcoming_posts.append({
                        'post_type': schedule['post_type'],
                        'scheduled_for': schedule['next_post_date'],
                        'frequency': schedule['frequency'],
                        'days_until': (next_post - datetime.now()).days
                    })
            
            # Sort by scheduled date
            upcoming_posts.sort(key=lambda x: x['scheduled_for'])
            return upcoming_posts
            
        except Exception as e:
            logger.error(f"Error getting upcoming posts: {str(e)}")
            return []
    
    async def schedule_specific_post(self, post_context: Dict[str, Any], scheduled_for: datetime) -> Dict[str, Any]:
        """Schedule a specific post for a specific time"""
        try:
            # Generate the post content
            complete_post = await self.agent_coordinator.generate_complete_post(post_context)
            
            if 'error' in complete_post:
                return complete_post
            
            # Save as scheduled post
            post_data = {
                'post_id': complete_post['post_id'],
                'user_id': post_context.get('user_id', 'default'),
                'content': complete_post['content'],
                'hashtags': complete_post['hashtags'],
                'post_type': post_context.get('post_type', 'general'),
                'image_path': complete_post.get('image_path', ''),
                'engagement_prediction': complete_post.get('engagement_prediction', {}),
                'scheduled_for': scheduled_for.isoformat(),
                'status': 'scheduled'
            }
            
            success = await self.db_manager.save_generated_post(post_data)
            
            if success:
                return {
                    'post_id': post_data['post_id'],
                    'scheduled_for': scheduled_for.isoformat(),
                    'content_preview': post_data['content'][:100] + "...",
                    'message': 'Post scheduled successfully'
                }
            else:
                return {'error': 'Failed to save scheduled post'}
                
        except Exception as e:
            logger.error(f"Error scheduling specific post: {str(e)}")
            return {'error': str(e)}
    
    async def auto_schedule_next_posts(self, user_id: str = 'default') -> Dict[str, Any]:
        """Automatically schedule the next round of posts based on user strategy"""
        try:
            user_profile = await self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            schedules = await self.db_manager.get_active_schedules(user_id)
            scheduled_posts = []
            
            for schedule in schedules:
                post_type = schedule['post_type']
                next_date = datetime.fromisoformat(schedule['next_post_date'])
                
                # Only schedule if the time has come
                if next_date <= datetime.now() + timedelta(hours=24):  # Schedule 24 hours ahead
                    
                    # Create base context from user profile
                    post_context = {
                        'user_id': user_id,
                        'post_type': post_type,
                        'name': user_profile['name'],
                        'industry': user_profile['industry'],
                        'experience_level': user_profile['experience_level'],
                        'current_work': user_profile['current_work'],
                        'skills': user_profile['skills'],
                        'career_goals': user_profile['career_goals']
                    }
                    
                    # Add user preferences
                    post_context.update(user_profile.get('preferences', {}))
                    
                    # Add auto-generated context based on post type
                    post_context.update(self._generate_auto_context(post_type, user_profile))
                    
                    # Schedule the post
                    result = await self.schedule_specific_post(post_context, next_date)
                    
                    if 'error' not in result:
                        scheduled_posts.append(result)
                        
                        # Update the schedule for next occurrence
                        await self._update_schedule_next_date(schedule)
            
            return {
                'scheduled_count': len(scheduled_posts),
                'scheduled_posts': scheduled_posts,
                'message': f"Auto-scheduled {len(scheduled_posts)} posts"
            }
            
        except Exception as e:
            logger.error(f"Error auto-scheduling posts: {str(e)}")
            return {'error': str(e)}
    
    def _generate_auto_context(self, post_type: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automatic context based on post type and user profile"""
        context = {}
        
        skills = user_profile.get('skills', [])
        industry = user_profile.get('industry', 'Technology')
        
        if post_type == 'mini_project':
            context.update({
                'project_details': f"Recent work involving {skills[0] if skills else 'professional development'}",
                'key_learnings': f"Insights from applying {skills[1] if len(skills) > 1 else 'new techniques'} in {industry}",
                'include_image': True,
                'image_type': 'infographic'
            })
        elif post_type == 'main_project':
            context.update({
                'project_details': f"Significant {industry} initiative leveraging {', '.join(skills[:2])}",
                'challenges': f"Overcoming {industry} challenges through innovative approaches",
                'results': "Measurable improvements in efficiency and outcomes",
                'include_image': True,
                'image_type': 'chart'
            })
        elif post_type == 'capstone':
            context.update({
                'achievement': f"Major milestone in {industry} leveraging {', '.join(skills)}",
                'impact': "Significant impact on team and organizational objectives",
                'journey': f"Journey of growth in {skills[0] if skills else 'professional development'}",
                'include_image': True,
                'image_type': 'achievement'
            })
        elif post_type == 'insight':
            context.update({
                'observation': f"Current trends and observations in {industry}",
                'analysis': f"Analysis based on experience with {skills[0] if skills else 'industry practices'}",
                'include_image': True,
                'image_type': 'quote'
            })
        elif post_type == 'achievement':
            context.update({
                'achievement': f"Professional milestone in {skills[0] if skills else industry}",
                'acknowledgments': "Team members and mentors who supported this journey",
                'include_image': True,
                'image_type': 'achievement'
            })
        
        return context
    
    async def _update_schedule_next_date(self, schedule: Dict[str, Any]):
        """Update schedule for the next occurrence"""
        try:
            frequency = schedule['frequency']
            days_interval = self.frequency_mapping.get(frequency, 7)
            
            current_date = datetime.fromisoformat(schedule['next_post_date'])
            next_date = current_date + timedelta(days=days_interval)
            
            # Update in database (simplified - in real implementation, you'd have an update method)
            # For now, we'll create a new schedule entry
            new_schedule_data = {
                'user_id': schedule['user_id'],
                'post_type': schedule['post_type'],
                'frequency': frequency,
                'next_post_date': next_date.isoformat(),
                'is_active': True
            }
            
            await self.db_manager.save_posting_schedule(new_schedule_data)
            
        except Exception as e:
            logger.error(f"Error updating schedule: {str(e)}")
    
    async def get_schedule_analytics(self, user_id: str = 'default') -> Dict[str, Any]:
        """Get analytics on posting schedule performance"""
        try:
            posts = await self.db_manager.get_posts_by_user(user_id, limit=100)
            schedules = await self.db_manager.get_active_schedules(user_id)
            
            # Analyze posting patterns
            post_types = {}
            total_posts = len(posts)
            
            for post in posts:
                post_type = post['post_type']
                post_types[post_type] = post_types.get(post_type, 0) + 1
            
            # Calculate adherence to schedule
            scheduled_posts = [p for p in posts if p['status'] == 'scheduled']
            posted_posts = [p for p in posts if p['status'] == 'posted']
            
            analytics = {
                'total_posts': total_posts,
                'scheduled_posts': len(scheduled_posts),
                'posted_posts': len(posted_posts),
                'active_schedules': len(schedules),
                'post_type_distribution': post_types,
                'schedule_adherence': len(posted_posts) / max(len(scheduled_posts), 1) * 100,
                'next_scheduled_posts': await self.get_upcoming_posts(user_id, 7)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting schedule analytics: {str(e)}")
            return {}
    
    async def manually_trigger_post_generation(self, post_type: str, user_id: str = 'default') -> Dict[str, Any]:
        """Manually trigger post generation for immediate use"""
        try:
            user_profile = await self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            # Create context
            post_context = {
                'user_id': user_id,
                'post_type': post_type,
                'name': user_profile['name'],
                'industry': user_profile['industry'],
                'experience_level': user_profile['experience_level'],
                'current_work': user_profile['current_work'],
                'skills': user_profile['skills'],
                'career_goals': user_profile['career_goals']
            }
            
            # Add user preferences
            post_context.update(user_profile.get('preferences', {}))
            
            # Add auto-generated context
            post_context.update(self._generate_auto_context(post_type, user_profile))
            
            # Generate post
            complete_post = await self.agent_coordinator.generate_complete_post(post_context)
            
            if 'error' not in complete_post:
                # Save as draft
                post_data = {
                    'post_id': complete_post['post_id'],
                    'user_id': user_id,
                    'content': complete_post['content'],
                    'hashtags': complete_post['hashtags'],
                    'post_type': post_type,
                    'image_path': complete_post.get('image_path', ''),
                    'engagement_prediction': complete_post.get('engagement_prediction', {}),
                    'status': 'draft'
                }
                
                await self.db_manager.save_generated_post(post_data)
            
            return complete_post
            
        except Exception as e:
            logger.error(f"Error manually triggering post generation: {str(e)}")
            return {'error': str(e)}
    
    def start_background_scheduler(self):
        """Start the background scheduler (for future automation)"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Schedule daily checks for auto-posting
        schedule.every().day.at("09:00").do(self._run_daily_check)
        
        logger.info("Background scheduler started")
    
    def stop_background_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Background scheduler stopped")
    
    def _run_daily_check(self):
        """Daily check for posts that need to be auto-scheduled"""
        # This would run in the background to auto-schedule posts
        # For now, it's a placeholder for future automation
        logger.info("Running daily schedule check")
        # asyncio.create_task(self.auto_schedule_next_posts())
    
    async def get_schedule_recommendations(self, user_id: str = 'default') -> Dict[str, Any]:
        """Get personalized schedule recommendations"""
        try:
            user_profile = await self.db_manager.get_user_profile(user_id)
            posts = await self.db_manager.get_posts_by_user(user_id, limit=20)
            
            recommendations = {
                'optimal_posting_times': list(self.optimal_times.keys()),
                'suggested_frequency': {},
                'content_mix_recommendations': {},
                'engagement_optimization': []
            }
            
            # Analyze current posting patterns
            if posts:
                post_types = {}
                for post in posts:
                    post_type = post['post_type']
                    post_types[post_type] = post_types.get(post_type, 0) + 1
                
                # Recommend balanced content mix
                total_posts = len(posts)
                recommendations['content_mix_recommendations'] = {
                    'mini_projects': f"{(post_types.get('mini_project', 0) / total_posts * 100):.1f}% (target: 40%)",
                    'main_projects': f"{(post_types.get('main_project', 0) / total_posts * 100):.1f}% (target: 30%)",
                    'insights': f"{(post_types.get('insight', 0) / total_posts * 100):.1f}% (target: 20%)",
                    'achievements': f"{(post_types.get('achievement', 0) / total_posts * 100):.1f}% (target: 10%)"
                }
            
            # General recommendations
            industry = user_profile.get('industry', 'Technology') if user_profile else 'Technology'
            
            if 'Technology' in industry:
                recommendations['suggested_frequency']['mini_project'] = 'every_15_days'
                recommendations['suggested_frequency']['main_project'] = 'monthly'
                recommendations['suggested_frequency']['insight'] = 'weekly'
            
            recommendations['engagement_optimization'] = [
                "Post during weekday mornings (9-11 AM) for maximum visibility",
                "Use Tuesday-Thursday for important announcements",
                "Include images in 70% of posts for better engagement",
                "Maintain consistent posting schedule",
                "Engage with comments within 2 hours of posting"
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting schedule recommendations: {str(e)}")
            return {}