"""
Image Agent - Creates relevant images for LinkedIn posts (infographics, illustrations)
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Pillow not installed. Run: pip install pillow")
    Image = ImageDraw = ImageFont = None

try:
    import numpy as np
except ImportError:
    print("❌ NumPy not installed. Run: pip install numpy")
    np = None

try:
    import seaborn as sns
except ImportError:
    print("❌ Seaborn not installed. Run: pip install seaborn")
    sns = None

try:
    from diffusers import StableDiffusionPipeline, FluxPipeline
    import torch
    DIFFUSERS_AVAILABLE = True
except ImportError:
    print("❌ Diffusers not installed. Run: pip install diffusers torch")
    StableDiffusionPipeline = FluxPipeline = None
    torch = None
    DIFFUSERS_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("❌ Google Generative AI not installed. Run: pip install google-generativeai")
    genai = None
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent
from config.settings import settings

logger = logging.getLogger(__name__)

class ImageAgent(BaseAgent):
    def __init__(self):
        super().__init__("ImageAgent")
        
        # Check for required dependencies
        self.dependencies_available = all([plt, np, Image])
        if not self.dependencies_available:
            logger.warning("Some image generation dependencies are missing. Image features may be limited.")
        
        # Initialize Gemini for AI image generation
        self.gemini_model = None
        if GEMINI_AVAILABLE and settings.gemini_api_key:
            try:
                logger.info("Configuring Google Gemini for image generation...")
                genai.configure(api_key=settings.gemini_api_key)
                
                # Try to use Gemini 2.5 Flash Image model
                try:
                    self.gemini_model = genai.GenerativeModel("gemini-2.5-flash-image")
                    logger.info("✅ Gemini 2.5 Flash Image model configured")
                except Exception:
                    try:
                        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                        logger.info("✅ Gemini 2.0 Flash model configured (fallback)")
                    except Exception:
                        self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                        logger.info(f"✅ Gemini {settings.gemini_model} configured (default)")
                        
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {str(e)}")
                self.gemini_model = None
        elif not settings.gemini_api_key:
            logger.warning("Gemini API key not found in settings")
        
        # Initialize FLUX.1-schnell as primary AI image generator
        self.flux_pipeline = None
        if DIFFUSERS_AVAILABLE:
            try:
                logger.info("Loading FLUX.1-schnell for AI image generation...")
                self.flux_pipeline = FluxPipeline.from_pretrained(
                    "black-forest-labs/FLUX.1-schnell",
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
                )
                
                if torch.cuda.is_available():
                    self.flux_pipeline = self.flux_pipeline.to("cuda")
                    logger.info("✅ FLUX.1-schnell loaded on GPU")
                else:
                    logger.info("✅ FLUX.1-schnell loaded on CPU (will be slower)")
                
                # Optimize for memory
                self.flux_pipeline.enable_model_cpu_offload()
                
            except Exception as e:
                logger.error(f"Failed to load FLUX.1-schnell: {str(e)}")
                self.flux_pipeline = None

        # Keep Stable Diffusion as fallback
        self.sd_pipeline = None
        if DIFFUSERS_AVAILABLE and not self.flux_pipeline:
            try:
                logger.info("Loading Stable Diffusion as fallback...")
                self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                    settings.stable_diffusion_model if hasattr(settings, 'stable_diffusion_model') else "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    use_safetensors=True
                )
                
                if torch.cuda.is_available():
                    self.sd_pipeline = self.sd_pipeline.to("cuda")
                    logger.info("✅ Stable Diffusion loaded on GPU as fallback")
                else:
                    logger.info("✅ Stable Diffusion loaded on CPU as fallback")
                
                # Optimize for memory
                self.sd_pipeline.enable_attention_slicing()
                if hasattr(self.sd_pipeline, 'enable_xformers_memory_efficient_attention'):
                    try:
                        self.sd_pipeline.enable_xformers_memory_efficient_attention()
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Failed to load Stable Diffusion fallback: {str(e)}")
                self.sd_pipeline = None
        
        self.image_types = {
            "infographic": self._create_infographic,
            "chart": self._create_chart,
            "quote": self._create_quote_image,
            "process": self._create_process_diagram,
            "comparison": self._create_comparison_chart,
            "timeline": self._create_timeline,
            "achievement": self._create_achievement_badge,
            "ai_generated": self._create_ai_image
        }
        self.color_schemes = {
            "professional": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
            "corporate": ["#003366", "#0066CC", "#66B2FF", "#CCE5FF"],
            "modern": ["#667eea", "#764ba2", "#f093fb", "#f5576c"],
            "minimal": ["#2c3e50", "#95a5a6", "#ecf0f1", "#34495e"],
            "linkedin": ["#0077B5", "#00A0DC", "#40E0D0", "#87CEEB"]
        }
        
        # Ensure images directory exists
        os.makedirs("data/images", exist_ok=True)
    
    def get_system_prompt(self) -> str:
        return """You are an expert visual content creator specializing in LinkedIn graphics and infographics.

        Your responsibilities:
        1. Analyze post content to determine optimal visual representation
        2. Create professional, engaging visuals that complement the text
        3. Design images optimized for LinkedIn's display format
        4. Ensure visual accessibility and brand consistency
        5. Generate images that drive engagement and shareability

        Image Types Supported:
        - Infographics: Data visualization and key points presentation
        - Charts: Statistical data and metrics visualization
        - Quote Images: Text-based inspirational or insight graphics
        - Process Diagrams: Step-by-step process visualization
        - Comparison Charts: Side-by-side comparisons
        - Timelines: Chronological progression displays
        - Achievement Badges: Milestone and accomplishment graphics

        Design Principles:
        - Professional aesthetics suitable for business audience
        - Clear, readable typography
        - Strategic use of brand colors
        - Optimal dimensions for LinkedIn (1200x630 recommended)
        - High contrast for accessibility
        - Clean, uncluttered layouts"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visual content based on post content and requirements
        """
        if not self.dependencies_available:
            return {"error": "Image generation dependencies not available. Please install: pip install matplotlib pillow numpy seaborn"}
        
        if not self.validate_input(input_data, ["post_content"]):
            return {"error": "Missing required post_content"}
        
        try:
            post_content = input_data["post_content"]
            image_type = input_data.get("image_type", "infographic")
            style = input_data.get("style", "professional")
            
            # Analyze content to extract visual elements
            visual_elements = await self._analyze_content_for_visuals(post_content)
            
            # Generate image based on type
            if image_type in self.image_types:
                image_path = await self.image_types[image_type](visual_elements, style)
            else:
                # Default to infographic
                image_path = await self._create_infographic(visual_elements, style)
            
            result = {
                "image_path": image_path,
                "image_type": image_type,
                "style_used": style,
                "visual_elements": visual_elements,
                "dimensions": f"{getattr(settings, 'image_width', 1200)}x{getattr(settings, 'image_height', 630)}",
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated {image_type} image with {style} style")
            return result
            
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_content_for_visuals(self, post_content: str) -> Dict[str, Any]:
        """
        Analyze post content to extract visual elements
        """
        content_analysis_prompt = f"""Analyze this LinkedIn post content and extract visual elements that could be represented graphically:

        POST CONTENT:
        {post_content}

        Extract and categorize:
        1. Key statistics or numbers mentioned
        2. Main points or insights (3-5 key points)
        3. Processes or steps described
        4. Comparisons made
        5. Timeline elements
        6. Achievements or milestones
        7. Quotes or key phrases worth highlighting

        Return analysis in this JSON format:
        {{
            "key_statistics": ["stat1", "stat2"],
            "main_points": ["point1", "point2", "point3"],
            "processes": ["step1", "step2", "step3"],
            "comparisons": ["item1 vs item2"],
            "timeline_elements": ["event1", "event2"],
            "achievements": ["achievement1"],
            "key_quotes": ["quote1"],
            "suggested_visual_type": "infographic/chart/quote/process/comparison/timeline/achievement"
        }}"""
        
        try:
            analysis_result = await self.call_ollama(
                prompt=content_analysis_prompt,
                system_prompt="You are an expert at analyzing content for visual representation opportunities."
            )
            
            # Parse the response or provide defaults
            import json
            try:
                if "{" in analysis_result and "}" in analysis_result:
                    start = analysis_result.find("{")
                    end = analysis_result.rfind("}") + 1
                    json_str = analysis_result[start:end]
                    parsed = json.loads(json_str)
                    return parsed
            except:
                pass
            
            # Fallback analysis
            return self._fallback_content_analysis(post_content)
            
        except Exception as e:
            logger.warning(f"Content analysis failed: {str(e)}, using fallback")
            return self._fallback_content_analysis(post_content)
    
    def _fallback_content_analysis(self, post_content: str) -> Dict[str, Any]:
        """Fallback content analysis when AI analysis fails"""
        words = post_content.split()
        
        # Simple extraction
        numbers = [word for word in words if word.replace('%', '').replace('$', '').replace(',', '').isdigit()]
        
        # Split content into sentences for key points
        sentences = [s.strip() for s in post_content.split('.') if s.strip()]
        key_points = sentences[:3] if len(sentences) >= 3 else sentences
        
        return {
            "key_statistics": numbers[:3],
            "main_points": key_points,
            "processes": [],
            "comparisons": [],
            "timeline_elements": [],
            "achievements": [],
            "key_quotes": [sentences[0]] if sentences else ["Professional Achievement"],
            "suggested_visual_type": "infographic"
        }
    
    async def _create_infographic(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create an infographic-style image"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Set background
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            # Remove axes
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Title
            main_title = "Key Insights"
            ax.text(5, 5.5, main_title, fontsize=24, fontweight='bold', 
                   ha='center', va='center', color=colors[0])
            
            # Main points as visual elements
            points = visual_elements.get("main_points", ["Professional Growth", "Innovation", "Leadership"])
            y_positions = [4.2, 3.2, 2.2]
            
            for i, point in enumerate(points[:3]):
                if i < len(y_positions):
                    # Create colored circles as bullet points
                    circle = plt.Circle((1, y_positions[i]), 0.15, color=colors[i % len(colors)])
                    ax.add_patch(circle)
                    
                    # Add text
                    ax.text(1.5, y_positions[i], point[:60], fontsize=14, 
                           va='center', ha='left', color='#2c3e50', weight='bold')
            
            # Add statistics if available
            stats = visual_elements.get("key_statistics", [])
            if stats:
                ax.text(5, 1.2, "Key Metrics", fontsize=18, fontweight='bold', 
                       ha='center', va='center', color=colors[0])
                
                for i, stat in enumerate(stats[:3]):
                    x_pos = 2 + (i * 2)
                    # Create stat boxes
                    rect = patches.Rectangle((x_pos-0.5, 0.3), 1, 0.6, 
                                           linewidth=2, edgecolor=colors[i % len(colors)], 
                                           facecolor=colors[i % len(colors)], alpha=0.3)
                    ax.add_patch(rect)
                    
                    ax.text(x_pos, 0.6, str(stat), fontsize=16, fontweight='bold',
                           ha='center', va='center', color=colors[i % len(colors)])
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/infographic_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating infographic: {str(e)}")
            return ""
    
    async def _create_chart(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create a chart/graph image"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Sample data - in real implementation, extract from visual_elements
            categories = ["Q1", "Q2", "Q3", "Q4"]
            values = [20, 35, 30, 35]  # Sample values
            
            # Create bar chart
            bars = ax.bar(categories, values, color=colors[:len(categories)])
            
            # Customize chart
            ax.set_title("Performance Metrics", fontsize=20, fontweight='bold', pad=20)
            ax.set_ylabel("Value", fontsize=14)
            ax.set_xlabel("Period", fontsize=14)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Style the chart
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_facecolor('white')
            fig.patch.set_facecolor('white')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/chart_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return ""
    
    async def _create_quote_image(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create a quote/text-based image"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Set background
            ax.set_facecolor(colors[0])
            fig.patch.set_facecolor(colors[0])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Get quote text
            quotes = visual_elements.get("key_quotes", ["Success comes from continuous learning and adaptation"])
            main_quote = quotes[0] if quotes else "Professional Excellence"
            
            # Add quote marks
            ax.text(5, 4.5, '"', fontsize=80, ha='center', va='center', 
                   color='white', alpha=0.3, weight='bold')
            
            # Main quote text
            ax.text(5, 3, main_quote[:100], fontsize=20, ha='center', va='center',
                   color='white', weight='bold', wrap=True)
            
            # Attribution or context
            ax.text(5, 1.5, "- Professional Insight", fontsize=14, ha='center', va='center',
                   color='white', alpha=0.8, style='italic')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/quote_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor=colors[0], edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating quote image: {str(e)}")
            return ""
    
    async def _create_process_diagram(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create a process flow diagram"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Set background
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Title
            ax.text(5, 5.5, "Process Flow", fontsize=24, fontweight='bold',
                   ha='center', va='center', color=colors[0])
            
            # Process steps
            processes = visual_elements.get("processes", ["Plan", "Execute", "Review", "Optimize"])
            step_positions = [(2, 3.5), (4, 3.5), (6, 3.5), (8, 3.5)]
            
            for i, (process, pos) in enumerate(zip(processes[:4], step_positions)):
                # Create process boxes
                rect = patches.FancyBboxPatch((pos[0]-0.6, pos[1]-0.4), 1.2, 0.8,
                                            boxstyle="round,pad=0.1",
                                            facecolor=colors[i % len(colors)],
                                            edgecolor='white', linewidth=2)
                ax.add_patch(rect)
                
                # Add process text
                ax.text(pos[0], pos[1], process[:10], fontsize=12, fontweight='bold',
                       ha='center', va='center', color='white')
                
                # Add arrows between steps
                if i < len(processes) - 1 and i < 3:
                    arrow = patches.FancyArrowPatch((pos[0] + 0.6, pos[1]), 
                                                  (step_positions[i+1][0] - 0.6, step_positions[i+1][1]),
                                                  arrowstyle='->', mutation_scale=20,
                                                  color=colors[0], linewidth=2)
                    ax.add_patch(arrow)
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/process_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating process diagram: {str(e)}")
            return ""
    
    async def _create_comparison_chart(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create a comparison chart"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Sample comparison data
            categories = ['Performance', 'Efficiency', 'Quality', 'Innovation']
            before = [60, 55, 70, 45]
            after = [85, 80, 90, 75]
            
            x = np.arange(len(categories))
            width = 0.35
            
            # Create bars
            bars1 = ax.bar(x - width/2, before, width, label='Before', color=colors[0], alpha=0.8)
            bars2 = ax.bar(x + width/2, after, width, label='After', color=colors[1], alpha=0.8)
            
            # Customize chart
            ax.set_title('Performance Comparison', fontsize=20, fontweight='bold', pad=20)
            ax.set_xlabel('Metrics', fontsize=14)
            ax.set_ylabel('Score', fontsize=14)
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{int(height)}', ha='center', va='bottom', fontsize=10)
            
            # Style
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_facecolor('white')
            fig.patch.set_facecolor('white')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/comparison_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating comparison chart: {str(e)}")
            return ""
    
    async def _create_timeline(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create a timeline visualization"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Set background
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Title
            ax.text(5, 5.5, "Project Timeline", fontsize=24, fontweight='bold',
                   ha='center', va='center', color=colors[0])
            
            # Timeline elements
            timeline_items = visual_elements.get("timeline_elements", 
                                               ["Planning", "Development", "Testing", "Launch"])
            
            # Draw timeline line
            ax.plot([1, 9], [3, 3], color=colors[0], linewidth=4)
            
            # Add timeline points
            x_positions = np.linspace(1.5, 8.5, len(timeline_items[:4]))
            
            for i, (item, x_pos) in enumerate(zip(timeline_items[:4], x_positions)):
                # Timeline point
                circle = plt.Circle((x_pos, 3), 0.2, color=colors[i % len(colors)], zorder=3)
                ax.add_patch(circle)
                
                # Label above
                ax.text(x_pos, 3.8, item[:15], fontsize=12, fontweight='bold',
                       ha='center', va='center', color=colors[0])
                
                # Date below (sample)
                date_label = f"Week {i+1}"
                ax.text(x_pos, 2.2, date_label, fontsize=10,
                       ha='center', va='center', color='#666666')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/timeline_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating timeline: {str(e)}")
            return ""
    
    async def _create_achievement_badge(self, visual_elements: Dict[str, Any], style: str) -> str:
        """Create an achievement badge/celebration image"""
        try:
            # Set up the figure
            fig, ax = plt.subplots(figsize=(12, 6.3))
            colors = self.color_schemes.get(style, self.color_schemes["professional"])
            
            # Set background with gradient effect
            ax.set_facecolor(colors[0])
            fig.patch.set_facecolor(colors[0])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Achievement badge circle
            badge_circle = plt.Circle((5, 3), 2, color='white', alpha=0.9, zorder=2)
            ax.add_patch(badge_circle)
            
            # Inner achievement circle
            inner_circle = plt.Circle((5, 3), 1.5, color=colors[1], alpha=0.8, zorder=3)
            ax.add_patch(inner_circle)
            
            # Achievement text
            achievements = visual_elements.get("achievements", ["Achievement Unlocked!"])
            main_achievement = achievements[0] if achievements else "Success!"
            
            ax.text(5, 3.3, "🏆", fontsize=40, ha='center', va='center', zorder=4)
            ax.text(5, 2.7, main_achievement[:20], fontsize=14, fontweight='bold',
                   ha='center', va='center', color='white', zorder=4)
            
            # Celebration elements (stars)
            star_positions = [(2, 4.5), (8, 4.5), (1.5, 2), (8.5, 2), (3, 1), (7, 1)]
            for pos in star_positions:
                ax.text(pos[0], pos[1], "⭐", fontsize=20, ha='center', va='center',
                       color='yellow', alpha=0.8)
            
            # Congratulatory text
            ax.text(5, 0.5, "Congratulations on this milestone!", 
                   fontsize=16, ha='center', va='center', color='white', 
                   style='italic', weight='bold')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/achievement_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(image_path, dpi=300, bbox_inches='tight',
                       facecolor=colors[0], edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating achievement badge: {str(e)}")
            return ""
    
    async def _create_ai_image(self, visual_elements: Dict[str, Any], style: str) -> str:
        """
        Generate an AI image using FLUX.1-schnell (primary) or other methods
        """
        # Try FLUX.1-schnell first (best quality and speed)
        if self.flux_pipeline:
            try:
                return await self._generate_flux_image(visual_elements, style)
            except Exception as e:
                logger.error(f"FLUX.1-schnell generation failed: {str(e)}")
                logger.info("Falling back to other methods...")
        
        # Try Gemini second
        if self.gemini_model:
            try:
                return await self._generate_gemini_image(visual_elements, style)
            except Exception as e:
                logger.error(f"Gemini image generation failed: {str(e)}")
                logger.info("Falling back to Stable Diffusion...")
        
        # Fallback to Stable Diffusion
        if self.sd_pipeline:
            try:
                return await self._generate_stable_diffusion_image(visual_elements, style)
            except Exception as e:
                logger.error(f"Stable Diffusion generation failed: {str(e)}")
        
        # Final fallback to programmatic infographic
        logger.warning("All AI image generation methods failed, using programmatic infographic")
        return await self._create_infographic(visual_elements, style)
    
    async def _generate_flux_image(self, visual_elements: Dict[str, Any], style: str) -> str:
        """
        Generate high-quality image using FLUX.1-schnell
        """
        try:
            # Build prompt from visual elements
            prompt = await self._build_ai_image_prompt(visual_elements, style)
            
            logger.info(f"Generating FLUX.1-schnell image with prompt: {prompt[:100]}...")
            
            # Generate image with FLUX.1-schnell (1-4 steps for fast generation)
            with torch.no_grad():
                image = self.flux_pipeline(
                    prompt=prompt,
                    height=832,  # FLUX optimal dimensions
                    width=1216,  # FLUX optimal dimensions (close to LinkedIn 1200x630)
                    num_inference_steps=4,  # Fast generation with schnell
                    guidance_scale=0.0,  # FLUX schnell doesn't use guidance
                    max_sequence_length=256  # Control prompt length
                ).images[0]
            
            # Resize to LinkedIn optimal dimensions
            linkedin_image = image.resize((1200, 630), Image.Resampling.LANCZOS)
            
            # Save the generated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/flux_generated_{timestamp}.png"
            linkedin_image.save(image_path, "PNG", quality=95, optimize=True)
            
            logger.info(f"✅ FLUX.1-schnell image generated successfully: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error generating FLUX image: {str(e)}")
            raise
    
    async def _generate_gemini_image(self, visual_elements: Dict[str, Any], style: str) -> str:
        """
        Generate image using Google Gemini 2.0 Flash with proper image generation prompt
        """
        try:
            # Build prompt from visual elements
            base_prompt = await self._build_ai_image_prompt(visual_elements, style)
            
            # Add explicit image generation instruction
            image_prompt = f"Generate an image: {base_prompt}"
            
            logger.info(f"Generating Gemini image with prompt: {image_prompt[:100]}...")
            
            # Generate image using Gemini with proper configuration
            try:
                response = self.gemini_model.generate_content(
                    image_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=settings.gemini_max_tokens,
                        temperature=0.7
                    )
                )
            except Exception as sync_error:
                logger.info("Sync call failed, trying async...")
                response = await self.gemini_model.generate_content_async(image_prompt)
            
            # Check response
            if not response or not response.candidates:
                raise Exception("No response from Gemini")
                
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise Exception("No content in Gemini response")
            
            # Look for image data in response parts
            image_data = None
            for part in candidate.content.parts:
                # Check for inline data (image)
                if hasattr(part, 'inline_data') and part.inline_data:
                    if part.inline_data.mime_type.startswith('image/'):
                        image_data = part.inline_data.data
                        break
                # Check for file data (newer API)
                elif hasattr(part, 'file_data') and part.file_data:
                    logger.warning("File data format not yet supported")
                    continue
            
            if not image_data:
                # If no image in response, this model might not support image generation
                raise Exception("Gemini model does not support image generation or returned no image data")
            
            # Save the generated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/gemini_generated_{timestamp}.png"
            
            # Decode and save image
            import base64
            try:
                decoded_data = base64.b64decode(image_data)
                with open(image_path, 'wb') as f:
                    f.write(decoded_data)
                
                logger.info(f"✅ Gemini image generated successfully: {image_path}")
                return image_path
                
            except Exception as decode_error:
                raise Exception(f"Failed to decode image data: {str(decode_error)}")
            
        except Exception as e:
            logger.error(f"Error generating Gemini image: {str(e)}")
            raise
    
    async def _generate_stable_diffusion_image(self, visual_elements: Dict[str, Any], style: str) -> str:
        """
        Generate image using Stable Diffusion (fallback)
        """
        try:
            # Build prompt from visual elements
            prompt = await self._build_ai_image_prompt(visual_elements, style)
            
            logger.info(f"Generating Stable Diffusion image with prompt: {prompt[:100]}...")
            
            # Generate image
            with torch.no_grad():
                image = self.sd_pipeline(
                    prompt=prompt,
                    height=getattr(settings, 'image_height', 630),
                    width=getattr(settings, 'image_width', 1200),
                    num_inference_steps=getattr(settings, 'ai_image_steps', 20),
                    guidance_scale=getattr(settings, 'ai_image_guidance', 7.5),
                    negative_prompt="low quality, blurry, distorted, text, watermark, signature"
                ).images[0]
            
            # Save the generated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/sd_generated_{timestamp}.png"
            image.save(image_path, "PNG", quality=getattr(settings, 'image_quality', 95))
            
            logger.info(f"✅ Stable Diffusion image generated successfully: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error generating Stable Diffusion image: {str(e)}")
            raise
    
    async def _build_ai_image_prompt(self, visual_elements: Dict[str, Any], style: str) -> str:
        """
        Build a detailed prompt for AI image generation based on content analysis
        """
        try:
            # Extract key elements
            main_points = visual_elements.get("main_points", [])
            key_quotes = visual_elements.get("key_quotes", [])
            achievements = visual_elements.get("achievements", [])
            processes = visual_elements.get("processes", [])
            
            # Build context for prompt generation
            context = f"""
            Main Points: {', '.join(main_points[:3])}
            Key Quotes: {', '.join(key_quotes[:2])}
            Achievements: {', '.join(achievements[:2])}
            Processes: {', '.join(processes[:3])}
            Style: {style}
            """
            
            # Use LLM to generate a detailed image prompt
            prompt_generation_request = f"""Generate a detailed, professional image prompt for LinkedIn based on this content analysis:
            
            {context}
            
            Create a prompt for a high-quality, professional image that would be engaging on LinkedIn. Focus on:
            - Professional business aesthetics
            - Clean, modern design
            - Colors appropriate for {style} style
            - Visual metaphors for the main concepts
            - No text or words in the image
            - High quality, detailed, realistic style
            
            Return ONLY the image prompt, no additional text or explanation."""
            
            ai_prompt = await self.call_ollama(
                prompt=prompt_generation_request,
                system_prompt="You are an expert at creating detailed prompts for AI image generation, specifically for professional LinkedIn content."
            )
            
            # Clean and enhance the prompt
            if ai_prompt and len(ai_prompt.strip()) > 20:
                enhanced_prompt = f"Professional LinkedIn image, {ai_prompt.strip()}, high quality, detailed, realistic, business professional, clean modern design, no text"
                return enhanced_prompt[:500]  # Limit prompt length
            else:
                # Fallback prompt
                topic = main_points[0] if main_points else "professional business"
                return f"Professional LinkedIn image about {topic}, high quality, modern business aesthetic, clean design, no text, realistic style"
                
        except Exception as e:
            logger.error(f"Error building AI image prompt: {str(e)}")
            return "Professional business image for LinkedIn, modern clean design, high quality, no text"
    
    async def optimize_image_for_linkedin(self, image_path: str) -> str:
        """
        Optimize image dimensions and quality for LinkedIn
        """
        try:
            if not os.path.exists(image_path):
                return image_path
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to optimal LinkedIn dimensions
                target_size = (getattr(settings, 'image_width', 1200), getattr(settings, 'image_height', 630))
                img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Save optimized version
                optimized_path = image_path.replace('.png', '_optimized.png')
                img_resized.save(optimized_path, 'PNG', quality=getattr(settings, 'image_quality', 95), optimize=True)
                
                return optimized_path
                
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            return image_path