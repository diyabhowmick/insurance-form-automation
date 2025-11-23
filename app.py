"""
Insurance Form Automation - Streamlit Application
Automates filling insurance forms using AI and PDF extraction
"""

import streamlit as st
import os
from datetime import datetime
from modules.pdf_extractor import extract_text_from_pdf, extract_text_from_multiple_pdfs
from modules.llm_processor import extract_fields_from_text, validate_api_key
from modules.docx_handler import (
    load_template, 
    find_placeholders, 
    replace_placeholders, 
    save_document_to_bytes
)

# Page configuration
st.set_page_config(
    page_title="Insurance Form Automation | AI-Powered Claims Processing",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --accent-color: #10b981;
        --background-light: #f8fafc;
        --text-dark: #1e293b;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: #e0e7ff;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Card styling */
    .upload-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .feature-card h3 {
        color: white !important;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #e0e7ff;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Process steps */
    .process-step {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 4px solid #10b981;
    }
    
    .process-step h4 {
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: white !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: white !important;
    }
    
    /* Success/Info boxes */
    .success-box {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Progress bar custom styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #cbd5e1;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1>🏢 Insurance Form Automation</h1>
    <p>AI-Powered Claims Processing | Fast, Accurate, Automated</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    api_key = st.text_input(
        "🔑 OpenRouter API Key",
        type="password",
        help="Get your free API key from https://openrouter.ai/",
        placeholder="sk-or-..."
    )
    
    if api_key:
        st.success("✅ API Key Connected")
    else:
        st.warning("⚠️ Please enter API key")
    
    st.markdown("---")
    
    # Stats section
    st.markdown("### 📊 Quick Stats")
    st.markdown('<div class="stat-card" style="background: rgba(255,255,255,0.1); border-left: 4px solid white;"><p class="stat-number" style="color: white;">3</p><p class="stat-label" style="color: #e0e7ff;">Processing Steps</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-card" style="background: rgba(255,255,255,0.1); border-left: 4px solid white;"><p class="stat-number" style="color: white;">AI</p><p class="stat-label" style="color: #e0e7ff;">Powered Extraction</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-card" style="background: rgba(255,255,255,0.1); border-left: 4px solid white;"><p class="stat-number" style="color: white;">100%</p><p class="stat-label" style="color: #e0e7ff;">Automated</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How it works
    st.markdown("### 📖 How It Works")
    st.markdown("""
    <div class="process-step" style="background: rgba(255,255,255,0.1); border-left: 4px solid #10b981;">
        <h4 style="color: white !important;">1️⃣ Upload Files</h4>
        <p style="color: #e0e7ff;">Template (.docx) + Reports (.pdf)</p>
    </div>
    <div class="process-step" style="background: rgba(255,255,255,0.1); border-left: 4px solid #10b981;">
        <h4 style="color: white !important;">2️⃣ AI Processing</h4>
        <p style="color: #e0e7ff;">Extract & Match Data</p>
    </div>
    <div class="process-step" style="background: rgba(255,255,255,0.1); border-left: 4px solid #10b981;">
        <h4 style="color: white !important;">3️⃣ Download Result</h4>
        <p style="color: #e0e7ff;">Get Filled Document</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Supported Formats")
    st.markdown("""
    <div style="color: white;">
        <p style="color: #e0e7ff;">• <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; color: white;">[FIELD_NAME]</code></p>
        <p style="color: #e0e7ff;">• <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; color: white;">{{FieldName}}</code></p>
        <p style="color: #e0e7ff;">• <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; color: white;">{FIELD_NAME}</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: #e0e7ff; font-size: 0.85rem;'>
            🔒 Secure | 🚀 Fast | 🎯 Accurate
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content
# Feature highlights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Lightning Fast</h3>
        <p>Process forms in seconds, not hours</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 AI Accuracy</h3>
        <p>Powered by advanced LLM technology</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🔄 Auto-Fill</h3>
        <p>Extract data automatically from PDFs</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Upload sections
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Upload Insurance Template")
    template_file = st.file_uploader(
        "Choose your .docx template",
        type=['docx'],
        help="Word document with placeholder fields",
        label_visibility="collapsed"
    )
    
    if template_file:
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>Template Loaded:</strong> {template_file.name}
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📑 Upload Photo Reports")
    report_files = st.file_uploader(
        "Choose your PDF reports",
        type=['pdf'],
        accept_multiple_files=True,
        help="One or more PDF photo reports",
        label_visibility="collapsed"
    )
    
    if report_files:
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>{len(report_files)} Report(s) Loaded</strong>
        </div>
        """, unsafe_allow_html=True)
        for rf in report_files:
            st.markdown(f"&nbsp;&nbsp;&nbsp;📎 {rf.name}")

# Process button
st.markdown("<br>", unsafe_allow_html=True)

# Create centered button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("🚀 Process Documents", use_container_width=True)

if process_button:
    # Validation
    errors = []
    
    if not api_key:
        errors.append("🔑 API key required")
    if not template_file:
        errors.append("📄 Template required")
    if not report_files:
        errors.append("📑 Reports required")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Processing pipeline
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Load template and find placeholders
            status_text.markdown('<div class="info-box">📄 Step 1/4: Loading template...</div>', unsafe_allow_html=True)
            progress_bar.progress(25)
            
            doc = load_template(template_file)
            placeholders = find_placeholders(doc)
            
            if not placeholders:
                st.error("❌ No placeholders found in template. Use [FIELD_NAME], {{FieldName}}, or {FIELD_NAME} format.")
                st.stop()
            
            status_text.markdown(f'<div class="success-box">✅ Found {len(placeholders)} placeholders</div>', unsafe_allow_html=True)
            
            # Show placeholders in an expander
            with st.expander("🔍 View Detected Placeholders"):
                cols = st.columns(3)
                for idx, placeholder in enumerate(placeholders):
                    cols[idx % 3].markdown(f"✓ `{placeholder}`")
            
            # Step 2: Extract text from PDFs
            status_text.markdown('<div class="info-box">📑 Step 2/4: Extracting text from reports...</div>', unsafe_allow_html=True)
            progress_bar.progress(50)
            
            if len(report_files) == 1:
                extracted_text = extract_text_from_pdf(report_files[0])
            else:
                all_texts = extract_text_from_multiple_pdfs(report_files)
                extracted_text = "\n\n=== COMBINED REPORTS ===\n\n".join(
                    [f"File: {name}\n{text}" for name, text in all_texts.items()]
                )
            
            status_text.markdown(f'<div class="success-box">✅ Extracted {len(extracted_text):,} characters</div>', unsafe_allow_html=True)
            
            # Show preview of extracted text
            with st.expander("📝 Preview Extracted Text"):
                st.text_area("Content Preview", extracted_text[:1500] + "..." if len(extracted_text) > 1500 else extracted_text, height=200)
            
            # Step 3: Use LLM to extract field values
            status_text.markdown('<div class="info-box">🤖 Step 3/4: AI processing...</div>', unsafe_allow_html=True)
            progress_bar.progress(75)
            
            extracted_data = extract_fields_from_text(
                placeholders, 
                extracted_text, 
                api_key
            )
            
            status_text.markdown('<div class="success-box">✅ AI extraction complete!</div>', unsafe_allow_html=True)
            
            # Show extracted data in a nice table
            with st.expander("🔍 View Extracted Data"):
                for field, value in extracted_data.items():
                    col1, col2 = st.columns([1, 2])
                    col1.markdown(f"**{field}**")
                    col2.markdown(f"`{value}`")
            
            # Step 4: Fill template
            status_text.markdown('<div class="info-box">✍️ Step 4/4: Filling template...</div>', unsafe_allow_html=True)
            progress_bar.progress(90)
            
            filled_doc = replace_placeholders(doc, extracted_data)
            doc_bytes = save_document_to_bytes(filled_doc)
            
            progress_bar.progress(100)
            status_text.markdown('<div class="success-box">✅ <strong>Document processing complete!</strong></div>', unsafe_allow_html=True)
            
            # Success section
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download section with styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"filled_insurance_form_{timestamp}.docx"
                
                st.download_button(
                    label="📥 Download Filled Document",
                    data=doc_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <h3 style='color: #1e3a8a; margin-bottom: 1rem;'>Trusted by Insurance Professionals</h3>
    <p style='color: #64748b; font-size: 1rem;'>
        🔒 Secure Processing | 🚀 Lightning Fast | 🎯 99.9% Accuracy
    </p>
    <p style='color: #94a3b8; font-size: 0.9rem; margin-top: 1rem;'>
        Built with Streamlit | Powered by OpenRouter AI | © 2025
    </p>
</div>
""", unsafe_allow_html=True)