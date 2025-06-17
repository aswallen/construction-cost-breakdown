"""
Construction Cost Breakdown Automation - Streamlit Web App
Optimized for Snowflake Streamlit Environment

A user-friendly web interface for automating construction cost breakdowns.
Upload documents, process with AI, and get formatted Excel outputs.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import pandas as pd
from construction_cost_automation import ConstructionCostAutomation
import zipfile
import io

# Page configuration
st.set_page_config(
    page_title="Construction Cost Breakdown Automation",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-box {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'automation' not in st.session_state:
        st.session_state.automation = None
    if 'api_key_set' not in st.session_state:
        st.session_state.api_key_set = False

def check_environment_capabilities():
    """Check what libraries are available in the current environment"""
    capabilities = {
        'pdf_processing': False,
        'ocr_available': False,
        'ai_available': False,
        'pdf_library': 'None',
        'is_cloud_environment': False,
        'is_snowflake': False,
        'debug_info': {}  # Add debug information
    }
    
    # Detect Snowflake environment specifically (not all cloud environments)
    snowflake_indicators = [
        'SNOWFLAKE' in str(os.environ),
        any('SNOWFLAKE' in key for key in os.environ.keys()),
        # Check for Snowflake-specific environment variables
        'SNOWFLAKE_WAREHOUSE' in os.environ,
        'SNOWFLAKE_DATABASE' in os.environ
    ]
    capabilities['is_snowflake'] = any(snowflake_indicators)
    capabilities['debug_info']['snowflake_indicators'] = snowflake_indicators
    
    # Only consider it a limited cloud environment if it's specifically Snowflake
    capabilities['is_cloud_environment'] = capabilities['is_snowflake']
    
    # Check PDF processing
    try:
        import fitz
        capabilities['pdf_processing'] = True
        capabilities['pdf_library'] = 'PyMuPDF (Premium)'
    except ImportError:
        try:
            import PyPDF2
            capabilities['pdf_processing'] = True
            capabilities['pdf_library'] = 'PyPDF2 (Compatible)'
        except ImportError:            pass
    
    # Check OCR (may not be available in some cloud environments)
    try:
        import pytesseract
        # Test if pytesseract can actually run (not just imported)
        pytesseract.get_tesseract_version()
        capabilities['ocr_available'] = True
    except (ImportError, Exception):
        capabilities['ocr_available'] = False
      # Check AI availability by actually trying to import (not based on environment)
    ai_error = None
    try:
        import google.generativeai
        capabilities['ai_available'] = True
        capabilities['debug_info']['ai_import_success'] = True
        capabilities['debug_info']['ai_version'] = getattr(google.generativeai, '__version__', 'Unknown')
    except ImportError as e:
        capabilities['ai_available'] = False
        ai_error = str(e)
        capabilities['debug_info']['ai_import_success'] = False
        capabilities['debug_info']['ai_import_error'] = ai_error
    except Exception as e:
        capabilities['ai_available'] = False
        ai_error = str(e)
        capabilities['debug_info']['ai_import_success'] = False
        capabilities['debug_info']['ai_import_error'] = f"Unexpected error: {ai_error}"
    
    return capabilities

def setup_api_key():
    """Handle API key setup with multiple options"""
    st.sidebar.header("🔑 API Configuration")
    
    capabilities = check_environment_capabilities()
    
    # First, try to configure AI regardless of environment
    # This allows for AI processing even in cloud environments if libraries are available
    
    # Option 1: Check if API key is already in environment
    existing_key = os.getenv('GEMINI_API_KEY')
    if existing_key:
        try:
            # Test if AI libraries are actually available
            import google.generativeai
            st.sidebar.success("✅ API Key loaded from environment")
            st.session_state.api_key_set = True
            if st.session_state.automation is None:
                st.session_state.automation = ConstructionCostAutomation(existing_key)
            return True
        except ImportError:
            st.sidebar.warning("⚠️ API Key found but AI libraries not available")
    
    # Option 2: Check if API key is stored in company config
    try:
        from config_company import GEMINI_API_KEY
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here":
            try:
                # Test if AI libraries are actually available
                import google.generativeai
                st.sidebar.success("✅ API Key loaded from company configuration")
                st.session_state.api_key_set = True
                if st.session_state.automation is None:
                    st.session_state.automation = ConstructionCostAutomation(GEMINI_API_KEY)
                return True
            except ImportError:
                st.sidebar.warning("⚠️ API Key found in config but AI libraries not available")
    except (ImportError, AttributeError):
        pass
    
    # Option 3: Check if API key is stored in a secure file
    api_key_file = "api_key.txt"
    if os.path.exists(api_key_file):
        try:
            with open(api_key_file, 'r') as f:
                file_key = f.read().strip()
            if file_key and file_key != "your_actual_api_key_here":
                try:
                    # Test if AI libraries are actually available
                    import google.generativeai
                    st.sidebar.success("✅ API Key loaded from secure file")
                    st.session_state.api_key_set = True
                    if st.session_state.automation is None:
                        st.session_state.automation = ConstructionCostAutomation(file_key)
                    return True
                except ImportError:
                    st.sidebar.warning("⚠️ API Key found in file but AI libraries not available")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not read API key file: {e}")    
    # Handle different environments based on actual AI availability
    if not capabilities['ai_available']:
        if capabilities['is_snowflake']:
            st.sidebar.info("🏔️ **Snowflake Environment Detected**")
            st.sidebar.markdown("AI libraries not available. App will run in manual mode.")
        else:
            # AI libraries not available but not in Snowflake - show installation help
            st.sidebar.warning("⚠️ **AI Libraries Not Available**")
            st.sidebar.markdown("Install google-generativeai or configure API key to enable AI processing.")
    else:
        # AI libraries are available - allow API key configuration
        st.sidebar.info("💡 **API Key Options:**")
        st.sidebar.markdown("""
        **For IT Administrators:**
        1. Set environment variable: `GEMINI_API_KEY`
        2. Edit `config_company.py` file
        3. Create `api_key.txt` file (secure)
        
        **For Individual Users:**
        Enter your API key below (temporary session)
        """)
        
        api_key = st.sidebar.text_input(
            "Enter your Google Gemini API Key:",
            type="password",
            help="Get your API key from Google AI Studio"
        )
        
        if api_key:
            try:
                st.session_state.automation = ConstructionCostAutomation(api_key)
                st.session_state.api_key_set = True
                st.sidebar.success("✅ API Key configured successfully")
                return True
            except Exception as e:
                st.sidebar.error(f"❌ Error configuring API: {e}")
                return False
        else:            st.sidebar.warning("⚠️ Please enter your Gemini API key to use AI processing")
    
    # Fallback to manual mode
    st.sidebar.info("💡 Manual processing mode available - no AI needed")
    st.session_state.api_key_set = False
    if st.session_state.automation is None:
        st.session_state.automation = ConstructionCostAutomation()
    return False

def upload_template():
    """Handle template upload"""
    st.sidebar.header("📋 Template Upload")
    
    # Check for default template
    default_template = "_Construction_Breakdown_Template_BLANK.xlsx"
    if os.path.exists(default_template):
        st.sidebar.success(f"✅ Default template found: {default_template}")
        return default_template
    
    # Allow user to upload template
    template_file = st.sidebar.file_uploader(
        "Upload Excel Template",
        type=['xlsx', 'xls'],
        help="Upload your construction cost breakdown template"
    )
    
    if template_file:
        # Save uploaded template
        template_path = f"temp_template_{template_file.name}"
        with open(template_path, "wb") as f:
            f.write(template_file.getbuffer())
        st.sidebar.success(f"✅ Template uploaded: {template_file.name}")
        return template_path
    
    st.sidebar.warning("⚠️ Please upload an Excel template")
    return None

def process_single_file(uploaded_file, template_path, automation):
    """Process a single uploaded file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = tmp_file.name
        
        # Generate output filename
        output_filename = f"COMPLETED_{Path(uploaded_file.name).stem}_breakdown.xlsx"
        
        # Process the document
        with st.spinner(f"Processing {uploaded_file.name}..."):
            result_path = automation.process_document(temp_path, template_path, output_filename)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if result_path and os.path.exists(result_path):
            return result_path, output_filename
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {e}")
        return None, None

