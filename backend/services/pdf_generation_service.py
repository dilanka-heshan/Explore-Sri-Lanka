"""
PDF Generation Service for Travel Plans
Creates branded PDF documents with travel itineraries, maps, and photos
"""
import os
import io
import logging
import base64
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, KeepTogether
    )
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. Install with: pip install reportlab")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests not available. Install with: pip install requests")

from models.travel_plan_models import (
    UserTravelPlan, 
    PDFGenerationRequest, 
    PDFGenerationResponse
)

logger = logging.getLogger(__name__)


class TravelPlanPDFGenerator:
    """Service for generating branded PDF travel plans"""
    
    def __init__(self):
        self.logo_path = self._get_logo_path()
        self.styles = self._setup_styles()
        self.colors = {
            'primary': colors.Color(0.2, 0.6, 0.8),  # Blue
            'secondary': colors.Color(0.8, 0.3, 0.2),  # Red/Orange
            'accent': colors.Color(0.2, 0.7, 0.3),  # Green
            'text': colors.Color(0.2, 0.2, 0.2),  # Dark gray
            'light': colors.Color(0.9, 0.9, 0.9),  # Light gray
        }
    
    def _get_logo_path(self) -> Optional[str]:
        """Get the path to the website logo"""
        # Check for logo in various locations
        possible_paths = [
            "assets/logo.png",
            "static/logo.png",
            "../my-app/public/logo.png",
            "logo.png"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _setup_styles(self):
        """Setup custom styles for the PDF"""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=self.colors['primary']
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=self.colors['primary'],
            borderWidth=0,
            borderColor=self.colors['primary'],
            borderPadding=0
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=self.colors['secondary']
        ))
        
        styles.add(ParagraphStyle(
            name='DayTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=10,
            textColor=self.colors['accent'],
            leftIndent=0,
            borderWidth=1,
            borderColor=self.colors['accent'],
            borderPadding=5
        ))
        
        styles.add(ParagraphStyle(
            name='AttractionTitle',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=5,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='PlaceTitle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=3,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Description',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=self.colors['text']
        ))
        
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=self.colors['text']
        ))
        
        return styles
    
    async def generate_pdf(
        self, 
        travel_plan: UserTravelPlan, 
        request: PDFGenerationRequest,
        output_dir: str = "generated_pdfs"
    ) -> PDFGenerationResponse:
        """Generate a PDF for the travel plan"""
        if not REPORTLAB_AVAILABLE:
            return PDFGenerationResponse(
                success=False,
                error_message="PDF generation not available. ReportLab library missing."
            )
        
        start_time = datetime.now()
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename
            safe_title = "".join(c for c in travel_plan.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{travel_plan.id[:8]}_{datetime.now().strftime('%Y%m%d')}.pdf"
            file_path = os.path.join(output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Build PDF content
            story = []
            
            # Header with logo and title
            story.extend(self._create_header(travel_plan, request))
            
            # Trip overview
            story.extend(self._create_overview(travel_plan))
            
            # Daily itinerary
            story.extend(self._create_itinerary(travel_plan, request))
            
            # Additional information
            if request.include_weather or request.include_maps:
                story.extend(self._create_additional_info(travel_plan, request))
            
            # Footer
            story.extend(self._create_footer(travel_plan))
            
            # Build PDF
            doc.build(story)
            
            # Calculate file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            generation_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Generated PDF for travel plan {travel_plan.id}: {file_path}")
            
            return PDFGenerationResponse(
                success=True,
                file_path=file_path,
                file_size_mb=round(file_size_mb, 2),
                generation_time_seconds=round(generation_time, 2)
            )
            
        except Exception as e:
            logger.error(f"Error generating PDF for travel plan {travel_plan.id}: {str(e)}")
            return PDFGenerationResponse(
                success=False,
                error_message=str(e)
            )
    
    def _create_header(self, travel_plan: UserTravelPlan, request: PDFGenerationRequest) -> List:
        """Create PDF header with logo and title"""
        elements = []
        
        # Logo and title row
        header_data = []
        
        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=2*inch, height=1*inch, hAlign='LEFT')
                header_data.append([logo, ""])
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
                header_data.append(["", ""])
        else:
            header_data.append(["EXPLORE SRI LANKA", ""])
        
        if header_data:
            header_table = Table(header_data, colWidths=[3*inch, 3*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
        
        elements.append(Spacer(1, 20))
        
        # Title
        title = request.custom_title if request.custom_title else travel_plan.title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtitle with dates
        subtitle_parts = [f"{travel_plan.trip_duration_days} Days in Sri Lanka"]
        if travel_plan.planned_start_date:
            subtitle_parts.append(f"Starting {travel_plan.planned_start_date.strftime('%B %d, %Y')}")
        subtitle = " • ".join(subtitle_parts)
        elements.append(Paragraph(subtitle, self.styles['CustomSubheading']))
        
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.colors['primary']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_overview(self, travel_plan: UserTravelPlan) -> List:
        """Create trip overview section"""
        elements = []
        
        elements.append(Paragraph("Trip Overview", self.styles['CustomHeading']))
        
        # Overview table
        overview_data = [
            ["Duration:", f"{travel_plan.trip_duration_days} days"],
            ["Budget Level:", travel_plan.budget_level.replace('_', ' ').title()],
            ["Trip Type:", travel_plan.trip_type.title()],
            ["Destinations:", travel_plan.destination_summary],
        ]
        
        if travel_plan.interests:
            overview_data.append(["Interests:", ", ".join(travel_plan.interests)])
        
        if travel_plan.description:
            overview_data.append(["Description:", travel_plan.description])
        
        overview_table = Table(overview_data, colWidths=[1.5*inch, 4.5*inch])
        overview_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.colors['light']]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['light']),
        ]))
        
        elements.append(overview_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_itinerary(self, travel_plan: UserTravelPlan, request: PDFGenerationRequest) -> List:
        """Create detailed daily itinerary"""
        elements = []
        
        elements.append(Paragraph("Daily Itinerary", self.styles['CustomHeading']))
        elements.append(Spacer(1, 10))
        
        # Extract daily itineraries from travel plan data
        daily_itineraries = travel_plan.travel_plan_data.get('daily_itineraries', [])
        
        for day_idx, day in enumerate(daily_itineraries, 1):
            # Day header
            day_title = f"Day {day_idx}"
            if 'cluster_name' in day:
                day_title += f": {day['cluster_name']}"
            
            elements.append(Paragraph(day_title, self.styles['DayTitle']))
            elements.append(Spacer(1, 8))
            
            # Day summary
            if 'summary' in day:
                elements.append(Paragraph(day['summary'], self.styles['Description']))
                elements.append(Spacer(1, 8))
            
            # Attractions
            if 'attractions' in day:
                for attraction in day['attractions']:
                    attraction_elements = self._create_attraction_section(attraction)
                    elements.extend(attraction_elements)
            
            # Enhanced places (restaurants, hotels, etc.)
            if 'places' in day:
                places_elements = self._create_places_section(day['places'])
                elements.extend(places_elements)
            
            # Travel information
            if 'travel_info' in day:
                travel_elements = self._create_travel_section(day['travel_info'])
                elements.extend(travel_elements)
            
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_attraction_section(self, attraction: Dict[str, Any]) -> List:
        """Create section for an attraction"""
        elements = []
        
        # Attraction name
        name = attraction.get('name', 'Unnamed Attraction')
        elements.append(Paragraph(f"📍 {name}", self.styles['AttractionTitle']))
        
        # Location
        if 'location' in attraction:
            elements.append(Paragraph(f"Location: {attraction['location']}", self.styles['Description']))
        
        # Description
        if 'description' in attraction:
            elements.append(Paragraph(attraction['description'], self.styles['Description']))
        
        # Details table
        details = []
        if 'duration' in attraction:
            details.append(["Recommended Duration:", attraction['duration']])
        if 'best_time' in attraction:
            details.append(["Best Time to Visit:", attraction['best_time']])
        if 'entrance_fee' in attraction:
            details.append(["Entrance Fee:", attraction['entrance_fee']])
        if 'category' in attraction:
            details.append(["Category:", attraction['category']])
        
        if details:
            details_table = Table(details, colWidths=[1.5*inch, 3*inch])
            details_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(details_table)
        
        elements.append(Spacer(1, 10))
        return elements
    
    def _create_places_section(self, places: Dict[str, Any]) -> List:
        """Create section for enhanced places (restaurants, hotels, etc.)"""
        elements = []
        
        for place_type, place_list in places.items():
            if not place_list:
                continue
                
            # Section header
            type_title = place_type.replace('_', ' ').title()
            elements.append(Paragraph(f"🏪 {type_title}", self.styles['CustomSubheading']))
            
            for place in place_list:
                if isinstance(place, dict):
                    # Place name and details
                    name = place.get('name', 'Unknown Place')
                    elements.append(Paragraph(f"• {name}", self.styles['PlaceTitle']))
                    
                    if 'rating' in place:
                        rating_text = f"Rating: {'⭐' * int(place['rating'])} ({place['rating']}/5)"
                        elements.append(Paragraph(rating_text, self.styles['Description']))
                    
                    if 'price_level' in place:
                        price_text = f"Price Level: {'$' * place['price_level']}"
                        elements.append(Paragraph(price_text, self.styles['Description']))
                    
                    if 'address' in place:
                        elements.append(Paragraph(f"Address: {place['address']}", self.styles['Description']))
                    
                    elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_travel_section(self, travel_info: Dict[str, Any]) -> List:
        """Create travel information section"""
        elements = []
        
        elements.append(Paragraph("🚗 Travel Information", self.styles['CustomSubheading']))
        
        travel_details = []
        if 'distance' in travel_info:
            travel_details.append(["Distance:", travel_info['distance']])
        if 'duration' in travel_info:
            travel_details.append(["Travel Time:", travel_info['duration']])
        if 'transportation' in travel_info:
            travel_details.append(["Transportation:", travel_info['transportation']])
        
        if travel_details:
            travel_table = Table(travel_details, colWidths=[1.2*inch, 3*inch])
            travel_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            elements.append(travel_table)
        
        elements.append(Spacer(1, 10))
        return elements
    
    def _create_additional_info(self, travel_plan: UserTravelPlan, request: PDFGenerationRequest) -> List:
        """Create additional information section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Additional Information", self.styles['CustomHeading']))
        
        if request.include_weather:
            elements.extend(self._create_weather_section(travel_plan))
        
        if request.include_maps:
            elements.extend(self._create_maps_section(travel_plan))
        
        # Tips and recommendations
        elements.extend(self._create_tips_section(travel_plan))
        
        return elements
    
    def _create_weather_section(self, travel_plan: UserTravelPlan) -> List:
        """Create weather information section"""
        elements = []
        
        elements.append(Paragraph("🌤️ Weather Information", self.styles['CustomSubheading']))
        
        # General weather info for Sri Lanka
        weather_info = """
        Sri Lanka enjoys a tropical climate with distinct wet and dry seasons:
        
        • **Best Time to Visit West/South Coast:** December to March
        • **Best Time to Visit East Coast:** April to September  
        • **Temperature:** 25-30°C (77-86°F) year-round
        • **Humidity:** High (70-80%)
        • **Monsoon Seasons:** May-September (Southwest), October-January (Northeast)
        
        **Packing Recommendations:**
        • Light, breathable clothing
        • Rain jacket or umbrella
        • Sunscreen and hat
        • Comfortable walking shoes
        """
        
        elements.append(Paragraph(weather_info, self.styles['Description']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_maps_section(self, travel_plan: UserTravelPlan) -> List:
        """Create maps and location information"""
        elements = []
        
        elements.append(Paragraph("🗺️ Location Information", self.styles['CustomSubheading']))
        
        # Extract locations from travel plan
        locations = set()
        daily_itineraries = travel_plan.travel_plan_data.get('daily_itineraries', [])
        
        for day in daily_itineraries:
            if 'cluster_name' in day:
                locations.add(day['cluster_name'])
            if 'attractions' in day:
                for attraction in day['attractions']:
                    if 'location' in attraction:
                        locations.add(attraction['location'])
        
        if locations:
            locations_text = f"**Key Destinations:** {', '.join(list(locations)[:10])}"
            elements.append(Paragraph(locations_text, self.styles['Description']))
        
        # General Sri Lanka info
        sri_lanka_info = """
        **About Sri Lanka:**
        • **Capital:** Colombo (Commercial), Sri Jayawardenepura Kotte (Administrative)
        • **Size:** 65,610 km² (25,332 sq mi)
        • **Population:** ~22 million
        • **Languages:** Sinhala, Tamil, English
        • **Currency:** Sri Lankan Rupee (LKR)
        • **Time Zone:** UTC+5:30
        
        **Getting Around:**
        • **Tuk-tuks:** Great for short distances
        • **Trains:** Scenic routes, especially hill country
        • **Buses:** Extensive network, budget-friendly
        • **Private Drivers:** Recommended for convenience
        """
        
        elements.append(Paragraph(sri_lanka_info, self.styles['Description']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_tips_section(self, travel_plan: UserTravelPlan) -> List:
        """Create tips and recommendations section"""
        elements = []
        
        elements.append(Paragraph("💡 Travel Tips & Recommendations", self.styles['CustomSubheading']))
        
        tips = """
        **Essential Tips for Sri Lanka:**
        
        • **Respect Local Culture:** Dress modestly when visiting temples
        • **Remove Shoes:** Always remove footwear before entering temples
        • **Bargaining:** Common in markets and with tuk-tuk drivers
        • **Tipping:** 10% at restaurants, small amounts for services
        • **Water:** Drink bottled or filtered water
        • **Electricity:** 230V, Type D, M, G plugs
        
        **Safety & Health:**
        • **Vaccinations:** Consult your doctor before travel
        • **Sun Protection:** Strong tropical sun - use sunscreen
        • **Insect Repellent:** Recommended for evenings
        • **Travel Insurance:** Highly recommended
        
        **Cultural Etiquette:**
        • **Greetings:** "Ayubowan" (may you live long)
        • **Head Gestures:** Head wobble can mean yes/maybe
        • **Photography:** Ask permission before photographing people
        • **Buddha Images:** Never pose with your back to Buddha statues
        """
        
        elements.append(Paragraph(tips, self.styles['Description']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_footer(self, travel_plan: UserTravelPlan) -> List:
        """Create PDF footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.colors['light']))
        elements.append(Spacer(1, 10))
        
        # Footer content
        footer_text = f"""
        Generated by Explore Sri Lanka • {datetime.now().strftime('%B %d, %Y')}
        Plan ID: {travel_plan.id} • Created: {travel_plan.created_at.strftime('%B %d, %Y')}
        Visit us at www.exploresrilanka.com for more amazing travel experiences!
        """
        
        elements.append(Paragraph(footer_text, self.styles['Footer']))
        
        return elements


# Singleton instance
_pdf_generator = None

def get_pdf_generator() -> TravelPlanPDFGenerator:
    """Get the PDF generator instance"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = TravelPlanPDFGenerator()
    return _pdf_generator
