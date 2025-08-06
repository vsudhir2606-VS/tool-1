
# Desktop Auto Highlighter for SAP Applications

A powerful desktop application that can highlight keywords in any desktop application, including SAP GUI, SAP Fiori, or any other desktop software that displays text.

## 🌟 Features

- **Universal Desktop Highlighting**: Works with SAP GUI, SAP Fiori, and any desktop application
- **OCR-Based Text Recognition**: Uses Tesseract OCR to read text from screen
- **Real-time Monitoring**: Continuously scans selected areas or full screen
- **Customizable Keywords**: Add/remove keywords with ease
- **Multiple Highlight Colors**: Support for multiple colors to categorize keywords
- **Area Selection**: Monitor specific screen areas or full screen
- **Configuration Management**: Save/load/export configuration files
- **Transparency Control**: Adjustable highlight transparency
- **Case Sensitivity Options**: Toggle case-sensitive matching
- **Statistics Logging**: Track monitoring activity and matches

## 🚀 Installation

### Step 1: Install Python Dependencies

Run the installation script:
```bash
python install_desktop_highlighter.py
```

Or install manually:
```bash
pip install opencv-python pytesseract Pillow pyautogui numpy
```

### Step 2: Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Or use winget: `winget install UB-Mannheim.TesseractOCR`

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**CentOS/RHEL:**
```bash
sudo yum install tesseract
```

## 🎯 Usage

### Starting the Application

```bash
python desktop_highlighter.py
```

### Basic Setup

1. **Add Keywords**: Go to the "Keywords" tab and add words you want to highlight
2. **Configure Colors**: Click on color buttons to change highlight colors
3. **Adjust Settings**: Use the "Settings" tab to configure refresh rate, transparency, etc.
4. **Select Monitor Area**: Choose to monitor full screen or select a specific area
5. **Start Monitoring**: Click "Start Monitoring" to begin highlighting

### Working with SAP Applications

1. **Open your SAP application** (SAP GUI, SAP Fiori, etc.)
2. **Configure keywords** related to your SAP workflow:
   - Document numbers (e.g., "PO", "SO", "Invoice")
   - Status indicators (e.g., "Approved", "Pending", "Error")
   - User IDs, Customer codes, Material numbers
   - Error messages, Success messages
3. **Select monitor area** to focus on specific SAP screen areas
4. **Start monitoring** and watch as keywords get highlighted in real-time

### Example SAP Keywords

For SAP GUI monitoring, consider these keyword categories:

**Document Types:**
- Purchase Order
- Sales Order
- Invoice
- Delivery
- Material Document

**Status Keywords:**
- Approved
- Pending
- Blocked
- Error
- Success
- Warning

**Transaction Codes:**
- VA01, VA02, VA03
- ME21N, ME22N, ME23N
- VF01, VF02, VF03

## 🔧 Configuration

### Keyword Management
- Add keywords one by one using the input field
- Remove selected keywords from the list
- Clear all keywords with one click
- Keywords are automatically saved

### Color Configuration
- Click on color buttons to change highlight colors
- Add more colors using the "+" button
- Each keyword cycles through available colors

### Monitor Settings
- **Refresh Rate**: How often to scan the screen (0.5-10 seconds)
- **Transparency**: Highlight overlay transparency (0.1-1.0)
- **Case Sensitivity**: Toggle case-sensitive keyword matching

### Area Selection
- **Full Screen**: Monitor the entire screen
- **Custom Area**: Click and drag to select specific screen regions

## 💾 Configuration Files

### Saving Configuration
```json
{
  "keywords": ["Purchase Order", "Invoice", "Approved"],
  "highlight_colors": ["#ffff00", "#90EE90", "#FFB6C1"],
  "refresh_rate": 2.0,
  "transparency": 0.7,
  "case_sensitive": false,
  "monitor_area": [100, 100, 800, 600]
}
```

### Loading Configuration
- Use "Load Config" to import saved configurations
- Use "Export Config" to share configurations with team members

## 🎨 Use Cases

### SAP GUI Applications
- Highlight important document numbers
- Monitor transaction statuses
- Track error messages and warnings
- Identify approval requirements

### SAP Fiori Applications
- Highlight workflow items
- Monitor dashboard KPIs
- Track notification statuses
- Identify action items

### General Desktop Applications
- Monitor log files for errors
- Highlight important data in spreadsheets
- Track status updates in any application
- Monitor system messages

## 🔍 Troubleshooting

### Common Issues

**1. OCR Not Working**
- Ensure Tesseract OCR is installed correctly
- Check if tesseract is in system PATH
- Try adjusting screen DPI settings

**2. No Highlights Appearing**
- Verify keywords are added correctly
- Check if monitor area is selected properly
- Ensure transparency isn't set to 0
- Try increasing refresh rate

**3. Performance Issues**
- Reduce refresh rate (increase seconds)
- Select smaller monitor area
- Close unnecessary applications
- Use fewer keywords

**4. Permission Issues**
- Run as administrator on Windows
- Grant screen recording permissions on macOS
- Check display manager on Linux

### Optimization Tips

1. **Select Specific Areas**: Monitor only the relevant parts of SAP screens
2. **Use Appropriate Keywords**: Choose specific, unique keywords
3. **Adjust Refresh Rate**: Balance between responsiveness and performance
4. **Configure Colors**: Use contrasting colors for better visibility

## 🔒 Security & Privacy

- **Local Processing**: All OCR processing happens locally
- **No Network Access**: Application doesn't send data over network
- **Screen Access**: Only reads screen content, doesn't modify applications
- **Configuration Storage**: Settings stored locally in JSON files

## 📋 System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.7 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Display**: Any resolution supported
- **Tesseract OCR**: Latest version recommended

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs and issues
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

---

**Note**: This application is designed to work with any desktop application, including SAP systems. It reads text from the screen using OCR technology and does not interfere with the underlying applications.
