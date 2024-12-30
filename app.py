import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

def load_default_font(size):
    """Load a default font that's likely to be available on most systems"""
    try:
        # Try different system fonts in order of preference
        font_options = [
            "DejaVuSans.ttf",
            "Arial.ttf",
            "Helvetica.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux path
            "/System/Library/Fonts/Helvetica.ttc",  # MacOS path
            "C:\\Windows\\Fonts\\arial.ttf"  # Windows path
        ]
        
        for font_path in font_options:
            try:
                return ImageFont.truetype(font_path, size=size)
            except OSError:
                continue
                
        # If no system fonts work, use PIL's default font
        return ImageFont.load_default()
    except Exception as e:
        st.warning(f"Using basic font due to: {str(e)}")
        return ImageFont.load_default()

def get_centered_position(text, font, y_position, image_width):
    """Calculate the centered position for text"""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    return ((image_width - text_width) // 2, y_position)

# Set page config
st.set_page_config(page_title="Birthday Card Generator", layout="wide")

# Add custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .upload-text {
        font-size: 18px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Main title with styling
st.title("🎂 Birthday Card Generator")

# Create two columns for uploads
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="upload-text">1. Upload Excel File</p>', unsafe_allow_html=True)
    excel_file = st.file_uploader(
        "Must include 'Owner Name' and 'Business Name' columns",
        type=['xlsx']
    )

with col2:
    st.markdown('<p class="upload-text">2. Upload Template Image</p>', unsafe_allow_html=True)
    template_image = st.file_uploader(
        "Select your birthday card template",
        type=['png', 'jpg', 'jpeg']
    )

# Font size adjustment
font_size = st.slider("Adjust font size", min_value=30, max_value=150, value=100)

if excel_file and template_image:
    try:
        # Read Excel data
        df = pd.read_excel(excel_file)
        
        # Validate columns
        required_columns = {'Owner Name', 'Business Name'}
        if not required_columns.issubset(df.columns):
            missing_cols = required_columns - set(df.columns)
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            st.stop()
            
        # Load template
        template = Image.open(template_image)
        template_width = template.width
        
        # Load font
        font = load_default_font(font_size)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as output_dir:
            # Add a status message
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # Generate images
            for i, row in df.iterrows():
                status_text.text(f"Processing card {i+1} of {len(df)}: {row['Owner Name']}")
                
                name = row['Owner Name']
                business = row['Business Name']
                
                img = template.copy()
                draw = ImageDraw.Draw(img)
                
                # Calculate positions
                name_position = get_centered_position(name, font, 590, template_width)
                business_position = get_centered_position(f"({business})", font, 660, template_width)
                
                # Draw text
                draw.text(name_position, name, fill="black", font=font)
                draw.text(business_position, f"({business})", fill="black", font=font)
                
                # Save image
                output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}_birthday.png")
                img.save(output_file)
                
                # Update progress
                progress_bar.progress((i + 1) / len(df))
            
            # Create zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, os.path.basename(file_path))
            
            # Success message
            st.success("✅ All cards generated successfully!")
            
            # Download button
            st.download_button(
                label="📥 Download Birthday Cards",
                data=zip_buffer.getvalue(),
                file_name="birthday_cards.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

# Instructions section
st.markdown("""
---
### 📝 Instructions

1. **Upload Excel File**
   - Must contain columns 'Owner Name' and 'Business Name'
   - File should be in .xlsx format

2. **Upload Template Image**
   - Supported formats: PNG, JPG, JPEG
   - Make sure the template has space for the text

3. **Adjust Font Size**
   - Use the slider to adjust text size as needed

4. **Download**
   - Click the download button to get a ZIP file with all generated cards
""")