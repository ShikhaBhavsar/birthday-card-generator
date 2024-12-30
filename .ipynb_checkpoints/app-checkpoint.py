{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "682f5a62-c490-40ff-b091-c2f1ce272619",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2024-12-30 22:57:47.969 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.317 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\ipykernel_launcher.py [ARGUMENTS]\n",
      "2024-12-30 22:57:48.318 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.319 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.319 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.320 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.321 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.321 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.322 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.323 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.324 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.325 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.325 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.327 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2024-12-30 22:57:48.328 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "DeltaGenerator()"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import streamlit as st\n",
    "from PIL import Image, ImageDraw, ImageFont\n",
    "import pandas as pd\n",
    "import os\n",
    "import io\n",
    "import zipfile\n",
    "import tempfile\n",
    "\n",
    "st.title(\"Birthday Card Generator\")\n",
    "\n",
    "# File uploads\n",
    "excel_file = st.file_uploader(\"Upload Excel file (with 'Owner Name' and 'Business Name' columns)\", type=['xlsx'])\n",
    "template_image = st.file_uploader(\"Upload template image\", type=['png', 'jpg', 'jpeg'])\n",
    "\n",
    "if excel_file and template_image:\n",
    "    # Read Excel data\n",
    "    df = pd.read_excel(excel_file)\n",
    "    \n",
    "    # Load template\n",
    "    template = Image.open(template_image)\n",
    "    template_width = template.width\n",
    "    \n",
    "    # Create temporary directory for generated images\n",
    "    with tempfile.TemporaryDirectory() as output_dir:\n",
    "        # Font setup (using default font since we can't access system fonts)\n",
    "        font = ImageFont.truetype(\"Arial\", size=25)\n",
    "        \n",
    "        def get_centered_position(text, font, y_position, image_width):\n",
    "            bbox = font.getbbox(text)\n",
    "            text_width = bbox[2] - bbox[0]\n",
    "            return ((image_width - text_width) // 2, y_position)\n",
    "        \n",
    "        # Progress bar\n",
    "        progress_bar = st.progress(0)\n",
    "        \n",
    "        # Generate images\n",
    "        for i in range(len(df)):\n",
    "            name = df['Owner Name'][i]\n",
    "            business = df['Business Name'][i]\n",
    "            \n",
    "            img = template.copy()\n",
    "            draw = ImageDraw.Draw(img)\n",
    "            \n",
    "            name_position = get_centered_position(name, font, 590, template_width)\n",
    "            business_position = get_centered_position(f\"({business})\", font, 660, template_width)\n",
    "            \n",
    "            draw.text(name_position, name, fill=\"black\", font=font)\n",
    "            draw.text(business_position, f\"({business})\", fill=\"black\", font=font)\n",
    "            \n",
    "            output_file = os.path.join(output_dir, f\"{name.replace(' ', '_')}_birthday.png\")\n",
    "            img.save(output_file)\n",
    "            \n",
    "            # Update progress\n",
    "            progress_bar.progress((i + 1) / len(df))\n",
    "        \n",
    "        # Create zip file in memory\n",
    "        zip_buffer = io.BytesIO()\n",
    "        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:\n",
    "            for root, dirs, files in os.walk(output_dir):\n",
    "                for file in files:\n",
    "                    file_path = os.path.join(root, file)\n",
    "                    zip_file.write(file_path, os.path.basename(file_path))\n",
    "        \n",
    "        # Download button\n",
    "        st.download_button(\n",
    "            label=\"Download Generated Cards\",\n",
    "            data=zip_buffer.getvalue(),\n",
    "            file_name=\"birthday_cards.zip\",\n",
    "            mime=\"application/zip\"\n",
    "        )\n",
    "\n",
    "st.markdown(\"\"\"\n",
    "### Instructions:\n",
    "1. Upload your Excel file with columns 'Owner Name' and 'Business Name'\n",
    "2. Upload your template image\n",
    "3. Click 'Download Generated Cards' to get a zip file with all generated images\n",
    "\"\"\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b0061f9e-af8e-4d19-8119-5d863dba0ba9",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
