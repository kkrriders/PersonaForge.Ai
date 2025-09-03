"""
Database Manager for LinkedIn Automation Tool
Handles all database operations using SQLite
"""

try:
    import aiosqlite
except ImportError:
    print("❌ aiosqlite not installed. Run: pip install aiosqlite")
    aiosqlite = None

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_path = settings.database_path
        if not aiosqlite:
            raise ImportError("aiosqlite is required but not installed")
        
    async def initialize(self):
        """Initialize database and create tables"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await db.commit()
        logger.info("Database initialized successfully")
    
    async def _create_tables(self, db):
        """Create all necessary tables"""
        
        # User profiles table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                industry TEXT,
                experience_level TEXT,
                current_work TEXT,
                skills TEXT, -- JSON array
                career_goals TEXT,
                preferences TEXT, -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Generated posts table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS generated_posts (
                post_id TEXT PRIMARY KEY,
                user_id TEXT,
                content TEXT,
                hashtags TEXT, -- JSON array
                post_type TEXT,
                image_path TEXT,
                engagement_prediction TEXT, -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_for TIMESTAMP,
                posted_at TIMESTAMP,
                status TEXT DEFAULT 'draft' -- draft, scheduled, posted
            )
        ''')
        
        # Post analytics table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS post_analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES generated_posts (post_id)
            )
        ''')
        
        # Posting schedule table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS posting_schedule (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                post_type TEXT,
                frequency TEXT, -- daily, weekly, monthly, etc.
                next_post_date TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Content themes and topics tracking
        await db.execute('''
            CREATE TABLE IF NOT EXISTS content_themes (
                theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                theme_name TEXT,
                keywords TEXT, -- JSON array
                performance_score REAL DEFAULT 0.0,
                post_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # User Profile Operations
    async def save_user_profile(self, user_data: Dict[str, Any]) -> bool:
        """Save or update user profile"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, industry, experience_level, current_work, skills, career_goals, preferences, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data.get('user_id', 'default'),
                    user_data.get('name', ''),
                    user_data.get('industry', ''),
                    user_data.get('experience_level', ''),
                    user_data.get('current_work', ''),
                    json.dumps(user_data.get('skills', [])),
                    user_data.get('career_goals', ''),
                    json.dumps(user_data.get('preferences', {})),
                    datetime.now().isoformat()
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving user profile: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str = 'default') -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT * FROM user_profiles WHERE user_id = ?', (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return {
                            'user_id': row[0],
                            'name': row[1],
                            'industry': row[2],
                            'experience_level': row[3],
                            'current_work': row[4],
                            'skills': json.loads(row[5]) if row[5] else [],
                            'career_goals': row[6],
                            'preferences': json.loads(row[7]) if row[7] else {},
                            'created_at': row[8],
                            'updated_at': row[9]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    # Post Operations
    async def save_generated_post(self, post_data: Dict[str, Any]) -> bool:
        """Save generated post to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO generated_posts 
                    (post_id, user_id, content, hashtags, post_type, image_path, engagement_prediction, scheduled_for, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data.get('post_id'),
                    post_data.get('user_id', 'default'),
                    post_data.get('content', ''),
                    json.dumps(post_data.get('hashtags', [])),
                    post_data.get('post_type', 'general'),
                    post_data.get('image_path', ''),
                    json.dumps(post_data.get('engagement_prediction', {})),
                    post_data.get('scheduled_for'),
                    post_data.get('status', 'draft')
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving generated post: {str(e)}")
            return False
    
    async def get_posts_by_user(self, user_id: str = 'default', limit: int = 50) -> List[Dict[str, Any]]:
        """Get posts by user ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT * FROM generated_posts 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    posts = []
                    for row in rows:
                        posts.append({
                            'post_id': row[0],
                            'user_id': row[1],
                            'content': row[2],
                            'hashtags': json.loads(row[3]) if row[3] else [],
                            'post_type': row[4],
                            'image_path': row[5],
                            'engagement_prediction': json.loads(row[6]) if row[6] else {},
                            'created_at': row[7],
                            'scheduled_for': row[8],
                            'posted_at': row[9],
                            'status': row[10]
                        })
                    return posts
        except Exception as e:
            logger.error(f"Error getting posts by user: {str(e)}")
            return []
    
    # Analytics Operations
    async def save_post_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Save post analytics data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO post_analytics 
                    (post_id, likes, comments, shares, views, engagement_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    analytics_data.get('post_id'),
                    analytics_data.get('likes', 0),
                    analytics_data.get('comments', 0),
                    analytics_data.get('shares', 0),
                    analytics_data.get('views', 0),
                    analytics_data.get('engagement_rate', 0.0)
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving post analytics: {str(e)}")
            return False
    
    async def get_analytics_summary(self, user_id: str = 'default', days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get post performance
                async with db.execute('''
                    SELECT AVG(a.likes), AVG(a.comments), AVG(a.shares), AVG(a.engagement_rate), COUNT(*)
                    FROM post_analytics a
                    JOIN generated_posts p ON a.post_id = p.post_id
                    WHERE p.user_id = ? AND a.recorded_at >= datetime('now', '-' || ? || ' days')
                ''', (user_id, days)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row and row[4] > 0:  # If we have data
                        return {
                            'avg_likes': round(row[0] or 0, 2),
                            'avg_comments': round(row[1] or 0, 2),
                            'avg_shares': round(row[2] or 0, 2),
                            'avg_engagement_rate': round(row[3] or 0, 2),
                            'total_posts': row[4],
                            'period_days': days
                        }
                    else:
                        return {
                            'avg_likes': 0,
                            'avg_comments': 0,
                            'avg_shares': 0,
                            'avg_engagement_rate': 0,
                            'total_posts': 0,
                            'period_days': days
                        }
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {}
    
    # Scheduling Operations
    async def save_posting_schedule(self, schedule_data: Dict[str, Any]) -> bool:
        """Save posting schedule"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO posting_schedule 
                    (user_id, post_type, frequency, next_post_date, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    schedule_data.get('user_id', 'default'),
                    schedule_data.get('post_type', 'general'),
                    schedule_data.get('frequency', 'weekly'),
                    schedule_data.get('next_post_date'),
                    schedule_data.get('is_active', True)
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving posting schedule: {str(e)}")
            return False
    
    async def get_active_schedules(self, user_id: str = 'default') -> List[Dict[str, Any]]:
        """Get active posting schedules"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT * FROM posting_schedule 
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY next_post_date
                ''', (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    schedules = []
                    for row in rows:
                        schedules.append({
                            'schedule_id': row[0],
                            'user_id': row[1],
                            'post_type': row[2],
                            'frequency': row[3],
                            'next_post_date': row[4],
                            'is_active': row[5],
                            'created_at': row[6]
                        })
                    return schedules
        except Exception as e:
            logger.error(f"Error getting active schedules: {str(e)}")
            return []
    
    # Content Theme Operations
    async def track_content_theme(self, user_id: str, theme_name: str, keywords: List[str], performance_score: float = 0.0):
        """Track content theme performance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if theme exists
                async with db.execute(
                    'SELECT theme_id, post_count FROM content_themes WHERE user_id = ? AND theme_name = ?',
                    (user_id, theme_name)
                ) as cursor:
                    existing = await cursor.fetchone()
                
                if existing:
                    # Update existing theme
                    await db.execute('''
                        UPDATE content_themes 
                        SET keywords = ?, performance_score = ?, post_count = post_count + 1
                        WHERE theme_id = ?
                    ''', (json.dumps(keywords), performance_score, existing[0]))
                else:
                    # Create new theme
                    await db.execute('''
                        INSERT INTO content_themes (user_id, theme_name, keywords, performance_score, post_count)
                        VALUES (?, ?, ?, ?, 1)
                    ''', (user_id, theme_name, json.dumps(keywords), performance_score))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error tracking content theme: {str(e)}")
            return False
    
    async def get_top_themes(self, user_id: str = 'default', limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content themes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT theme_name, keywords, performance_score, post_count
                    FROM content_themes 
                    WHERE user_id = ?
                    ORDER BY performance_score DESC, post_count DESC
                    LIMIT ?
                ''', (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    themes = []
                    for row in rows:
                        themes.append({
                            'theme_name': row[0],
                            'keywords': json.loads(row[1]) if row[1] else [],
                            'performance_score': row[2],
                            'post_count': row[3]
                        })
                    return themes
        except Exception as e:
            logger.error(f"Error getting top themes: {str(e)}")
            return []