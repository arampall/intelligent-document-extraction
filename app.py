"""
Streamlit web application for Receipt Scanner.

This app provides a user-friendly interface for uploading receipt images
and extracting structured information using Google Gemini Vision API.
"""

import streamlit as st
import os
import tempfile
import json
import csv
from datetime import datetime
from src.doc_extractor import process_receipt_dataset

# Page configuration
st.set_page_config(
    page_title="Receipt Scanner",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .receipt-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .expense-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Header
st.title("🤖 Receipt Scanner")
st.markdown("""
Extract and categorize expense information from receipt images.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Enter your Google API key for Gemini",
        value=os.getenv('GOOGLE_API_KEY', '')
    )
    
    # Model selection
    model = st.selectbox(
        "Gemini Model",
        options=['gemini-2.0-flash-exp', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-pro'],
        help="Select the Gemini model to use for extraction"
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        sleep_time = st.slider(
            "API Rate Limit Delay (seconds)",
            min_value=0,
            max_value=10,
            value=2,
            help="Time to wait between processing multiple receipts"
        )
    
    st.divider()
    
    # Information
    st.markdown("### 📊 What We Extract")
    st.markdown("""
    - Merchant name
    - Date and time
    - Total amount
    - Individual items
    - Tax & subtotal
    - Payment method
    - Expense category
    """)

# Main content area
if not api_key:
    st.warning("⚠️ Please enter your Google API Key in the sidebar to proceed.")
else:
    # File uploader
    st.subheader("📤 Upload Receipts")
    
    uploaded_files = st.file_uploader(
        "Choose receipt image(s) or PDF(s)",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload one or more receipt images or PDFs"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} receipt(s) uploaded successfully!")
        
        # Display uploaded files with preview
        with st.expander("📁 Uploaded Receipts", expanded=True):
            cols = st.columns(min(len(uploaded_files), 4))
            for idx, uploaded_file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    # Show image preview for image files
                    if uploaded_file.type.startswith('image'):
                        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
                    else:
                        st.info(f"📄 {uploaded_file.name}")
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
        
        # Process button
        if st.button("🚀 Scan Receipts", type="primary", use_container_width=True):
            # Save uploaded files to temporary directory
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)
            
            # Process receipts
            try:
                with st.spinner("🔍 Scanning receipts... This may take a moment."):
                    # Create a progress container
                    progress_container = st.container()
                    
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("Processing receipts...")
                        
                        # Process receipts
                        results = process_receipt_dataset(
                            file_paths=file_paths,
                            api_key=api_key,
                            model=model,
                            sleep_time=sleep_time if len(file_paths) > 1 else 0
                        )
                        
                        progress_bar.progress(100)
                        status_text.success("✅ Scanning complete!")
                    
                    # Store results in session state
                    st.session_state.results = results
                    st.session_state.processing_complete = True
                
            except Exception as e:
                st.error(f"❌ Error processing receipts: {str(e)}")
                st.exception(e)
            
            finally:
                # Cleanup temporary files
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Display results
    if st.session_state.processing_complete and st.session_state.results:
        st.divider()
        st.subheader("📊 Scan Results")
        
        results = st.session_state.results
        
        # Calculate summary metrics
        total_amount = sum(
            r['extracted_info'].get('total', 0) 
            for r in results 
            if isinstance(r['extracted_info'].get('total'), (int, float))
        )
        total_receipts = len(results)
        total_tokens = sum(r['token_usage']['total'] for r in results)
        
        # Category breakdown
        categories = {}
        for r in results:
            category = r['extracted_info'].get('category', 'Other')
            amount = r['extracted_info'].get('total', 0)
            if isinstance(amount, (int, float)):
                categories[category] = categories.get(category, 0) + amount
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🧾 Receipts Scanned", total_receipts)
        
        with col2:
            st.metric("💰 Total Amount", f"${total_amount:.2f}")
        
        with col3:
            st.metric("🔢 Total Tokens", f"{total_tokens:,}")
        
        with col4:
            st.metric("📂 Categories", len(categories))
        
        # Category breakdown chart
        if categories:
            st.divider()
            st.subheader("📊 Spending by Category")
            
            import pandas as pd
            category_df = pd.DataFrame([
                {'Category': cat, 'Amount': amt} 
                for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True)
            ])
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(category_df.set_index('Category'))
            with col2:
                for _, row in category_df.iterrows():
                    st.markdown(f"**{row['Category']}**: ${row['Amount']:.2f}")
        
        st.divider()
        
        # Detailed results for each receipt
        st.subheader("📋 Receipt Details")
        
        for idx, result in enumerate(results):
            info = result['extracted_info']
            
            # Skip if there's an error
            if 'error' in info:
                st.error(f"❌ Receipt {idx + 1}: {info['error']}")
                continue
            
            with st.expander(
                f"🧾 {info.get('merchant_name', 'Unknown')} - ${info.get('total') or 0:.2f} ({info.get('date', 'N/A')})",
                expanded=(idx == 0)
            ):
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🛒 Items", "📊 Tokens", "💾 Raw JSON"])
                
                with tab1:
                    # Summary information
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🏪 Merchant Info")
                        st.markdown(f"**Name:** {info.get('merchant_name', 'N/A')}")
                        st.markdown(f"**Date:** {info.get('date', 'N/A')}")
                        st.markdown(f"**Time:** {info.get('time', 'N/A')}")
                        if info.get('address'):
                            st.markdown(f"**Address:** {info.get('address')}")
                        if info.get('phone'):
                            st.markdown(f"**Phone:** {info.get('phone')}")
                    
                    with col2:
                        st.markdown("#### 💵 Payment Info")
                        st.markdown(f"**Subtotal:** ${info.get('subtotal') or 0:.2f}")
                        st.markdown(f"**Tax:** ${info.get('tax') or 0:.2f}")
                        st.markdown(f"**Total:** ${info.get('total') or 0:.2f}")
                        st.markdown(f"**Payment:** {info.get('payment_method', 'N/A')}")
                        
                        # Category badge
                        category = info.get('category', 'Other')
                        category_colors = {
                            'Meals & Entertainment': '#FF6B6B',
                            'Travel': '#4ECDC4',
                            'Office Supplies': '#45B7D1',
                            'Transportation': '#FFA07A',
                            'Lodging': '#98D8C8',
                            'Other': '#95A5A6'
                        }
                        color = category_colors.get(category, '#95A5A6')
                        st.markdown(
                            f'<span style="background-color: {color}; color: white; '
                            f'padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.875rem; '
                            f'font-weight: 600;">{category}</span>',
                            unsafe_allow_html=True
                        )
                
                with tab2:
                    # Items list
                    items = info.get('items', [])
                    if items:
                        # Create a table
                        item_data = []
                        for item in items:
                            item_data.append({
                                'Item': item.get('name', 'N/A'),
                                'Qty': item.get('quantity', 1),
                                'Price': f"${(item.get('price') or 0):.2f}",
                                'Total': f"${(item.get('price') or 0) * (item.get('quantity') or 1):.2f}"
                            })
                        
                        st.dataframe(item_data, use_container_width=True, hide_index=True)
                    else:
                        st.info("No itemized details available")
                
                with tab3:
                    # Token usage
                    token_data = result['token_usage']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Input Tokens", f"{token_data['prompt']:,}")
                        st.metric("Output Tokens", f"{token_data['output']:,}")
                    
                    with col2:
                        thoughts = token_data.get('thoughts') or 0
                        if thoughts > 0:
                            st.metric("Thinking Tokens", f"{thoughts:,}")
                        st.metric("Total Tokens", f"{token_data['total']:,}")
                
                with tab4:
                    # Raw JSON
                    st.json(info)
        
        # Export buttons
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            download_data = {
                'timestamp': datetime.now().isoformat(),
                'model': model,
                'total_receipts': total_receipts,
                'total_amount': total_amount,
                'total_tokens': total_tokens,
                'categories': categories,
                'receipts': results
            }
            
            json_str = json.dumps(download_data, indent=2)
            
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # CSV export
            csv_data = []
            for r in results:
                info = r['extracted_info']
                if 'error' not in info:
                    csv_data.append({
                        'Date': info.get('date', ''),
                        'Merchant': info.get('merchant_name', ''),
                        'Category': info.get('category', ''),
                        'Subtotal': info.get('subtotal', 0),
                        'Tax': info.get('tax', 0),
                        'Total': info.get('total', 0),
                        'Payment Method': info.get('payment_method', ''),
                        'Receipt Number': info.get('receipt_number', '')
                    })
            
            if csv_data:
                # Convert to CSV string
                import io
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Reset button
        st.divider()
        if st.button("🔄 Scan More Receipts", use_container_width=True):
            st.session_state.results = None
            st.session_state.processing_complete = False
            st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Built with ❤️ using Streamlit & Google Gemini</p>
</div>
""", unsafe_allow_html=True)
