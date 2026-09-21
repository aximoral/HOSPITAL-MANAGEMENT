from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
import datetime

def generate_invoice_pdf(invoice_data):
    """
    Generate a professional hospital PDF invoice using ReportLab.
    Returns bytes.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.1, 0.2, 0.4)
    c.drawString(50, height - 70, "HOSPITAL MANAGEMENT SYSTEM")

    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(50, height - 90, "123 Health Ave, Medical District")
    c.drawString(50, height - 105, "Phone: +1 800-555-0199 | Web: www.hms-system.local")

    # Invoice Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawString(450, height - 70, "INVOICE")
    
    # Line separator
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, height - 120, width - 50, height - 120)

    # Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 150, "Billed To:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 170, f"Patient ID: {invoice_data.get('patient_id', 'Unknown')}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 150, f"Invoice #: {invoice_data.get('id', 'N/A')}")
    c.setFont("Helvetica", 10)
    c.drawString(350, height - 170, f"Date: {invoice_data.get('created_at', datetime.datetime.now().strftime('%Y-%m-%d'))}")
    c.drawString(350, height - 185, f"Status: {invoice_data.get('status', 'Pending')}")

    # Table Header
    y_position = height - 230
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(50, y_position - 5, width - 100, 25, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y_position, "Description")
    c.drawString(450, y_position, "Total Amount")

    # Table Content
    y_position -= 30
    c.setFont("Helvetica", 11)
    c.drawString(60, y_position, str(invoice_data.get('description', 'Medical Services')))
    c.drawString(450, y_position, f"INR {float(invoice_data.get('amount', 0)):,.2f}")

    # Line separator
    y_position -= 20
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, y_position, width - 50, y_position)

    # Total
    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(350, y_position, "TOTAL PAID:")
    c.setFillColorRGB(0.1, 0.6, 0.1) if invoice_data.get('status') == 'Paid' else c.setFillColorRGB(0.8, 0.2, 0.2)
    c.drawString(450, y_position, f"INR {float(invoice_data.get('amount', 0)):,.2f}")

    # Footer
    c.setFillColor(colors.gray)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Thank you for choosing our hospital. For billing inquiries, contact billing@hms-system.local.")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
