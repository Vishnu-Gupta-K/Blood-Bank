from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from models import Donor
import crud

def generate_donor_list_pdf(db: Session, donor_ids: List[int], title: str = "Donor List", include_contact_info: bool = True) -> BytesIO:
    """
    Generate a PDF report of donors based on the provided donor IDs.
    
    Args:
        db: Database session
        donor_ids: List of donor IDs to include in the report
        title: Title of the PDF report
        include_contact_info: Whether to include contact information in the report
        
    Returns:
        BytesIO object containing the PDF data
    """
    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()
    
    # Create the PDF document using ReportLab
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get the donors from the database
    donors = []
    for donor_id in donor_ids:
        donor = crud.get_donor_by_id(db, donor_id)
        if donor:
            donors.append(donor)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Create the content for the PDF
    content = []
    
    # Add title
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 0.25 * inch))
    
    # Add generation date
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    content.append(Spacer(1, 0.25 * inch))
    
    # Add donor count
    content.append(Paragraph(f"Total Donors: {len(donors)}", normal_style))
    content.append(Spacer(1, 0.5 * inch))
    
    # Define table headers based on whether to include contact info
    if include_contact_info:
        headers = ["Name", "Blood Group", "Gender", "Phone", "Location", "Pincode"]
    else:
        headers = ["Name", "Blood Group", "Gender", "Location", "Pincode"]
    
    # Create table data
    table_data = [headers]
    
    for donor in donors:
        location = f"{donor.village}, {donor.district}, {donor.state}"
        
        if include_contact_info:
            row = [
                donor.name,
                donor.blood_group.value,
                donor.gender.value,
                donor.phone_number,
                location,
                donor.pincode
            ]
        else:
            row = [
                donor.name,
                donor.blood_group.value,
                donor.gender.value,
                location,
                donor.pincode
            ]
        
        table_data.append(row)
    
    # Create the table
    if donors:
        table = Table(table_data, repeatRows=1)
        
        # Add style to the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Add zebra striping
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.white)
        
        table.setStyle(table_style)
        content.append(table)
    else:
        content.append(Paragraph("No donors found matching the criteria.", normal_style))
    
    # Build the PDF document
    doc.build(content)
    
    # Reset the buffer position to the beginning
    buffer.seek(0)
    
    return buffer