def process_documents_manual_mode(uploaded_files, template_path, automation):
    """Process multiple uploaded documents in manual mode (no AI parsing)"""
    try:
        st.header("📄 Manual Processing Mode")
        st.info("🛠️ **Manual Mode Active** - Review extracted text and enter line items manually")
        
        if automation is None:
            st.error("❌ Automation system not initialized")
            return
        
        processed_files = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Extracting text from {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_path = tmp_file.name
                
                # Extract text from the file
                extracted_text = automation.extract_text_from_file(temp_path)
                
                if extracted_text.strip():
                    st.subheader(f"📝 Text from: {uploaded_file.name}")
                    
                    # Show extracted text in expandable section
                    with st.expander(f"View extracted text ({len(extracted_text)} characters)", expanded=False):
                        st.text_area(
                            "Raw extracted text:",
                            value=extracted_text,
                            height=200,
                            key=f"text_{i}",
                            help="Copy this text and manually enter line items below"
                        )
                    
                    # Manual data entry section
                    st.markdown("### ✏️ Manual Data Entry")
                    st.markdown("Based on the extracted text above, enter the line items and amounts:")
                    
                    # Dynamic form for manual entry
                    num_items = st.number_input(f"Number of line items for {uploaded_file.name}:", 
                                              min_value=1, max_value=50, value=5, key=f"num_{i}")
                    
                    manual_data = []
                    with st.form(f"manual_form_{i}"):
                        for j in range(int(num_items)):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                line_item = st.text_input(f"Line Item {j+1}:", key=f"item_{i}_{j}")
                            with col2:
                                amount = st.number_input(f"Amount {j+1}:", min_value=0.0, format="%.2f", key=f"amount_{i}_{j}")
                            
                            if line_item.strip() and amount > 0:
                                manual_data.append({'line_item': line_item.strip(), 'amount': amount})
                        
                        if st.form_submit_button(f"Generate Breakdown for {uploaded_file.name}"):
                            if manual_data:
                                # Generate output filename
                                output_filename = f"COMPLETED_{Path(uploaded_file.name).stem}_breakdown.xlsx"
                                
                                # Populate template with manual data
                                success = automation.populate_template(manual_data, template_path, output_filename)
                                
                                if success and os.path.exists(output_filename):
                                    processed_files.append((output_filename, uploaded_file.name))
                                    st.success(f"✅ Generated breakdown for {uploaded_file.name}")
                                    
                                    # Offer immediate download
                                    with open(output_filename, "rb") as file:
                                        st.download_button(
                                            label=f"📥 Download {output_filename}",
                                            data=file.read(),
                                            file_name=output_filename,
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key=f"download_{i}"
                                        )
                                else:
                                    st.error(f"❌ Failed to generate breakdown for {uploaded_file.name}")
                            else:
                                st.warning("Please enter at least one line item with an amount.")
                    
                    st.markdown("---")  # Separator between files
                else:
                    st.error(f"❌ Could not extract text from {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                # Show debug info
                with st.expander("🔧 Debug Information"):
                    st.write(f"**Error Type:** {type(e).__name__}")
                    st.write(f"**Error Details:** {str(e)}")
                    st.write(f"**File Name:** {uploaded_file.name}")
                    st.write(f"**File Size:** {uploaded_file.size if hasattr(uploaded_file, 'size') else 'Unknown'}")
            
            finally:
                # Clean up temp file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass  # Ignore cleanup errors
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("Text extraction complete!")
        st.session_state.processed_files.extend(processed_files)
    
    except Exception as e:
        st.error(f"❌ **Critical Error in Manual Processing:** {str(e)}")
        with st.expander("🔧 Debug Information"):
            st.write(f"**Error Type:** {type(e).__name__}")
            st.write(f"**Error Details:** {str(e)}")
            st.write(f"**Automation Object:** {automation is not None}")
            st.write(f"**Template Path:** {template_path}")
            st.write(f"**Number of Files:** {len(uploaded_files) if uploaded_files else 'None'}")

def create_download_zip(file_paths):
    """Create a ZIP file for multiple downloads"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏗️ Construction Cost Breakdown Automation</h1>', unsafe_allow_html=True)
    
    # Display environment info    capabilities = check_environment_capabilities()
    
    # Environment status in sidebar
    st.sidebar.markdown("### 🔧 Environment Status")
    
    # Show Snowflake-specific message only for actual Snowflake environments
    if capabilities['is_snowflake']:
        st.sidebar.info("🏔️ **Snowflake Environment Detected**")
    elif capabilities['is_cloud_environment']:
        st.sidebar.info("☁️ **Cloud Environment**")
    
    if capabilities['pdf_processing']:
        st.sidebar.success(f"✅ PDF Processing: {capabilities['pdf_library']}")
    else:
        st.sidebar.error("❌ PDF Processing: Not Available")
        st.sidebar.info("💡 Install PyPDF2 or PyMuPDF for PDF support")
    
    if capabilities['ocr_available']:
        st.sidebar.success("✅ Image OCR: Available")
    else:
        st.sidebar.warning("⚠️ Image OCR: Not Available")
        if capabilities['is_snowflake']:
            st.sidebar.info("💡 **Snowflake:** Convert images to PDF before uploading")
        else:
            st.sidebar.info("💡 **Tip:** Install Tesseract for OCR support")
    
    st.sidebar.success("✅ Excel Processing: Available")
      # Show AI status based on actual availability, not environment assumptions
    if capabilities['ai_available']:
        st.sidebar.success("✅ AI Processing: Available")
    else:
        if capabilities['is_snowflake']:
            st.sidebar.info("ℹ️ AI Processing: Not Available in Snowflake")
            st.sidebar.markdown("🛠️ **Manual Mode:** Extract and enter data manually")
        else:
            st.sidebar.warning("⚠️ AI Processing: Not Available")
            st.sidebar.info("💡 Install google-generativeai library or configure API key")
    
    # Debug information (if requested)
    if st.sidebar.checkbox("🔍 Show Debug Info", help="Show detailed environment and capability information"):
        st.sidebar.markdown("### 🔧 Debug Information")
        debug_info = capabilities.get('debug_info', {})
        
        # Show environment detection
        st.sidebar.write(f"**Snowflake detected:** {capabilities['is_snowflake']}")
        if 'snowflake_indicators' in debug_info:
            st.sidebar.write(f"**Snowflake indicators:** {debug_info['snowflake_indicators']}")
        
        # Show AI detection details
        st.sidebar.write(f"**AI available:** {capabilities['ai_available']}")
        if 'ai_import_success' in debug_info:
            st.sidebar.write(f"**AI import success:** {debug_info['ai_import_success']}")
        if 'ai_import_error' in debug_info:
            st.sidebar.error(f"**AI import error:** {debug_info['ai_import_error']}")
        if 'ai_version' in debug_info:
            st.sidebar.write(f"**AI library version:** {debug_info['ai_version']}")
        
        # Show all capabilities
        st.sidebar.json(capabilities)
    
    # Description with dynamic capabilities
    supported_files = "Excel files (.xlsx, .xls)"
    if capabilities['pdf_processing']:
        supported_files += ", PDF files"
    if capabilities['ocr_available']:
        supported_files += ", Images (.png, .jpg, .jpeg, .bmp, .tiff)"
    
    # Adjust messaging based on environment
    if capabilities['is_cloud_environment']:
        ai_description = "🛠️ <strong>Manual extraction</strong> of line items (optimized for cloud environment)"
        processing_note = "<br>🏔️ <strong>Cloud Mode:</strong> Manual data processing with guided forms"
    elif capabilities['ai_available']:
        ai_description = "🤖 <strong>Uses AI</strong> to parse and structure the data intelligently"
        processing_note = ""
    else:
        ai_description = "🛠️ <strong>Manual extraction</strong> of line items (AI not configured)"
        processing_note = "<br>💡 <strong>Tip:</strong> Configure Gemini API key for AI-powered extraction"
    
    st.markdown(f"""
    <div class="info-box">
    <h3>🎯 What this tool does:</h3>
    <ul>
        <li>📄 <strong>Extracts</strong> line items from construction documents ({supported_files})</li>
        <li>{ai_description}</li>
        <li>📊 <strong>Populates</strong> your Excel template while preserving all formatting</li>
        <li>💾 <strong>Outputs</strong> professional, ready-to-use cost breakdowns</li>
    </ul>
    {processing_note}
    </div>
    """, unsafe_allow_html=True)
    
    # Setup sidebar
    api_configured = setup_api_key()
    template_path = upload_template()
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload Construction Documents")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload your construction cost documents",
            type=['pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Supported formats: PDF, Excel, Images (PNG, JPG)"
        )
        
        # Processing options
        st.subheader("⚙️ Processing Options")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            force_column_b = st.checkbox("Force amounts to Column B", value=True, 
                                       help="Always write amounts to column B regardless of template structure")
        
        with col_opt2:
            preserve_formatting = st.checkbox("Preserve template formatting", value=True,
                                            help="Maintain colors, formulas, and styling from template")
          # Process button
        if uploaded_files and template_path:
            if st.button("🚀 Process Documents", type="primary"):
                try:
                    # Check environment and API configuration
                    is_cloud = capabilities.get('is_cloud_environment', False)
                    
                    if is_cloud or not api_configured:
                        # Show message for cloud/manual mode
                        if is_cloud:
                            st.info("🏔️ **Cloud Mode:** Processing documents with manual data entry. Extracted text will be displayed for review.")
                        else:
                            st.warning("⚠️ **Manual Mode:** No AI configured. Extracted text will be displayed for manual review.")
                        
                        # Ensure automation object exists
                        if st.session_state.automation is None:
                            st.session_state.automation = ConstructionCostAutomation()
                        
                        process_documents_manual_mode(uploaded_files, template_path, st.session_state.automation)
                    else:
                        # AI mode
                        if st.session_state.automation is None:
                            st.error("❌ Automation system not initialized properly")
                            return
                        
                        process_documents(uploaded_files, template_path, st.session_state.automation)
                        
                except Exception as e:
                    st.error(f"❌ **Application Error:** {str(e)}")
                    st.error("Please check the console for detailed error information.")
                    st.info("💡 **Tip:** Try refreshing the page and uploading files one at a time.")
                    
                    # Show debug info
                    with st.expander("🔧 Debug Information"):
                        st.write(f"**Error Type:** {type(e).__name__}")
                        st.write(f"**Error Details:** {str(e)}")
                        st.write(f"**Cloud Environment:** {is_cloud}")
                        st.write(f"**API Configured:** {api_configured}")
                        st.write(f"**Automation Object:** {st.session_state.automation is not None}")
                        st.write(f"**Number of Files:** {len(uploaded_files)}")
                        st.write(f"**Template Path:** {template_path}")
                    
                    # Try to reinitialize automation
                    try:
                        st.session_state.automation = ConstructionCostAutomation()
                        st.info("🔄 Automation system reinitialized. Please try again.")
                    except Exception as init_error:
                        st.error(f"❌ Could not reinitialize automation: {init_error}")
        elif not template_path:
            st.warning("⚠️ Please upload a template first")
        elif not uploaded_files:
            st.info("📤 Upload documents to get started")
    
    with col2:
        st.header("📊 Results")
        
        if st.session_state.processed_files:
            st.success(f"✅ {len(st.session_state.processed_files)} files processed")
            
            # Download individual files
            for file_info in st.session_state.processed_files:
                file_path, original_name = file_info
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"📥 Download {os.path.basename(file_path)}",
                            data=file.read(),
                            file_name=os.path.basename(file_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            
            # Download all as ZIP
            if len(st.session_state.processed_files) > 1:
                file_paths = [f[0] for f in st.session_state.processed_files]
                zip_data = create_download_zip(file_paths)
                st.download_button(
                    label="📦 Download All (ZIP)",
                    data=zip_data,
                    file_name="construction_breakdowns.zip",
                    mime="application/zip"
                )
            
            # Clear results button
            if st.button("🗑️ Clear Results"):
                st.session_state.processed_files = []
                st.rerun()
        else:
            st.info("No files processed yet")

def process_documents(uploaded_files, template_path, automation):
    """Process multiple uploaded documents with AI"""
    processed_files = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        
        result_path, output_filename = process_single_file(uploaded_file, template_path, automation)
        
        if result_path:
            processed_files.append((result_path, uploaded_file.name))
            st.success(f"✅ Processed: {uploaded_file.name}")
        else:
            st.error(f"❌ Failed: {uploaded_file.name}")
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    status_text.text("Processing complete!")
    st.session_state.processed_files = processed_files
    
    # Summary
    success_count = len(processed_files)
    total_count = len(uploaded_files)
    
    if success_count == total_count:
        st.balloons()
        st.success(f"🎉 All {total_count} documents processed successfully!")
    else:
        st.warning(f"⚠️ {success_count}/{total_count} documents processed successfully")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ Information")
    
    capabilities = check_environment_capabilities()
    
    if capabilities['is_cloud_environment']:
        st.markdown("""
        **🏔️ Cloud Environment:**
        - PDF processing with PyPDF2
        - Excel file processing
        - Manual data entry mode
        - No AI or OCR capabilities
        
        **📋 Supported Formats:**
        - PDF documents (text-based)
        - Excel files (.xlsx, .xls)
        
        **💡 Cloud Tips:**
        - Use text-based PDFs (not scanned images)
        - Review extracted text manually
        - Enter line items and amounts manually
        """)
    else:
        st.markdown("""
        **📋 Supported Formats:**
        - PDF documents
        - Excel files (.xlsx, .xls)
        - Images (PNG, JPG, JPEG) - with OCR
        
        **🔧 Requirements:**
        - Google Gemini API key (for AI processing)
        - Excel template file
        
        **💡 Tips:**
        - Ensure documents are clear and readable
        - Use high-quality scans for images
        - Template should have proper headers
        """)
    
    st.header("🆘 Support")
    if capabilities['is_cloud_environment']:
        st.markdown("""
        **Cloud Environment Issues:**
        - Text extraction problems: Ensure PDFs contain selectable text
        - Upload failures: Check file format and size
        - Template errors: Ensure Excel template is valid
        - Manual entry: Copy text from extracted content
        
        **Note:** AI processing is not available in cloud environment
        """)
    else:
        st.markdown("""
        **Common Issues:**
        - API key errors: Check your Gemini API key
        - Upload failures: Check file format and size
        - Template errors: Ensure Excel template is valid
        
        **Contact IT Support:** [your-it-email@company.com]
        """)

if __name__ == "__main__":
    main()
