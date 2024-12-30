import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

def get_centered_position(text, font, y_position, template_width):
    """
    Calculate the position for centering the text horizontally and placing it at a specific Y position.
    """
    bbox = ImageDraw.Draw(Image.new('RGB', (template_width, 1))).textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_position = (template_width - text_width) // 2  # Center horizontally
    return (x_position, y_position)

def generate_birthday_cards(df, template, font_size, name_y_position, business_y_position):
    """Generate birthday cards and return the zip buffer"""
    zip_buffer = io.BytesIO()
    
    with tempfile.TemporaryDirectory() as output_dir:
        try:
            # Try loading Arial-Bold font, if available in the working directory
            font_path = "Arial-Bold.ttf"  # Replace with correct path if not found
            font = ImageFont.truetype(font_path, size=font_size)
        except OSError as e:
            st.error(f"Error loading font: {e}. Falling back to default font.")
            font = ImageFont.load_default()
        
        template_width = template.width
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
            
            # Draw text with bold font
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
font_size = st.slider("Adjust font size", min_value=15, max_value=150, value=100)

# Only show position adjustments if template is uploaded
if template_image is not None:
    # Get template dimensions
    img = Image.open(template_image)
    img_height = img.height
    img_width = img.width
    
    # Show template preview and dimensions
    st.markdown("### Template Preview")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(template_image, caption="Template Image", use_container_width=True)
        st.markdown(f"""
        **Image Dimensions:**
        - Width: {img_width}px
        - Height: {img_height}px
        """)
    
    # Create two columns for position adjustments
    pos_col1, pos_col2 = st.columns(2)
    
    with pos_col1:
        name_y_position = st.slider(
            "Adjust name vertical position",
            min_value=0,
            max_value=img_height,
            value=min(590, img_height // 2)
        )
    
    with pos_col2:
        business_y_position = st.slider(
            "Adjust business name vertical position",
            min_value=0,
            max_value=img_height,
            value=min(660, int(img_height * 0.7))
        )
else:
    # Set default values when no template is uploaded
    name_y_position = 590
    business_y_position = 660

# Generate button
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

3. **Adjust Settings**
   - Font Size: Change the size of the text
   - Name Position: Adjust where the name appears vertically
   - Business Position: Adjust where the business name appears vertically

4. **Generate Cards**
   - Click "Generate Birthday Cards" to create all cards

5. **Download**
   - Once generated, click "Download Birthday Cards" to get the ZIP file
""")
