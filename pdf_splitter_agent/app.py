import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

st.set_page_config(page_title="PDF Splitter Agent", layout="centered")

st.title("📄 PDF Splitter Agent")
st.write("Upload a PDF and choose how many pages to extract from the start.")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Read the PDF
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        st.success(f"✅ PDF uploaded. Total pages: {total_pages}")

        # Select number of pages to keep
        num_pages_to_keep = st.number_input(
            "Select how many pages you want to keep (from start)",
            min_value=1,
            max_value=total_pages,
            value=2,
            step=1
        )

        if st.button("✂️ Split and Download"):
            writer = PdfWriter()
            for i in range(num_pages_to_keep):
                writer.add_page(reader.pages[i])

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            st.download_button(
                label="📥 Download Split PDF",
                data=output,
                file_name=f"split_{num_pages_to_keep}_pages.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Something went wrong: {e}")
