import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

def main():
    st.title("Certificate Generator")
    
    uploaded_files = st.file_uploader("Upload Template Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        for i, uploaded_file in enumerate(uploaded_files):
            img = Image.open(uploaded_file)
            draw = ImageDraw.Draw(img)
            
            st.image(img, caption=f"Template {i+1}", use_column_width=True)
            
            st.markdown("##### Font Size")
            font_size = st.number_input("Enter font size:", min_value=10, max_value=150, value=25, step=1, key=f"font_num_{i}")
            font_size = st.slider("Adjust font size:", min_value=10, max_value=150, value=font_size, step=1, key=f"font_slider_{i}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name_y = st.number_input(
                    f"Name position (Template {i+1})", 
                    min_value=0, 
                    max_value=img.height, 
                    value=590 if img.height > 590 else img.height // 2, 
                    step=5, 
                    key=f"name_num_{i}"
                )
                name_y = st.slider(
                    f"Adjust Name position (Template {i+1})", 
                    min_value=0, 
                    max_value=img.height, 
                    value=name_y, 
                    step=5, 
                    key=f"name_slider_{i}"
                )
            
            with col2:
                business_y = st.number_input(
                    f"Business position (Template {i+1})", 
                    min_value=0, 
                    max_value=img.height, 
                    value=700 if img.height > 700 else img.height // 2, 
                    step=5, 
                    key=f"business_num_{i}"
                )
                business_y = st.slider(
                    f"Adjust Business position (Template {i+1})", 
                    min_value=0, 
                    max_value=img.height, 
                    value=business_y, 
                    step=5, 
                    key=f"business_slider_{i}"
                )
            
            # Dummy text placement logic (example)
            font = ImageFont.truetype("arial.ttf", font_size)
            draw.text((img.width // 2, name_y), "John Doe", font=font, fill=(0, 0, 0))
            draw.text((img.width // 2, business_y), "Business Name", font=font, fill=(0, 0, 0))
            
            st.image(img, caption=f"Updated Template {i+1}", use_column_width=True)

if __name__ == "__main__":
    main()
