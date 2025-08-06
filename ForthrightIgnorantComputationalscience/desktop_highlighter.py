
#!/usr/bin/env python3
"""
Desktop Auto Highlighter for SAP Applications
A desktop application that can highlight keywords in any application window including SAP.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
import threading
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pytesseract
import re
from datetime import datetime

class DesktopHighlighter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Desktop Auto Highlighter - SAP & Desktop Apps")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration
        self.config_file = "highlighter_config.json"
        self.keywords = []
        self.highlight_colors = ['#ffff00', '#90EE90', '#FFB6C1', '#87CEEB', '#DDA0DD']
        self.is_monitoring = False
        self.monitor_thread = None
        self.overlay_windows = []
        
        # Load saved configuration
        self.load_config()
        
        # Setup GUI
        self.setup_gui()
        
        # Disable pyautogui failsafe
        pyautogui.FAILSAFE = True
        
    def setup_gui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="🔍 Desktop Auto Highlighter", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Highlight keywords in SAP and other desktop applications", 
                                 font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        subtitle_label.pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Keywords tab
        self.create_keywords_tab()
        
        # Settings tab
        self.create_settings_tab()
        
        # Monitor tab
        self.create_monitor_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Configure keywords and start monitoring")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W, bg='#ecf0f1')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_keywords_tab(self):
        keywords_frame = ttk.Frame(self.notebook)
        self.notebook.add(keywords_frame, text="Keywords")
        
        # Keywords section
        tk.Label(keywords_frame, text="Keywords to Highlight:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # Keywords listbox with scrollbar
        keywords_list_frame = tk.Frame(keywords_frame)
        keywords_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        keywords_scrollbar = tk.Scrollbar(keywords_list_frame)
        keywords_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.keywords_listbox = tk.Listbox(keywords_list_frame, yscrollcommand=keywords_scrollbar.set, height=8)
        self.keywords_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        keywords_scrollbar.config(command=self.keywords_listbox.yview)
        
        # Keyword entry and buttons
        keyword_entry_frame = tk.Frame(keywords_frame)
        keyword_entry_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(keyword_entry_frame, text="Add Keyword:").pack(side=tk.LEFT)
        self.keyword_entry = tk.Entry(keyword_entry_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        self.keyword_entry.bind('<Return>', lambda e: self.add_keyword())
        
        tk.Button(keyword_entry_frame, text="Add", command=self.add_keyword, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(keyword_entry_frame, text="Remove", command=self.remove_keyword, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(keyword_entry_frame, text="Clear All", command=self.clear_keywords, bg='#f39c12', fg='white').pack(side=tk.LEFT, padx=2)
        
        # Colors section
        colors_frame = tk.Frame(keywords_frame)
        colors_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(colors_frame, text="Highlight Colors:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        self.color_buttons_frame = tk.Frame(colors_frame)
        self.color_buttons_frame.pack(anchor='w', pady=5)
        
        self.update_color_buttons()
        
        # Configuration management
        config_frame = tk.Frame(keywords_frame)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(config_frame, text="Configuration:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        config_buttons_frame = tk.Frame(config_frame)
        config_buttons_frame.pack(anchor='w', pady=5)
        
        tk.Button(config_buttons_frame, text="Save Config", command=self.save_config, bg='#27ae60', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(config_buttons_frame, text="Load Config", command=self.load_config_dialog, bg='#8e44ad', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(config_buttons_frame, text="Export Config", command=self.export_config, bg='#16a085', fg='white').pack(side=tk.LEFT, padx=2)
        
        # Load keywords into listbox
        self.update_keywords_listbox()
        
    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Monitor settings
        monitor_settings_frame = tk.LabelFrame(settings_frame, text="Monitor Settings", font=('Arial', 11, 'bold'))
        monitor_settings_frame.pack(fill='x', padx=10, pady=10)
        
        # Refresh rate
        refresh_frame = tk.Frame(monitor_settings_frame)
        refresh_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(refresh_frame, text="Refresh Rate (seconds):").pack(side=tk.LEFT)
        self.refresh_rate_var = tk.DoubleVar(value=2.0)
        refresh_spinbox = tk.Spinbox(refresh_frame, from_=0.5, to=10.0, increment=0.5, 
                                   textvariable=self.refresh_rate_var, width=10)
        refresh_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Highlight transparency
        transparency_frame = tk.Frame(monitor_settings_frame)
        transparency_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(transparency_frame, text="Highlight Transparency:").pack(side=tk.LEFT)
        self.transparency_var = tk.DoubleVar(value=0.7)
        transparency_scale = tk.Scale(transparency_frame, from_=0.1, to=1.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, variable=self.transparency_var)
        transparency_scale.pack(side=tk.LEFT, padx=5)
        
        # Case sensitivity
        case_frame = tk.Frame(monitor_settings_frame)
        case_frame.pack(fill='x', padx=10, pady=5)
        
        self.case_sensitive_var = tk.BooleanVar(value=False)
        case_check = tk.Checkbutton(case_frame, text="Case Sensitive Matching", 
                                   variable=self.case_sensitive_var)
        case_check.pack(side=tk.LEFT)
        
        # OCR settings
        ocr_settings_frame = tk.LabelFrame(settings_frame, text="OCR Settings", font=('Arial', 11, 'bold'))
        ocr_settings_frame.pack(fill='x', padx=10, pady=10)
        
        ocr_info = tk.Label(ocr_settings_frame, 
                           text="Note: Tesseract OCR must be installed for text recognition to work.\n"
                                "Download from: https://github.com/tesseract-ocr/tesseract",
                           justify=tk.LEFT, wraplength=600)
        ocr_info.pack(padx=10, pady=5)
        
    def create_monitor_tab(self):
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="Monitor")
        
        # Instructions
        instructions_frame = tk.LabelFrame(monitor_frame, text="Instructions", font=('Arial', 11, 'bold'))
        instructions_frame.pack(fill='x', padx=10, pady=10)
        
        instructions_text = """
