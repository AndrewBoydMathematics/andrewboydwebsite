import os
import random
from django.core.management.base import BaseCommand
from artwork.models import Artwork

class Command(BaseCommand):
    help = 'Load artwork from the media/artwork directory'

    def handle(self, *args, **options):
        artwork_dir = os.path.join('media', 'artwork')
        
        # Clear existing artwork
        Artwork.objects.all().delete()
        
        # Get all image files
        image_files = [f for f in os.listdir(artwork_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for filename in image_files:
            # Generate a random price between £50 and £1000
            price = round(random.uniform(50, 1000), 2)
            
            # Create artwork entry
            artwork = Artwork.objects.create(
                title=os.path.splitext(filename)[0],
                description=f"A beautiful artwork titled {os.path.splitext(filename)[0]}",
                image=f"artwork/{filename}",
                status='FOR_SALE',
                price=price,
                medium='OIL' if 'oil' in filename.lower() else 'GRAPHITE',
                category='PORTRAIT' if 'portrait' in filename.lower() else 'FIGURE',
                is_featured=False
            )
            # Call save to generate tile and thumbnail images
            artwork.save()
            self.stdout.write(self.style.SUCCESS(f'Created artwork: {artwork.title}')) 