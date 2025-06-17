from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, F, FloatField, Value
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Artwork, CommissionRequest, PayPalAccount, ModelApplication, ModelImage
from .serializers import ArtworkSerializer, CommissionRequestSerializer
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

# API Views
class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'medium', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Artwork.objects.all()
        
        # Get filter parameters
        status = self.request.query_params.get('status')
        medium = self.request.query_params.get('medium')
        category = self.request.query_params.get('category')
        sort = self.request.query_params.get('sort', 'newest')
        
        # Apply filters if they are not 'all' and not None
        if status and status != 'all':
            queryset = queryset.filter(status=status)
        if medium and medium != 'all':
            queryset = queryset.filter(medium=medium)
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        # Apply sorting
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'price_high':
            # When sorting by price, exclude NOT_AVAILABLE items
            queryset = queryset.exclude(status='NOT_AVAILABLE').order_by('-price', '-created_at')
        elif sort == 'price_low':
            # When sorting by price, exclude NOT_AVAILABLE items
            queryset = queryset.exclude(status='NOT_AVAILABLE').order_by('price', '-created_at')
        
        return queryset

class CommissionRequestViewSet(viewsets.ModelViewSet):
    queryset = CommissionRequest.objects.all().order_by('-created_at')
    serializer_class = CommissionRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'medium', 'category']
    search_fields = ['name', 'description']

# Template Views
def home(request):
    # Get filter parameters
    status = request.GET.getlist('status')
    medium = request.GET.getlist('medium')
    category = request.GET.getlist('category')
    
    # Base queryset
    featured_artworks = Artwork.objects.filter(status='FOR_SALE').order_by('-price')[:3]
    latest_artworks = Artwork.objects.all().order_by('-created_at')
    
    # Build conditions for each group
    conditions = Q()
    
    # Status group
    if status and 'all' not in status:
        status_condition = Q()
        for s in status:
            status_condition |= Q(status=s)
        conditions &= status_condition

    # Medium group
    if medium and 'all' not in medium:
        medium_condition = Q()
        for m in medium:
            medium_condition |= Q(medium=m)
        conditions &= medium_condition

    # Category group
    if category and 'all' not in category:
        category_condition = Q()
        for c in category:
            category_condition |= Q(category=c)
        conditions &= category_condition
    
    # Apply the combined conditions if any filters are present
    if status or medium or category:
        latest_artworks = latest_artworks.filter(conditions)
    
    # Limit to 25 items
    latest_artworks = latest_artworks[:25]
    
    # Serialize the data
    featured_serializer = ArtworkSerializer(featured_artworks, many=True)
    latest_serializer = ArtworkSerializer(latest_artworks, many=True)
    
    return render(request, 'home.html', {
        'featured_artworks': featured_artworks,
        'latest_artworks': latest_artworks,
        'featured_json': featured_serializer.data,
        'latest_json': latest_serializer.data,
        'current_filters': {
            'status': status,
            'medium': medium,
            'category': category
        }
    })

def commission(request):
    if request.method == 'POST':
        # Handle commission request form submission
        pass
    return render(request, 'commission.html')

def artwork_detail(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    paypal_account = PayPalAccount.get_active_account()
    
    # Find similar artworks based on matching both medium and category
    similar_artworks = Artwork.objects.filter(
        medium=artwork.medium,
        category=artwork.category
    ).exclude(
        id=artwork.id  # Exclude the current artwork
    ).order_by('?')[:3]  # Get 3 random matching artworks
    
    return render(request, 'artwork_detail.html', {
        'artwork': artwork,
        'paypal_account': paypal_account,
        'similar_artworks': similar_artworks
    })

def gallery(request):
    # Get filter parameters
    status = request.GET.get('status')
    medium = request.GET.get('medium')
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    # Base queryset
    artworks = Artwork.objects.all()
    
    # Apply filters
    if status:
        artworks = artworks.filter(status=status)
    if medium:
        artworks = artworks.filter(medium=medium)
    if category:
        artworks = artworks.filter(category=category)
    if search:
        artworks = artworks.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    # Order by newest first
    artworks = artworks.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(artworks, 20)  # Show 20 artworks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gallery.html', {
        'page_obj': page_obj,
        'current_filters': {
            'status': status,
            'medium': medium,
            'category': category,
            'search': search
        }
    })

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            artwork = Artwork.objects.get(id=data['artwork_id'])
            
            # Mark artwork as sold
            artwork.status = 'SOLD'
            artwork.save()
            
            # Prepare email content
            context = {
                'artwork': artwork,
                'customer_name': data['name'],
                'customer_email': data['email'],
                'customer_phone': data['phone'],
                'customer_address': data['address'],
            }
            
            # Render email templates
            html_message = render_to_string('emails/purchase_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            # Send confirmation email to customer
            send_mail(
                subject=f'Purchase Confirmation - {artwork.title}',
                message=plain_message,
                from_email='noreply@yourdomain.com',  # Update this with your email
                recipient_list=[data['email']],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Send notification email to artist
            artist_message = render_to_string('emails/artist_notification.html', context)
            artist_plain_message = strip_tags(artist_message)
            
            send_mail(
                subject=f'New Artwork Purchase - {artwork.title}',
                message=artist_plain_message,
                from_email='noreply@yourdomain.com',  # Update this with your email
                recipient_list=['aboydmobile@gmail.com'],  # Update this with your email
                html_message=artist_message,
                fail_silently=False,
            )
            
            return render(request, 'payment_success.html', {
                'artwork': artwork,
                'customer_name': data['name']
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def models(request):
    if request.method == 'POST':
        try:
            # Create the model application
            application = ModelApplication.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST.get('phone', ''),
                modeling_type=request.POST['modeling_type'],
                description=request.POST['description'],
                availability=request.POST['availability'],
                additional_info=request.POST.get('additional_info', '')
            )

            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for image in images:
                ModelImage.objects.create(
                    application=application,
                    image=image
                )

            # Send confirmation email to applicant
            context = {
                'name': application.name,
                'modeling_type': application.get_modeling_type_display()
            }
            
            html_message = render_to_string('emails/model_application_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Model Application Received',
                message=plain_message,
                from_email='noreply@yourdomain.com',  # Update this with your email
                recipient_list=[application.email],
                html_message=html_message,
                fail_silently=False,
            )

            # Send notification email to artist
            artist_message = render_to_string('emails/model_application_notification.html', context)
            artist_plain_message = strip_tags(artist_message)
            
            send_mail(
                subject='New Model Application Received',
                message=artist_plain_message,
                from_email='noreply@yourdomain.com',  # Update this with your email
                recipient_list=['aboydmobile@gmail.com'],  # Update this with your email
                html_message=artist_message,
                fail_silently=False,
            )

            return render(request, 'models.html', {'success': True})
        except Exception as e:
            return render(request, 'models.html', {'error': str(e)})

    return render(request, 'models.html') 