import wx
import os
import csv
import json
from datetime import datetime

from gui.menu import AboutDialog
try:
    from barcode import Code128, Code39, EAN13, EAN8, UPCA, ITF, CODABAR
    from barcode.writer import ImageWriter, SVGWriter
    import barcode
except ImportError:
    print("Please install python-barcode: pip install python-barcode")
    exit(1)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from PIL import Image
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False
    print("For PDF support, install: pip install reportlab pillow")

class BarcodeGeneratorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Professional Barcode Generator", size=(900, 700))
        
        # Available barcode types
        self.barcode_types = {
            'Code128': Code128,
            'Code39': Code39,
            'EAN13': EAN13,
            'EAN8': EAN8,
            'UPC-A': UPCA,
            'ITF': ITF,
            'CODABAR': CODABAR
        }
        
        # Settings
        self.settings = {
            'default_barcode_type': 'Code128',
            'default_output_format': 'PNG',
            'default_output_dir': os.path.expanduser('~/Downloads'),
            'barcode_width': 2.0,
            'barcode_height': 15.0,
            'include_text': True,
            'text_distance': 5,
            'font_size': 10
        }
        
        self.load_settings()
        self.init_ui()
        self.Center()
        self.Show()
        self.Layout()
        self.Refresh()
        
    def load_settings(self):
        """Load settings from file"""
        settings_file = 'barcode_generator_settings.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
            except:
                pass
                
    def save_settings(self):
        """Save settings to file"""
        try:
            with open('barcode_generator_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
            
    def init_ui(self):
        """Initialize the user interface"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create notebook for tabs
        notebook = wx.Notebook(panel)
        
        # Single Barcode Tab
        single_panel = wx.Panel(notebook)
        self.create_single_barcode_tab(single_panel)
        notebook.AddPage(single_panel, "Single Barcode")
        
        # Batch Processing Tab
        batch_panel = wx.Panel(notebook)
        self.create_batch_processing_tab(batch_panel)
        notebook.AddPage(batch_panel, "Batch Processing")
        
        # Settings Tab
        settings_panel = wx.Panel(notebook)
        self.create_settings_tab(settings_panel)
        notebook.AddPage(settings_panel, "Settings")
        
        main_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")
        
        # Menu bar
        self.create_menu_bar()
        
        panel.SetSizer(main_sizer)
        panel.Layout()
        panel.Refresh()
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit application")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        
        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        
    def create_single_barcode_tab(self, panel):
        """Create single barcode generation tab"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input section
        input_box = wx.StaticBox(panel, label="Barcode Input")
        input_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)
        
        # Text input
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_sizer.Add(wx.StaticText(panel, label="Text:"), 0, wx.CENTER | wx.ALL, 5)
        self.text_ctrl = wx.TextCtrl(panel, size=(300, -1))
        text_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(text_sizer, 0, wx.EXPAND)
        
        # Barcode type selection
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(wx.StaticText(panel, label="Barcode Type:"), 0, wx.CENTER | wx.ALL, 5)
        self.barcode_choice = wx.Choice(panel, choices=list(self.barcode_types.keys()))
        self.barcode_choice.SetSelection(0)
        type_sizer.Add(self.barcode_choice, 0, wx.ALL, 5)
        input_sizer.Add(type_sizer, 0, wx.EXPAND)
        
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Output section
        output_box = wx.StaticBox(panel, label="Output Options")
        output_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)
        
        # Output format
        format_sizer = wx.BoxSizer(wx.HORIZONTAL)
        format_sizer.Add(wx.StaticText(panel, label="Format:"), 0, wx.CENTER | wx.ALL, 5)
        formats = ['PNG', 'SVG']
        if HAS_PDF_SUPPORT:
            formats.append('PDF')
        self.format_choice = wx.Choice(panel, choices=formats)
        self.format_choice.SetSelection(0)
        format_sizer.Add(self.format_choice, 0, wx.ALL, 5)
        output_sizer.Add(format_sizer, 0, wx.EXPAND)
        
        # Output directory
        dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dir_sizer.Add(wx.StaticText(panel, label="Output Directory:"), 0, wx.CENTER | wx.ALL, 5)
        self.dir_picker = wx.DirPickerCtrl(panel, path=self.settings['default_output_dir'])
        dir_sizer.Add(self.dir_picker, 1, wx.EXPAND | wx.ALL, 5)
        output_sizer.Add(dir_sizer, 0, wx.EXPAND)
        
        sizer.Add(output_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Preview section
        preview_box = wx.StaticBox(panel, label="Preview")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)
        
        self.preview_panel = wx.Panel(panel, size=(400, 150))
        self.preview_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        preview_sizer.Add(self.preview_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.preview_btn = wx.Button(panel, label="Preview")
        self.generate_btn = wx.Button(panel, label="Generate & Save")
        button_sizer.Add(self.preview_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.generate_btn, 0, wx.ALL, 5)
        preview_sizer.Add(button_sizer, 0, wx.CENTER)
        
        sizer.Add(preview_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Bind events
        self.preview_btn.Bind(wx.EVT_BUTTON, self.on_preview)
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate_single)
        
        panel.SetSizer(sizer)
        
    def create_batch_processing_tab(self, panel):
        """Create batch processing tab"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input source selection
        source_box = wx.StaticBox(panel, label="Input Source")
        source_sizer = wx.StaticBoxSizer(source_box, wx.VERTICAL)
        
        self.source_radio = wx.RadioBox(panel, label="Select Input Type", 
                                       choices=["Text File (.txt)", "CSV File (.csv)"])
        source_sizer.Add(self.source_radio, 0, wx.EXPAND | wx.ALL, 5)
        
        # File picker
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_sizer.Add(wx.StaticText(panel, label="File:"), 0, wx.CENTER | wx.ALL, 5)
        self.file_picker = wx.FilePickerCtrl(panel, wildcard="Text files (*.txt)|*.txt|CSV files (*.csv)|*.csv")
        file_sizer.Add(self.file_picker, 1, wx.EXPAND | wx.ALL, 5)
        source_sizer.Add(file_sizer, 0, wx.EXPAND)
        
        # CSV column selection (only for CSV)
        csv_sizer = wx.BoxSizer(wx.HORIZONTAL)
        csv_sizer.Add(wx.StaticText(panel, label="CSV Column:"), 0, wx.CENTER | wx.ALL, 5)
        self.csv_column_choice = wx.Choice(panel)
        self.csv_column_choice.Enable(False)
        csv_sizer.Add(self.csv_column_choice, 0, wx.ALL, 5)
        self.analyze_csv_btn = wx.Button(panel, label="Analyze CSV")
        self.analyze_csv_btn.Enable(False)
        csv_sizer.Add(self.analyze_csv_btn, 0, wx.ALL, 5)
        source_sizer.Add(csv_sizer, 0, wx.EXPAND)
        
        sizer.Add(source_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Batch options
        batch_box = wx.StaticBox(panel, label="Batch Options")
        batch_sizer = wx.StaticBoxSizer(batch_box, wx.VERTICAL)
        
        # Barcode type for batch
        batch_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        batch_type_sizer.Add(wx.StaticText(panel, label="Barcode Type:"), 0, wx.CENTER | wx.ALL, 5)
        self.batch_barcode_choice = wx.Choice(panel, choices=list(self.barcode_types.keys()))
        self.batch_barcode_choice.SetSelection(0)
        batch_type_sizer.Add(self.batch_barcode_choice, 0, wx.ALL, 5)
        batch_sizer.Add(batch_type_sizer, 0, wx.EXPAND)
        
        # Output format for batch
        batch_format_sizer = wx.BoxSizer(wx.HORIZONTAL)
        batch_format_sizer.Add(wx.StaticText(panel, label="Format:"), 0, wx.CENTER | wx.ALL, 5)
        formats = ['PNG', 'SVG']
        if HAS_PDF_SUPPORT:
            formats.extend(['PDF (Individual)', 'PDF (Combined)'])
        self.batch_format_choice = wx.Choice(panel, choices=formats)
        self.batch_format_choice.SetSelection(0)
        batch_format_sizer.Add(self.batch_format_choice, 0, wx.ALL, 5)
        batch_sizer.Add(batch_format_sizer, 0, wx.EXPAND)
        
        # Output directory for batch
        batch_dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        batch_dir_sizer.Add(wx.StaticText(panel, label="Output Directory:"), 0, wx.CENTER | wx.ALL, 5)
        self.batch_dir_picker = wx.DirPickerCtrl(panel, path=self.settings['default_output_dir'])
        batch_dir_sizer.Add(self.batch_dir_picker, 1, wx.EXPAND | wx.ALL, 5)
        batch_sizer.Add(batch_dir_sizer, 0, wx.EXPAND)
        
        # Filename prefix
        prefix_sizer = wx.BoxSizer(wx.HORIZONTAL)
        prefix_sizer.Add(wx.StaticText(panel, label="Filename Prefix:"), 0, wx.CENTER | wx.ALL, 5)
        self.prefix_ctrl = wx.TextCtrl(panel, value="barcode_")
        prefix_sizer.Add(self.prefix_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        batch_sizer.Add(prefix_sizer, 0, wx.EXPAND)
        
        sizer.Add(batch_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Progress section
        progress_box = wx.StaticBox(panel, label="Progress")
        progress_sizer = wx.StaticBoxSizer(progress_box, wx.VERTICAL)
        
        self.progress_gauge = wx.Gauge(panel, range=100)
        progress_sizer.Add(self.progress_gauge, 0, wx.EXPAND | wx.ALL, 5)
        
        self.progress_text = wx.StaticText(panel, label="Ready")
        progress_sizer.Add(self.progress_text, 0, wx.ALL, 5)
        
        # Batch generate button
        self.batch_generate_btn = wx.Button(panel, label="Generate Batch")
        progress_sizer.Add(self.batch_generate_btn, 0, wx.CENTER | wx.ALL, 5)
        
        sizer.Add(progress_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Bind events
        self.source_radio.Bind(wx.EVT_RADIOBOX, self.on_source_change)
        self.analyze_csv_btn.Bind(wx.EVT_BUTTON, self.on_analyze_csv)
        self.batch_generate_btn.Bind(wx.EVT_BUTTON, self.on_generate_batch)
        
        panel.SetSizer(sizer)
        
    def create_settings_tab(self, panel):
        """Create settings tab"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Barcode appearance settings
        appearance_box = wx.StaticBox(panel, label="Barcode Appearance")
        appearance_sizer = wx.StaticBoxSizer(appearance_box, wx.VERTICAL)
        
        # Width setting
        width_sizer = wx.BoxSizer(wx.HORIZONTAL)
        width_sizer.Add(wx.StaticText(panel, label="Width:"), 0, wx.CENTER | wx.ALL, 5)
        self.width_spin = wx.SpinCtrlDouble(panel, value=str(self.settings['barcode_width']), 
                                          min=0.5, max=10.0, inc=0.1)
        width_sizer.Add(self.width_spin, 0, wx.ALL, 5)
        width_sizer.Add(wx.StaticText(panel, label="mm"), 0, wx.CENTER | wx.ALL, 5)
        appearance_sizer.Add(width_sizer, 0, wx.EXPAND)
        
        # Height setting
        height_sizer = wx.BoxSizer(wx.HORIZONTAL)
        height_sizer.Add(wx.StaticText(panel, label="Height:"), 0, wx.CENTER | wx.ALL, 5)
        self.height_spin = wx.SpinCtrlDouble(panel, value=str(self.settings['barcode_height']), 
                                           min=5.0, max=50.0, inc=1.0)
        height_sizer.Add(self.height_spin, 0, wx.ALL, 5)
        height_sizer.Add(wx.StaticText(panel, label="mm"), 0, wx.CENTER | wx.ALL, 5)
        appearance_sizer.Add(height_sizer, 0, wx.EXPAND)
        
        # Text inclusion
        self.include_text_cb = wx.CheckBox(panel, label="Include text below barcode")
        self.include_text_cb.SetValue(self.settings['include_text'])
        appearance_sizer.Add(self.include_text_cb, 0, wx.ALL, 5)

        # Font size
        text_distance_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_distance_sizer.Add(wx.StaticText(panel, label="Text Distance:"), 0, wx.CENTER | wx.ALL, 5)
        self.text_distance_spin = wx.SpinCtrl(panel, value=str(self.settings['text_distance']), 
                                   min=6, max=24)
        text_distance_sizer.Add(self.text_distance_spin, 0, wx.ALL, 5)
        text_distance_sizer.Add(wx.StaticText(panel, label="mm"), 0, wx.CENTER | wx.ALL, 5)
        appearance_sizer.Add(text_distance_sizer, 0, wx.EXPAND)
        
        # Font size
        font_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_sizer.Add(wx.StaticText(panel, label="Font Size:"), 0, wx.CENTER | wx.ALL, 5)
        self.font_spin = wx.SpinCtrl(panel, value=str(self.settings['font_size']), 
                                   min=6, max=24)
        font_sizer.Add(self.font_spin, 0, wx.ALL, 5)
        font_sizer.Add(wx.StaticText(panel, label="pt"), 0, wx.CENTER | wx.ALL, 5)
        appearance_sizer.Add(font_sizer, 0, wx.EXPAND)
        
        sizer.Add(appearance_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Default settings
        defaults_box = wx.StaticBox(panel, label="Defaults")
        defaults_sizer = wx.StaticBoxSizer(defaults_box, wx.VERTICAL)
        
        # Default barcode type
        default_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        default_type_sizer.Add(wx.StaticText(panel, label="Default Barcode Type:"), 0, wx.CENTER | wx.ALL, 5)
        self.default_type_choice = wx.Choice(panel, choices=list(self.barcode_types.keys()))
        current_selection = list(self.barcode_types.keys()).index(self.settings['default_barcode_type'])
        self.default_type_choice.SetSelection(current_selection)
        default_type_sizer.Add(self.default_type_choice, 0, wx.ALL, 5)
        defaults_sizer.Add(default_type_sizer, 0, wx.EXPAND)
        
        # Default output format
        default_format_sizer = wx.BoxSizer(wx.HORIZONTAL)
        default_format_sizer.Add(wx.StaticText(panel, label="Default Output Format:"), 0, wx.CENTER | wx.ALL, 5)
        formats = ['PNG', 'SVG']
        if HAS_PDF_SUPPORT:
            formats.append('PDF')
        self.default_format_choice = wx.Choice(panel, choices=formats)
        try:
            format_selection = formats.index(self.settings['default_output_format'])
            self.default_format_choice.SetSelection(format_selection)
        except ValueError:
            self.default_format_choice.SetSelection(0)
        default_format_sizer.Add(self.default_format_choice, 0, wx.ALL, 5)
        defaults_sizer.Add(default_format_sizer, 0, wx.EXPAND)
        
        sizer.Add(defaults_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_settings_btn = wx.Button(panel, label="Save Settings")
        reset_settings_btn = wx.Button(panel, label="Reset to Defaults")
        button_sizer.Add(save_settings_btn, 0, wx.ALL, 5)
        button_sizer.Add(reset_settings_btn, 0, wx.ALL, 5)
        
        sizer.Add(button_sizer, 0, wx.CENTER | wx.ALL, 10)
        
        # Bind events
        save_settings_btn.Bind(wx.EVT_BUTTON, self.on_save_settings)
        reset_settings_btn.Bind(wx.EVT_BUTTON, self.on_reset_settings)
        
        panel.SetSizer(sizer)
        
    def on_source_change(self, event):
        """Handle input source change"""
        selection = self.source_radio.GetSelection()
        if selection == 1:  # CSV
            self.csv_column_choice.Enable(True)
            self.analyze_csv_btn.Enable(True)
        else:  # Text file
            self.csv_column_choice.Enable(False)
            self.analyze_csv_btn.Enable(False)
            
    def on_analyze_csv(self, event):
        """Analyze CSV file to get column names"""
        file_path = self.file_picker.GetPath()
        if not file_path or not file_path.endswith('.csv'):
            wx.MessageBox("Please select a CSV file first.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                
            self.csv_column_choice.Clear()
            self.csv_column_choice.AppendItems(headers)
            if headers:
                self.csv_column_choice.SetSelection(0)
                
            wx.MessageBox(f"Found {len(headers)} columns in CSV file.", "Success", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"Error reading CSV file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            
    def on_preview(self, event):
        """Preview barcode"""
        text = self.text_ctrl.GetValue().strip()
        if not text:
            wx.MessageBox("Please enter text for the barcode.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            barcode_type = self.barcode_choice.GetStringSelection()
            barcode_class = self.barcode_types[barcode_type]
            
            # Generate barcode
            code = barcode_class(text, writer=ImageWriter())
            
            # Create temporary preview
            temp_path = "temp_preview"
            options = {
                'module_width': self.settings['barcode_width'],
                'module_height': self.settings['barcode_height'],
                'font_size': self.settings['font_size'],
                'text_distance': 20.0,
                'quiet_zone': 6.5
            }
            
            if not self.settings['include_text']:
                options['write_text'] = False
                
            full_path = code.save(temp_path, options=options)
            
            # Display preview
            self.show_preview(full_path)
            
            # Clean up
            if os.path.exists(full_path):
                os.remove(full_path)
                
        except Exception as e:
            wx.MessageBox(f"Error generating preview: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            
    def show_preview(self, image_path):
        """Display barcode preview"""
        try:
            # Load and display image
            image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            
            # Scale image to fit preview panel
            panel_size = self.preview_panel.GetSize()
            image_size = image.GetSize()
            
            # Calculate scaling factor
            scale_x = panel_size[0] / image_size[0]
            scale_y = panel_size[1] / image_size[1]
            scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            if scale < 1.0:
                new_width = int(image_size[0] * scale)
                new_height = int(image_size[1] * scale)
                image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
            
            bitmap = wx.Bitmap(image)
            
            # Create static bitmap to display
            for child in self.preview_panel.GetChildren():
                child.Destroy()
                
            sizer = wx.BoxSizer(wx.VERTICAL)
            static_bitmap = wx.StaticBitmap(self.preview_panel, bitmap=bitmap)
            sizer.Add(static_bitmap, 0, wx.CENTER)
            self.preview_panel.SetSizer(sizer)
            self.preview_panel.Layout()
            
        except Exception as e:
            wx.MessageBox(f"Error displaying preview: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            
    def on_generate_single(self, event):
        """Generate single barcode"""
        text = self.text_ctrl.GetValue().strip()
        if not text:
            wx.MessageBox("Please enter text for the barcode.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            barcode_type = self.barcode_choice.GetStringSelection()
            output_format = self.format_choice.GetStringSelection()
            output_dir = self.dir_picker.GetPath()
            
            success = self.generate_barcode(text, barcode_type, output_format, output_dir)
            
            if success:
                self.status_bar.SetStatusText("Barcode generated successfully!")
                wx.MessageBox(f"Barcode saved to {output_dir}", "Success", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"Error generating barcode: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            
    def generate_barcode(self, text, barcode_type, output_format, output_dir, filename=None):
        """Generate a single barcode"""
        try:
            barcode_class = self.barcode_types[barcode_type]
            
            if filename is None:
                # Create safe filename
                safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).rstrip()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"barcode_{safe_text}_{timestamp}"
            
            options = {
                'module_width': self.settings['barcode_width'],
                'module_height': self.settings['barcode_height'],
                'font_size': self.settings['font_size'],
                'text_distance': 100.0,
                'quiet_zone': 16.5
            }
            
            if not self.settings['include_text']:
                options['write_text'] = False
            
            if output_format == 'SVG':
                code = barcode_class(text, writer=SVGWriter())
                extension = '.svg'
            elif output_format == 'PDF' and HAS_PDF_SUPPORT:
                return self.generate_pdf_barcode(text, barcode_type, output_dir, filename)
            else:  # PNG
                code = barcode_class(text, writer=ImageWriter())
                extension = '.png'
            
            output_path = os.path.join(output_dir, filename + extension)
            code.save(output_path, options=options)
            
            return True
            
        except Exception as e:
            raise e
            
    def generate_pdf_barcode(self, text, barcode_type, output_dir, filename):
        """Generate PDF barcode"""
        if not HAS_PDF_SUPPORT:
            raise Exception("PDF support not available. Please install reportlab and pillow.")
            
        try:
            # Generate barcode as image first
            barcode_class = self.barcode_types[barcode_type]
            code = barcode_class(text, writer=ImageWriter())
            
            options = {
                'module_width': self.settings['barcode_width'],
                'module_height': self.settings['barcode_height'],
                'font_size': self.settings['font_size'],
                'text_distance': 5.0,
                'quiet_zone': 6.5
            }
            
            if not self.settings['include_text']:
                options['write_text'] = False
            
            # Save temporary image
            temp_path = code.save("temp_barcode", options=options)
            
            # Create PDF
            pdf_path = os.path.join(output_dir, filename + '.pdf')
            c = canvas.Canvas(pdf_path, pagesize=letter)
            
            # Add barcode image to PDF
            c.drawImage(temp_path, 72, 600, width=300, height=100)  # 1 inch margins
            c.save()
            
            # Clean up temporary image
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return True
            
        except Exception as e:
            raise e
            
    def on_generate_batch(self, event):
        """Generate batch barcodes"""
        file_path = self.file_picker.GetPath()
        if not file_path:
            wx.MessageBox("Please select an input file.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            # Read input data
            if self.source_radio.GetSelection() == 0:  # Text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = [line.strip() for line in f.readlines() if line.strip()]
            else:  # CSV file
                column_index = self.csv_column_choice.GetSelection()
                if column_index == -1:
                    wx.MessageBox("Please select a CSV column.", "Error", wx.OK | wx.ICON_ERROR)
                    return
                    
                data = []
                with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)  # Skip header
                    for row in reader:
                        if len(row) > column_index and row[column_index].strip():
                            data.append(row[column_index].strip())
            
            if not data:
                wx.MessageBox("No data found in the input file.", "Error", wx.OK | wx.ICON_ERROR)
                return
            
            # Get batch settings
            barcode_type = self.batch_barcode_choice.GetStringSelection()
            output_format = self.batch_format_choice.GetStringSelection()
            output_dir = self.batch_dir_picker.GetPath()
            prefix = self.prefix_ctrl.GetValue()
            
            # Initialize progress
            self.progress_gauge.SetRange(len(data))
            self.progress_gauge.SetValue(0)
            
            # Generate barcodes
            successful = 0
            failed_items = []
            
            if output_format == 'PDF (Combined)' and HAS_PDF_SUPPORT:
                # Generate combined PDF
                success = self.generate_combined_pdf(data, barcode_type, output_dir, prefix)
                if success:
                    successful = len(data)
            else:
                # Generate individual files
                for i, text in enumerate(data):
                    try:
                        filename = f"{prefix}{i+1:04d}_{text[:20]}"  # Limit filename length
                        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        
                        if output_format == 'PDF (Individual)':
                            format_to_use = 'PDF'
                        else:
                            format_to_use = output_format
                            
                        success = self.generate_barcode(text, barcode_type, format_to_use, output_dir, filename)
                        if success:
                            successful += 1
                        else:
                            failed_items.append(text)
                            
                    except Exception as e:
                        failed_items.append(f"{text} (Error: {str(e)})")
                        
                    # Update progress
                    self.progress_gauge.SetValue(i + 1)
                    self.progress_text.SetLabel(f"Processing: {i+1}/{len(data)}")
                    wx.GetApp().Yield()
            
            # Show results
            self.progress_text.SetLabel(f"Completed: {successful} successful, {len(failed_items)} failed")
            
            if failed_items:
                failed_msg = f"Successfully generated {successful} barcodes.\n\nFailed items:\n" + "\n".join(failed_items[:10])
                if len(failed_items) > 10:
                    failed_msg += f"\n... and {len(failed_items) - 10} more"
                wx.MessageBox(failed_msg, "Batch Generation Complete", wx.OK | wx.ICON_WARNING)
            else:
                wx.MessageBox(f"Successfully generated all {successful} barcodes!", "Success", wx.OK | wx.ICON_INFORMATION)
                
        except Exception as e:
            wx.MessageBox(f"Error processing batch: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            
    def generate_combined_pdf(self, data, barcode_type, output_dir, prefix):
        """Generate combined PDF with all barcodes"""
        if not HAS_PDF_SUPPORT:
            return False
            
        try:
            pdf_path = os.path.join(output_dir, f"{prefix}combined_barcodes.pdf")
            c = canvas.Canvas(pdf_path, pagesize=A4)
            
            barcode_class = self.barcode_types[barcode_type]
            
            options = {
                'module_width': self.settings['barcode_width'],
                'module_height': self.settings['barcode_height'],
                'font_size': self.settings['font_size'],
                'text_distance': 5.0,
                'quiet_zone': 6.5
            }
            
            if not self.settings['include_text']:
                options['write_text'] = False
            
            # Calculate layout
            page_width, page_height = A4
            margin = 72  # 1 inch
            usable_width = page_width - 2 * margin
            usable_height = page_height - 2 * margin
            
            barcode_height = 80
            barcode_width = 250
            spacing = 20
            
            barcodes_per_row = max(1, int(usable_width / (barcode_width + spacing)))
            barcodes_per_column = max(1, int(usable_height / (barcode_height + spacing)))
            barcodes_per_page = barcodes_per_row * barcodes_per_column
            
            current_page_count = 0
            
            for i, text in enumerate(data):
                try:
                    # Generate barcode image
                    code = barcode_class(text, writer=ImageWriter())
                    temp_path = code.save(f"temp_barcode_{i}", options=options)
                    
                    # Calculate position
                    page_position = i % barcodes_per_page
                    row = page_position // barcodes_per_row
                    col = page_position % barcodes_per_row
                    
                    x = margin + col * (barcode_width + spacing)
                    y = page_height - margin - (row + 1) * (barcode_height + spacing)
                    
                    # Add to PDF
                    c.drawImage(temp_path, x, y, width=barcode_width, height=barcode_height)
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    # Start new page if needed
                    if (i + 1) % barcodes_per_page == 0 and i < len(data) - 1:
                        c.showPage()
                        
                    # Update progress
                    if hasattr(self, 'progress_gauge'):
                        self.progress_gauge.SetValue(i + 1)
                        self.progress_text.SetLabel(f"Adding to PDF: {i+1}/{len(data)}")
                        wx.GetApp().Yield()
                        
                except Exception as e:
                    print(f"Error processing item {text}: {e}")
                    continue
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Error creating combined PDF: {e}")
            return False
    
    def on_save_settings(self, event):
        """Save current settings"""
        self.settings['barcode_width'] = self.width_spin.GetValue()
        self.settings['barcode_height'] = self.height_spin.GetValue()
        self.settings['include_text'] = self.include_text_cb.GetValue()
        self.settings['text_distance'] = self.text_distance_spin.GetValue()
        self.settings['font_size'] = self.font_spin.GetValue()
        self.settings['default_barcode_type'] = self.default_type_choice.GetStringSelection()
        self.settings['default_output_format'] = self.default_format_choice.GetStringSelection()
        
        self.save_settings()
        wx.MessageBox("Settings saved successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        
    def on_reset_settings(self, event):
        """Reset settings to defaults"""
        self.settings = {
            'default_barcode_type': 'Code128',
            'default_output_format': 'PNG',
            'default_output_dir': os.path.expanduser('~/Downloads'),
            'barcode_width': 1.0,
            'barcode_height': 50.0,
            'include_text': True,
            'font_size': 24
        }
        
        # Update UI controls
        self.width_spin.SetValue(self.settings['barcode_width'])
        self.height_spin.SetValue(self.settings['barcode_height'])
        self.include_text_cb.SetValue(self.settings['include_text'])
        self.font_spin.SetValue(self.settings['font_size'])
        
        current_selection = list(self.barcode_types.keys()).index(self.settings['default_barcode_type'])
        self.default_type_choice.SetSelection(current_selection)
        
        formats = ['PNG', 'SVG']
        if HAS_PDF_SUPPORT:
            formats.append('PDF')
        format_selection = formats.index(self.settings['default_output_format'])
        self.default_format_choice.SetSelection(format_selection)
        
        wx.MessageBox("Settings reset to defaults!", "Success", wx.OK | wx.ICON_INFORMATION)
        
    def on_exit(self, event):
        """Handle exit menu"""
        self.save_settings()
        self.Close()
        
    def on_about(self, event):
        dialog = AboutDialog(self)
        dialog.ShowModal()  # Makes the dialog modal → stays in front, blocks main window
        dialog.Destroy()

class BarcodeGeneratorApp(wx.App):
    def OnInit(self):
        frame = BarcodeGeneratorFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    # Check dependencies
    missing_deps = []
    
    try:
        import barcode
    except ImportError:
        missing_deps.append("python-barcode")
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  pip install {dep}")
        print("\nOptional dependencies for full functionality:")
        print("  pip install reportlab pillow  # For PDF support")
        exit(1)
    
    app = BarcodeGeneratorApp()
    app.MainLoop()