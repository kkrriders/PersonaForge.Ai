#!/usr/bin/env python3
"""
Direct test of FLUX.1-schnell without Ollama dependency
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_flux_direct():
    """Test FLUX.1-schnell directly without full agent setup"""
    logger.info("🧪 Testing FLUX.1-schnell directly...")
    
    try:
        # Check if required packages are available
        try:
            import torch
            import diffusers
            from diffusers import FluxPipeline
            logger.info(f"✅ PyTorch {torch.__version__} and Diffusers {diffusers.__version__} found")
        except ImportError as e:
            logger.error(f"❌ Missing dependencies: {e}")
            logger.info("📋 To install: pip install torch diffusers transformers accelerate")
            return False
        
        # Initialize FLUX.1-schnell pipeline
        logger.info("🔄 Loading FLUX.1-schnell...")
        try:
            pipeline = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-schnell",
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
            )
            
            if torch.cuda.is_available():
                pipeline = pipeline.to("cuda")
                logger.info("✅ FLUX.1-schnell loaded on GPU")
            else:
                logger.info("✅ FLUX.1-schnell loaded on CPU")
                
            # Enable memory optimization
            pipeline.enable_model_cpu_offload()
            
        except Exception as e:
            logger.error(f"❌ Failed to load FLUX.1-schnell: {e}")
            return False
        
        # Generate test image
        logger.info("🎨 Generating test image...")
        test_prompt = "Professional LinkedIn business image, modern office setting, clean design, high quality, no text"
        
        try:
            with torch.no_grad():
                image = pipeline(
                    prompt=test_prompt,
                    height=832,  # FLUX optimal dimensions
                    width=1216,  # FLUX optimal dimensions
                    num_inference_steps=4,  # Fast generation with schnell
                    guidance_scale=0.0,  # FLUX schnell doesn't use guidance
                    max_sequence_length=256
                ).images[0]
            
            # Save image
            os.makedirs("data/images", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"data/images/flux_test_{timestamp}.png"
            
            # Resize to LinkedIn dimensions
            linkedin_image = image.resize((1200, 630), resample=3)  # LANCZOS
            linkedin_image.save(image_path, "PNG", quality=95)
            
            logger.info(f"✅ FLUX test successful! Image saved: {image_path}")
            logger.info(f"   Original dimensions: {image.size}")
            logger.info(f"   LinkedIn dimensions: {linkedin_image.size}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        logger.info("🚀 Starting direct FLUX.1-schnell test...")
        success = await test_flux_direct()
        
        if success:
            logger.info("🎉 FLUX.1-schnell is working perfectly!")
        else:
            logger.info("⚠️  FLUX test failed. Check dependencies and GPU availability.")
    
    asyncio.run(main())