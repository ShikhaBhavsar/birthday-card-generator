import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

[Previous font loading functions remain the same...]

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
            
            [Rest of the image generation code remains the same...]

# Initialize session state
if 'zip_buffer' not in st.session_state:
    st.session_state.zip_buffer = None
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'template_height' not in st.session_state:
    st.session_state.template_height = 0

[Previous page config and CSS remains the same...]

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

# Update template height when image is uploaded
if template_image:
    img = Image.open(template_image)
    st.session_state.template_height = img.height

# Create three columns for adjustments
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### Font Size")
    font_size = st.slider("Adjust font size", min_value=30, max_value=150, value=100)

with col2:
    st.markdown("##### Name Position")
    name_y_position = st.slider(
        "Adjust name vertical position",
        min_value=0,
        max_value=st.session_state.template_height,
        value=590 if st.session_state.template_height > 590 else st.session_state.template_height // 2
    )

with col3:
    st.markdown("##### Business Name Position")
    business_y_position = st.slider(
        "Adjust business name vertical position",
        min_value=0,
        max_value=st.session_state.template_height,
        value=660 if st.session_state.template_height > 660 else (st.session_state.template_height * 2) // 3
    )

# Preview section
if template_image:
    st.markdown("### Preview")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(template_image, caption="Template Image", use_column_width=True)
        st.markdown(f"""
        **Image Dimensions:**
        - Width: {Image.open(template_image).width}px
        - Height: {Image.open(template_image).height}px
        """)

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

[Download button and instructions section remain the same...]

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