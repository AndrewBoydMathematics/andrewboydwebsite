import os
import random
from django.core.management.base import BaseCommand
from PIL import Image
import numpy as np
from artwork.models import Artwork

class Command(BaseCommand):
    help = 'Analyzes and tags artwork images'

    def analyze_image(self, image_path):
        """Analyze image to determine if it's a portrait or figure drawing"""
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale for analysis
                img_gray = img.convert('L')
                img_array = np.array(img_gray)
                
                # Get image dimensions
                height, width = img_array.shape
                aspect_ratio = width / height
                
                # Analyze brightness distribution
                # Split image into top, middle, and bottom thirds
                top_third = img_array[:height//3, :]
                middle_third = img_array[height//3:2*height//3, :]
                bottom_third = img_array[2*height//3:, :]
                
                # Calculate average brightness for each section
                top_brightness = np.mean(top_third)
                middle_brightness = np.mean(middle_third)
                bottom_brightness = np.mean(bottom_third)
                
                # Calculate brightness variation
                brightness_variation = np.std(img_array)
                
                # Determine if it's a portrait or figure
                # Portraits typically have more detail in the top region
                # and are more vertical
                is_portrait = (
                    aspect_ratio < 1.2 and  # More vertical
                    top_brightness < middle_brightness and  # More detail in top
                    brightness_variation > 50  # More contrast
                )
                
                return 'PORTRAIT' if is_portrait else 'FIGURE'
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error analyzing image {image_path}: {str(e)}"))
            return 'FIGURE'  # Default to figure if analysis fails

    def determine_medium(self, filename, image_path):
        """Determine if the artwork is an oil painting or drawing"""
        filename_lower = filename.lower()
        
        # Check filename patterns
        if any(keyword in filename_lower for keyword in ['oil', 'painting', 'canvas']):
            return 'OIL'
        if any(keyword in filename_lower for keyword in ['drawing', 'sketch', 'pencil', 'graphite']):
            return 'GRAPHITE'
            
        # If filename doesn't give clear indication, analyze the image
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale
                img_gray = img.convert('L')
                img_array = np.array(img_gray)
                
                # Calculate image statistics
                brightness = np.mean(img_array)
                contrast = np.std(img_array)
                
                # Oil paintings typically have:
                # - Higher contrast
                # - More varied brightness
                # - More texture
                if contrast > 60 and brightness < 200:
                    return 'OIL'
                else:
                    return 'GRAPHITE'
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error analyzing medium for {filename}: {str(e)}"))
            return 'GRAPHITE'  # Default to graphite if analysis fails

    def handle(self, *args, **options):
        artworks = Artwork.objects.all()
        
        for artwork in artworks:
            if not artwork.image:
                continue
                
            image_path = artwork.image.path
            if not os.path.exists(image_path):
                self.stdout.write(self.style.WARNING(f"Image file not found: {image_path}"))
                continue
            
            # Analyze image to determine category
            category = self.analyze_image(image_path)
            
            # Determine medium
            medium = self.determine_medium(artwork.image.name, image_path)
            
            # Assign status with weighted probabilities
            status = random.choices(
                ['FOR_SALE', 'SOLD', 'NOT_AVAILABLE'],
                weights=[60, 20, 20]
            )[0]
            
            # Set price if for sale
            if status == 'FOR_SALE':
                price = random.randint(50, 1000)
            else:
                price = None
            
            # Update artwork
            artwork.category = category
            artwork.medium = medium
            artwork.status = status
            if price:
                artwork.price = price
            artwork.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"{artwork.image.name}: {medium} {category} ({status})"
                )
            ) 