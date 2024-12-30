import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

st.title("Birthday Card Generator")

# File uploads
excel_file = st.file_uploader("Upload Excel file (with 'Owner Name' and 'Business Name' columns)", type=['xlsx'])
template_image = st.file_uploader("Upload template image", type=['png', 'jpg', 'jpeg'])

if excel_file and template_image:
    # Read Excel data
    df = pd.read_excel(excel_file)

    # Validate columns
    if not {'Owner Name', 'Business Name'}.issubset(df.columns):
        st.error("The uploaded Excel file must have 'Owner Name' and 'Business Name' columns.")
        st.stop()

    # Load template
    template = Image.open(template_image)
    template_width = template.width

    # Create temporary directory for generated images
    with tempfile.TemporaryDirectory() as output_dir:
        # Font setup
        try:
            font = ImageFont.truetype("Arial-Bold.ttf", size=100)
        except OSError:
            font = ImageFont.load_default()

        def get_centered_position(text, font, y_position, image_width):
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            return ((image_width - text_width) // 2, y_position)

        # Progress bar
        progress_bar = st.progress(0)

        # Generate images
        for i, row in df.iterrows():
            name = row['Owner Name']
            business = row['Business Name']

            img = template.copy()
            draw = ImageDraw.Draw(img)

            name_position = get_centered_position(name, font, 590, template_width)
            business_position = get_centered_position(f"({business})", font, 660, template_width)

            draw.text(name_position, name, fill="black", font=font)
            draw.text(business_position, f"({business})", fill="black", font=font)

            output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}_birthday.png")
            img.save(output_file)

            # Update progress
            progress_bar.progress((i + 1) / len(df))

        # Create zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.basename(file_path))

        # Download button
        st.download_button(
            label="Download Generated Cards",
            data=zip_buffer.getvalue(),
            file_name="birthday_cards.zip",
            mime="application/zip"
        )

st.markdown("""
### Instructions:
1. Upload your Excel file with columns 'Owner Name' and 'Business Name'
2. Upload your template image
3. Click 'Download Generated Cards' to get a zip file with all generated images
""")