1. Configure your keywords in the Keywords tab
2. Adjust settings in the Settings tab if needed
3. Click 'Start Monitoring' to begin highlighting
4. The application will scan your screen for the keywords
5. Highlights will appear as colored overlays on detected text
6. Click 'Stop Monitoring' to end the process
        """
        
        tk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack(padx=10, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(monitor_frame)
        control_frame.pack(fill='x', padx=10, pady=20)
        
        self.start_button = tk.Button(control_frame, text="🚀 Start Monitoring", 
                                     command=self.start_monitoring, 
                                     bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                     height=2, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(control_frame, text="⏹️ Stop Monitoring", 
                                    command=self.stop_monitoring, 
                                    bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                                    height=2, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Monitor area selection
        area_frame = tk.LabelFrame(monitor_frame, text="Monitor Area", font=('Arial', 11, 'bold'))
        area_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(area_frame, text="📱 Select Screen Area", 
                 command=self.select_monitor_area, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(area_frame, text="🖥️ Monitor Full Screen", 
                 command=self.monitor_full_screen, bg='#9b59b6', fg='white').pack(side=tk.LEFT, padx=10, pady=5)
        
        self.area_info_var = tk.StringVar()
        self.area_info_var.set("Monitoring: Full Screen")
        tk.Label(area_frame, textvariable=self.area_info_var).pack(side=tk.LEFT, padx=10)
        
        # Statistics
        stats_frame = tk.LabelFrame(monitor_frame, text="Statistics", font=('Arial', 11, 'bold'))
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD)
        stats_scrollbar = tk.Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Monitor area coordinates
        self.monitor_area = None  # (x, y, width, height) or None for full screen
        
    def add_keyword(self):
        keyword = self.keyword_entry.get().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.update_keywords_listbox()
            self.keyword_entry.delete(0, tk.END)
            self.log_stats(f"Added keyword: {keyword}")
        elif keyword in self.keywords:
            messagebox.showwarning("Duplicate", "Keyword already exists!")
        else:
            messagebox.showwarning("Empty", "Please enter a keyword!")
            
    def remove_keyword(self):
        selection = self.keywords_listbox.curselection()
        if selection:
            index = selection[0]
            keyword = self.keywords[index]
            del self.keywords[index]
            self.update_keywords_listbox()
            self.log_stats(f"Removed keyword: {keyword}")
        else:
            messagebox.showwarning("No Selection", "Please select a keyword to remove!")
            
    def clear_keywords(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all keywords?"):
            self.keywords.clear()
            self.update_keywords_listbox()
            self.log_stats("Cleared all keywords")
            
    def update_keywords_listbox(self):
        self.keywords_listbox.delete(0, tk.END)
        for keyword in self.keywords:
            self.keywords_listbox.insert(tk.END, keyword)
            
    def update_color_buttons(self):
        # Clear existing buttons
        for widget in self.color_buttons_frame.winfo_children():
            widget.destroy()
            
        for i, color in enumerate(self.highlight_colors):
            color_button = tk.Button(self.color_buttons_frame, 
                                   width=4, height=2, bg=color,
                                   command=lambda idx=i: self.change_color(idx))
            color_button.pack(side=tk.LEFT, padx=2)
            
        # Add new color button
        add_color_button = tk.Button(self.color_buttons_frame, text="+", 
                                   width=4, height=2, bg='#bdc3c7',
                                   command=self.add_color)
        add_color_button.pack(side=tk.LEFT, padx=2)
        
    def change_color(self, index):
        color = colorchooser.askcolor(color=self.highlight_colors[index])[1]
        if color:
            self.highlight_colors[index] = color
            self.update_color_buttons()
            
    def add_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.highlight_colors.append(color)
            self.update_color_buttons()
            
    def save_config(self):
        config = {
            'keywords': self.keywords,
            'highlight_colors': self.highlight_colors,
            'refresh_rate': self.refresh_rate_var.get(),
            'transparency': self.transparency_var.get(),
            'case_sensitive': self.case_sensitive_var.get(),
            'monitor_area': self.monitor_area,
            'saved_date': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_stats("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            self.log_stats(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.keywords = config.get('keywords', [])
                self.highlight_colors = config.get('highlight_colors', ['#ffff00', '#90EE90', '#FFB6C1', '#87CEEB', '#DDA0DD'])
                
                if hasattr(self, 'refresh_rate_var'):
                    self.refresh_rate_var.set(config.get('refresh_rate', 2.0))
                    self.transparency_var.set(config.get('transparency', 0.7))
                    self.case_sensitive_var.set(config.get('case_sensitive', False))
                    
                self.monitor_area = config.get('monitor_area')
                
                if hasattr(self, 'keywords_listbox'):
                    self.update_keywords_listbox()
                    self.update_color_buttons()
                    
                self.log_stats("Configuration loaded successfully")
            except Exception as e:
                self.log_stats(f"Error loading configuration: {str(e)}")
                
    def load_config_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    
                self.keywords = config.get('keywords', [])
                self.highlight_colors = config.get('highlight_colors', ['#ffff00', '#90EE90', '#FFB6C1', '#87CEEB', '#DDA0DD'])
                self.refresh_rate_var.set(config.get('refresh_rate', 2.0))
                self.transparency_var.set(config.get('transparency', 0.7))
                self.case_sensitive_var.set(config.get('case_sensitive', False))
                self.monitor_area = config.get('monitor_area')
                
                self.update_keywords_listbox()
                self.update_color_buttons()
                
                self.log_stats(f"Configuration loaded from: {file_path}")
                messagebox.showinfo("Success", "Configuration loaded!")
            except Exception as e:
                self.log_stats(f"Error loading configuration: {str(e)}")
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
                
    def export_config(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            config = {
                'keywords': self.keywords,
                'highlight_colors': self.highlight_colors,
                'refresh_rate': self.refresh_rate_var.get(),
                'transparency': self.transparency_var.get(),
                'case_sensitive': self.case_sensitive_var.get(),
                'monitor_area': self.monitor_area,
                'exported_date': datetime.now().isoformat()
            }
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=2)
                self.log_stats(f"Configuration exported to: {file_path}")
                messagebox.showinfo("Success", "Configuration exported!")
            except Exception as e:
                self.log_stats(f"Error exporting configuration: {str(e)}")
                messagebox.showerror("Error", f"Failed to export configuration: {str(e)}")
                
    def select_monitor_area(self):
        messagebox.showinfo("Area Selection", 
                           "Click and drag to select the area to monitor.\n"
                           "Press ESC to cancel or ENTER to confirm.")
        
        # Hide main window temporarily
        self.root.withdraw()
        
        try:
            # Take screenshot for area selection
            screenshot = pyautogui.screenshot()
            
            # Create selection window
            selection_window = tk.Toplevel()
            selection_window.attributes('-fullscreen', True)
            selection_window.attributes('-alpha', 0.3)
            selection_window.configure(bg='black')
            
            canvas = tk.Canvas(selection_window, highlightthickness=0)
            canvas.pack(fill='both', expand=True)
            
            # Variables for selection
            start_x, start_y = 0, 0
            rect_id = None
            
            def on_click(event):
                nonlocal start_x, start_y, rect_id
                start_x, start_y = event.x, event.y
                if rect_id:
                    canvas.delete(rect_id)
                    
            def on_drag(event):
                nonlocal rect_id
                if rect_id:
                    canvas.delete(rect_id)
                rect_id = canvas.create_rectangle(start_x, start_y, event.x, event.y, 
                                                outline='red', width=2)
                                                
            def on_release(event):
                nonlocal start_x, start_y
                end_x, end_y = event.x, event.y
                
                # Calculate area
                x = min(start_x, end_x)
                y = min(start_y, end_y)
                width = abs(end_x - start_x)
                height = abs(end_y - start_y)
                
                if width > 10 and height > 10:  # Minimum area
                    self.monitor_area = (x, y, width, height)
                    self.area_info_var.set(f"Monitoring: Area ({x}, {y}) - {width}x{height}")
                    selection_window.destroy()
                    self.root.deiconify()
                    self.log_stats(f"Monitor area selected: {x}, {y}, {width}x{height}")
                else:
                    messagebox.showwarning("Invalid Selection", "Please select a larger area!")
                    
            def on_key(event):
                if event.keysym == 'Escape':
                    selection_window.destroy()
                    self.root.deiconify()
                    
            canvas.bind('<Button-1>', on_click)
            canvas.bind('<B1-Motion>', on_drag)
            canvas.bind('<ButtonRelease-1>', on_release)
            selection_window.bind('<Key>', on_key)
            selection_window.focus_set()
            
        except Exception as e:
            self.root.deiconify()
            self.log_stats(f"Error in area selection: {str(e)}")
            messagebox.showerror("Error", f"Failed to select area: {str(e)}")
            
    def monitor_full_screen(self):
        self.monitor_area = None
        self.area_info_var.set("Monitoring: Full Screen")
        self.log_stats("Set to monitor full screen")
        
    def start_monitoring(self):
        if not self.keywords:
            messagebox.showwarning("No Keywords", "Please add some keywords before starting!")
            return
            
        self.is_monitoring = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_var.set("Monitoring started...")
        
        # Start monitoring in separate thread
        self.monitor_thread = threading.Thread(target=self.monitor_screen, daemon=True)
        self.monitor_thread.start()
        
        self.log_stats("Monitoring started")
        
    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.status_var.set("Monitoring stopped")
        
        # Clear existing overlays
        self.clear_overlays()
        
        self.log_stats("Monitoring stopped")
        
    def monitor_screen(self):
        while self.is_monitoring:
            try:
                # Take screenshot
                if self.monitor_area:
                    x, y, width, height = self.monitor_area
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                else:
                    screenshot = pyautogui.screenshot()
                
                # Convert to cv2 format
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Perform OCR
                try:
                    text_data = pytesseract.image_to_data(screenshot_cv, output_type=pytesseract.Output.DICT)
                    self.process_ocr_results(text_data, screenshot)
                except Exception as ocr_error:
                    self.log_stats(f"OCR Error: {str(ocr_error)}")
                
                # Wait before next scan
                time.sleep(self.refresh_rate_var.get())
                
            except Exception as e:
                self.log_stats(f"Monitoring error: {str(e)}")
                time.sleep(1)
                
    def process_ocr_results(self, text_data, screenshot):
        # Clear existing overlays
        self.clear_overlays()
        
        matches_found = 0
        
        for i, word in enumerate(text_data['text']):
            if int(text_data['conf'][i]) > 30:  # Confidence threshold
                for j, keyword in enumerate(self.keywords):
                    # Check for match
                    if self.case_sensitive_var.get():
                        match = keyword in word
                    else:
                        match = keyword.lower() in word.lower()
                        
                    if match:
                        # Get word coordinates
                        x = text_data['left'][i]
                        y = text_data['top'][i]
                        w = text_data['width'][i]
                        h = text_data['height'][i]
                        
                        # Adjust coordinates if monitoring specific area
                        if self.monitor_area:
                            area_x, area_y, _, _ = self.monitor_area
                            x += area_x
                            y += area_y
                        
                        # Create highlight overlay
                        color = self.highlight_colors[j % len(self.highlight_colors)]
                        self.create_highlight_overlay(x, y, w, h, color)
                        matches_found += 1
                        
        if matches_found > 0:
            self.status_var.set(f"Found {matches_found} matches")
        else:
            self.status_var.set("No matches found")
            
    def create_highlight_overlay(self, x, y, width, height, color):
        # Create transparent overlay window
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', self.transparency_var.get())
        overlay.configure(bg=color)
        
        # Position overlay
        overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Store overlay reference
        self.overlay_windows.append(overlay)
        
        # Auto-remove overlay after a short time
        self.root.after(int(self.refresh_rate_var.get() * 1000), lambda: self.remove_overlay(overlay))
        
    def remove_overlay(self, overlay):
        try:
            if overlay in self.overlay_windows:
                self.overlay_windows.remove(overlay)
            overlay.destroy()
        except:
            pass
            
    def clear_overlays(self):
        for overlay in self.overlay_windows[:]:
            try:
                overlay.destroy()
                self.overlay_windows.remove(overlay)
            except:
                pass
                
    def log_stats(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            self.stats_text.insert(tk.END, log_entry)
            self.stats_text.see(tk.END)
        except:
            pass
            
    def run(self):
        # Load configuration on startup
        self.load_config()
        
        # Handle window closing
        def on_closing():
            self.stop_monitoring()
            self.clear_overlays()
            self.root.destroy()
            
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        self.root.mainloop()

def main():
    """Main function to run the desktop highlighter"""
    print("🔍 Desktop Auto Highlighter - Starting...")
    
    # Check dependencies
    try:
        import pytesseract
        import cv2
        import pyautogui
        from PIL import Image, ImageTk
        print("✅ All dependencies are available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install pytesseract opencv-python pyautogui pillow")
        print("\nAlso install Tesseract OCR:")
        print("https://github.com/tesseract-ocr/tesseract")
        return
    
    # Start the application
    app = DesktopHighlighter()
    app.run()

if __name__ == "__main__":
    main()
