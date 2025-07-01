import streamlit as st
import fitz  # PyMuPDF
import io

def parse_page_numbers(page_string, max_pages):
    """
    Parses a string of page numbers and ranges (e.g., "1, 3, 5-7")
    into a sorted list of unique page indices (0-indexed).
    """
    pages = set()
    try:
        parts = page_string.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start > end or start < 1 or end > max_pages:
                    raise ValueError("Invalid page range.")
                for i in range(start, end + 1):
                    pages.add(i - 1)
            else:
                page_num = int(part)
                if page_num < 1 or page_num > max_pages:
                    raise ValueError("Page number out of range.")
                pages.add(page_num - 1)
    except ValueError as e:
        raise ValueError(f"Invalid page string format. Use numbers and ranges like '1, 3, 5-7'. Details: {e}")
    
    return sorted(list(pages))

def split_pdf_custom(file_bytes, page_indices):
    """
    Creates a new PDF from a list of specific page indices.
    """
    try:
        # Open the original PDF from bytes
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Create a new PDF to store the selected pages
        new_pdf = fitz.open()
        
        # Add selected pages to the new PDF
        for page_index in page_indices:
            new_pdf.insert_pdf(pdf_document, from_page=page_index, to_page=page_index)
        
        # Save the new PDF to a bytes buffer
        output_buffer = io.BytesIO()
        new_pdf.save(output_buffer)
        new_pdf.close()
        pdf_document.close()
        
        output_buffer.seek(0)
        return output_buffer, None
        
    except Exception as e:
        return None, f"An error occurred: {e}"

import zipfile

import zipfile

# Streamlit app layout
st.title("Advanced PDF Page Extractor")
st.write("Upload PDFs and specify unique page ranges for each.")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    
    page_selections = {}

    for uploaded_file in uploaded_files:
        try:
            bytes_data = uploaded_file.getvalue()
            pdf_check = fitz.open(stream=io.BytesIO(bytes_data), filetype="pdf")
            total_pages = len(pdf_check)
            pdf_check.close()
            
            # Create a unique key for the text input
            key = f"pages_for_{uploaded_file.name}"
            
            # Display file info and get page selection
            st.write(f"*File: {uploaded_file.name}* ({total_pages} pages)")
            page_selections[uploaded_file.name] = st.text_input(
                "Pages to extract (e.g., '1, 3, 5-7')", 
                value=f"1-{total_pages}", 
                key=key
            )
            # Reset file buffer for later use
            uploaded_file.seek(0)

        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")
            continue

    if st.button("Process All PDFs"):
        st.write("Processing...")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                selection_str = page_selections.get(file_name)
                
                if not selection_str:
                    st.warning(f"No page selection for {file_name}. Skipping.")
                    continue

                try:
                    bytes_data = uploaded_file.getvalue()
                    pdf_check = fitz.open(stream=io.BytesIO(bytes_data), filetype="pdf")
                    total_pages = len(pdf_check)
                    pdf_check.close()

                    page_indices = parse_page_numbers(selection_str, total_pages)
                    
                    if not page_indices:
                        st.warning(f"Invalid or empty page selection for {file_name}. Skipping.")
                        continue

                    new_pdf_bytes, error = split_pdf_custom(bytes_data, page_indices)
                    
                    if error:
                        st.warning(f"Could not process {file_name}: {error}. Skipping.")
                    else:
                        zf.writestr(f"extracted_{file_name}", new_pdf_bytes.getvalue())

                except Exception as e:
                    st.error(f"Failed to process {file_name}: {e}")

        zip_buffer.seek(0)
        
        st.success("Processing complete!")
        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer,
            file_name="extracted_pdfs_collection.zip",
            mime="application/zip"
        )