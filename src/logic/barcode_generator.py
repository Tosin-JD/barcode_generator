import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter, SVGWriter

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False


class BarcodeGenerator:
    def __init__(self, settings=None):
        # Default settings if none provided
        self.settings = settings or {
            'barcode_width': 0.2,
            'barcode_height': 15.0,
            'text_distance': 5.0,
            'font_size': 10,
            'include_text': True
        }
        self.barcode_types = {
            'EAN13': barcode.get_barcode_class('ean13'),
            'EAN8': barcode.get_barcode_class('ean8'),
            'Code128': barcode.get_barcode_class('code128'),
            'Code39': barcode.get_barcode_class('code39'),
            'UPC': barcode.get_barcode_class('upc'),
            'ISBN13': barcode.get_barcode_class('isbn13'),
        }

    def generate_barcode(self, text, barcode_type, output_format, output_dir, filename=None):
        """Generate a single barcode in PNG, SVG, or PDF format."""
        try:
            barcode_class = self.barcode_types[barcode_type]

            if filename is None:
                safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).rstrip()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"barcode_{safe_text}_{timestamp}"

            options = {
                'module_width': self.settings['barcode_width'],
                'module_height': self.settings['barcode_height'],
                'font_size': self.settings['font_size'],
                'text_distance': 5.0,
                'quiet_zone': 6.5
            }

            if not self.settings['include_text']:
                options['write_text'] = False

            if output_format.upper() == 'SVG':
                code = barcode_class(text, writer=SVGWriter())
                extension = '.svg'
                output_path = os.path.join(output_dir, filename + extension)
                code.save(output_path, options=options)
                return output_path

            elif output_format.upper() == 'PDF':
                if not HAS_PDF_SUPPORT:
                    raise Exception("PDF support not available. Install reportlab and pillow.")
                return self.generate_pdf_barcode(barcode_class, text, output_dir, filename, options)

            else:  # Default to PNG
                code = barcode_class(text, writer=ImageWriter())
                extension = '.png'
                output_path = os.path.join(output_dir, filename + extension)
                code.save(output_path, options=options)
                return output_path

        except Exception as e:
            raise e

    def generate_pdf_barcode(self, barcode_class, text, output_dir, filename, options):
        """Generate a barcode embedded in a PDF."""
        try:
            # Generate barcode image temporarily
            temp_path = code = barcode_class(text, writer=ImageWriter()).save("temp_barcode", options=options)

            # Create PDF
            pdf_path = os.path.join(output_dir, filename + '.pdf')
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawImage(temp_path, 72, 600, width=300, height=100)
            c.save()

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return pdf_path

        except Exception as e:
            raise e
