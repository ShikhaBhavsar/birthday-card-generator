import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

def load_bold_font(size):
    """Load a bold font that's likely to be available on most systems"""
    try:
        # Try different bold system fonts in order of preference
        bold_font_options = [
            "Arial-Bold.ttf",
            "ArialBD.ttf",  # Windows Arial Bold
            "DejaVuSans-Bold.ttf",
            "Helvetica-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux path
            "/System/Library/Fonts/Helvetica-Bold.ttc",  # MacOS path
            "C:\\Windows\\Fonts\\arialbd.ttf"  # Windows path
        ]
        
        for font_path in bold_font_options:
            try:
                return ImageFont.truetype(font_path, size=size)
            except OSError:
                continue
        
        # If no bold fonts work, try regular fonts
        regular_font_options = [
            "Arial.ttf",
            "DejaVuSans.ttf",
            "Helvetica.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        
        for font_path in regular_font_options:
            try:
                font = ImageFont.truetype(font_path, size=size)
                # Some PIL versions support font.font.style
                if hasattr(font, 'font') and hasattr(font.font, 'style'):
                    font.font.style = 'bold'
                return font
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

def preview_template(template, name, business, font, name_y_position, business_y_position):
    """Generate a preview of the card with the updated name and business positions"""
    preview_img = template.copy()
    draw = ImageDraw.Draw(preview_img)

    # Calculate positions using custom Y positions
    name_position = get_centered_position(name, font, name_y_position, template.width)
    business_position = get_centered_position(f"({business})", font, business_y_position, template.width)

    # Draw text with stroke for extra boldness if using default font
    if font == ImageFont.load_default():
        # Draw text multiple times with slight offsets for bold effect
        for offset in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            x, y = name_position
            draw.text((x + offset[0], y + offset[1]), name, fill="black", font=font)
            x, y = business_position
            draw.text((x + offset[0], y + offset[1]), f"({business})", fill="black", font=font)
    else:
        # Draw text normally if using a bold font
        draw.text(name_position, name, fill="black", font=font)
        draw.text(business_position, f"({business})", fill="black", font=font)

    return preview_img

def generate_birthday_cards(df, template, font_size, name_y_position, business_y_position):
    """Generate birthday cards and return the zip buffer"""
    zip_buffer = io.BytesIO()
    
    with tempfile.TemporaryDirectory() as output_dir:
        # Load bold font
        font = load_bold_font(font_size)
        template_width = template.width
        
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
            
            # Calculate positions using custom Y positions
            name_position = get_centered_position(name, font, name_y_position, template_width)
            business_position = get_centered_position(f"({business})", font, business_y_position, template_width)
            
            # Draw text with stroke for extra boldness if using default font
            if font == ImageFont.load_default():
                # Draw text multiple times with slight offsets for bold effect
                for offset in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                    x, y = name_position
                    draw.text((x + offset[0], y + offset[1]), name, fill="black", font=font)
                    x, y = business_position
                    draw.text((x + offset[0], y + offset[1]), f"({business})", fill="black", font=font)
            else:
                # Draw text normally if using a bold font
                draw.text(name_position, name, fill="black", font=font)
                draw.text(business_position, f"({business})", fill="black", font=font)
            
            # Save image
            output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}_birthday.png")
            img.save(output_file)
            
            # Update progress
            progress_bar.progress((i + 1) / len(df))
        
        # Create zip file
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.basename(file_path))
    
    status_text.empty()
    progress_bar.empty()
    return zip_buffer

# Initialize session state
if 'zip_buffer' not in st.session_state:
    st.session_state.zip_buffer = None
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'template_height' not in st.session_state:
    st.session_state.template_height = 0

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
# Preview the adjustments on the template image with a smaller width
if template_image:
    template = Image.open(template_image)
    font = load_bold_font(font_size)
    preview_image = preview_template(template, "Happy Birthday", "My Business", font, name_y_position, business_y_position)
    st.image(preview_image, caption="Preview of the Template", height=400)  # Set a fixed height for smaller preview

# Create two columns for adjustments
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Font Size")
    font_size = st.slider("Adjust font size", min_value=10, max_value=150, value=25)

# Ensure template height is not 0
if st.session_state.template_height > 0:
    with col2:
        st.markdown("##### Name Position")
        name_y_position = st.slider(
            "Adjust name vertical position",
            min_value=0,
            max_value=st.session_state.template_height,
            value=590 if st.session_state.template_height > 590 else st.session_state.template_height // 2
        )
        
        st.markdown("##### Business Name Position")
        business_y_position = st.slider(
            "Adjust business name vertical position",
            min_value=0,
            max_value=st.session_state.template_height,
            value=700 if st.session_state.template_height > 700 else st.session_state.template_height // 2
        )

    # Preview the adjustments on the template image
    if template_image:
        template = Image.open(template_image)
        font = load_bold_font(font_size)
        preview_image = preview_template(template, "Happy Birthday", "My Business", font, name_y_position, business_y_position)
        st.image(preview_image, caption="Preview of the Template", use_column_width=True)
else:
    with col2:
        st.warning("Please upload a valid template image.")

# Create button to generate birthday cards
if excel_file and template_image:
    if st.button("Generate Birthday Cards"):
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
            
            # Generate cards and store in session state
            zip_buffer = generate_birthday_cards(
                df, 
                template, 
                font_size, 
                name_y_position, 
                business_y_position
            )
            st.session_state.zip_buffer = zip_buffer.getvalue()
            st.session_state.generated = True
            
            # Success message
            st.success("✅ All cards generated successfully!")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

# Download button (only shows if cards have been generated)
if st.session_state.generated and st.session_state.zip_buffer:
    st.download_button(
        label="📥 Download Birthday Cards",
        data=st.session_state.zip_buffer,
        file_name="birthday_cards.zip",
        mime="application/zip"
    )

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

4. **Generate Cards**
   - Click "Generate Birthday Cards" to create all cards

5. **Download**
   - Once generated, click "Download Birthday Cards" to get the ZIP file
""")

