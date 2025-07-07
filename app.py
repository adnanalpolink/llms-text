"""
LLMS.txt Generator - Streamlit Web Application
A tool to help website owners create well-structured llms.txt files
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from typing import Dict, List, Optional

# Import our custom modules
from content_extractor import ContentExtractor, RobotsChecker
from openrouter_client import OpenRouterClient
from config import (
    OPENROUTER_MODELS, LLM_CRAWLERS, CUSTOM_CSS,
    MAX_CONCURRENT_REQUESTS, BATCH_SIZE
)


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="LLMS.txt Generator",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.markdown("## 🤖 LLMS.txt Generator")
        st.markdown("---")
        
        # New Features Section
        with st.expander("✨ New Features", expanded=True):
            st.markdown("""
            - **JavaScript Rendering**: Use Playwright for dynamic content
            - **AI Descriptions**: Generate descriptions using LLMs
            - **Parallel Processing**: Fast bulk URL processing
            - **Smart Categorization**: Automatic content organization
            - **Markdown Discovery**: Find corresponding .md files
            """)
        
        # Benefits Section
        with st.expander("📈 Benefits of llms.txt"):
            st.markdown("""
            - **Better AI Understanding**: Help LLMs comprehend your site structure
            - **Improved Responses**: More accurate AI-generated content about your site
            - **SEO Benefits**: Better content discovery and indexing
            - **Standardization**: Follow emerging web standards
            - **Control**: Guide how AI systems interact with your content
            """)
        
        # Setup Guide
        with st.expander("🔧 OpenRouter API Setup"):
            st.markdown("""
            1. Visit [OpenRouter.ai](https://openrouter.ai)
            2. Create an account and get your API key
            3. Add credits to your account (many models are free!)
            4. Paste your API key in the configuration section
            5. Select your preferred model
            """)
        
        # Resources
        with st.expander("🔗 Resources"):
            st.markdown("""
            - [LLMS.txt Specification](https://llmstxt.org/)
            - [OpenRouter Models](https://openrouter.ai/models)
            - [Playwright Documentation](https://playwright.dev/python/)
            - [Sitemap Protocol](https://www.sitemaps.org/protocol.html)
            """)


def render_about_section():
    """Render the about section"""
    with st.expander("ℹ️ About LLMS.txt", expanded=False):
        st.markdown("""
        **LLMS.txt** is a proposed standard that helps website owners provide structured information 
        about their site's content to Large Language Models (LLMs). Similar to robots.txt for web crawlers, 
        llms.txt guides AI systems on how to best understand and utilize your website's content.
        
        **Key Benefits:**
        - Helps LLMs provide more accurate information about your site
        - Improves AI-generated summaries and responses
        - Gives you control over how AI systems interpret your content
        - Follows emerging web standards for AI interaction
        
        **File Structure:**
        The llms.txt file contains your site name, description, and categorized links to important pages 
        with brief descriptions of each page's content.
        """)


def render_generate_tab():
    """Render the main generation tab"""
    st.header("📄 Generate LLMS.txt File")
    
    # Website Information
    col1, col2 = st.columns(2)
    with col1:
        website_name = st.text_input(
            "Website Name (optional)",
            placeholder="My Awesome Website",
            help="Leave blank to infer from the first URL"
        )
    
    with col2:
        website_description = st.text_input(
            "Website Description (optional)",
            placeholder="A comprehensive resource for...",
            help="Leave blank to infer from the first URL"
        )
    
    # URL Source Selection
    st.subheader("📋 URL Source")
    url_source = st.radio(
        "Choose your URL source:",
        ["Sitemap URL", "CSV Upload"],
        horizontal=True
    )
    
    urls = []
    if url_source == "Sitemap URL":
        sitemap_url = st.text_input(
            "Sitemap URL",
            placeholder="https://example.com/sitemap.xml",
            help="URL to your XML sitemap"
        )
        if sitemap_url:
            urls = [sitemap_url]
    else:
        uploaded_file = st.file_uploader(
            "Upload CSV file with URLs",
            type=['csv'],
            help="CSV file should contain URLs in a column named 'url' or in the first column"
        )
        if uploaded_file:
            urls = [uploaded_file]
    
    # Enhanced Features
    st.subheader("🚀 Enhanced Features")
    
    col1, col2 = st.columns(2)
    with col1:
        use_js_rendering = st.checkbox(
            "Use Playwright for JavaScript-heavy pages",
            help="Slower but more accurate for dynamic content. Requires: pip install playwright"
        )
    
    with col2:
        use_ai_descriptions = st.checkbox(
            "Generate descriptions using AI",
            help="Uses OpenRouter API to generate high-quality descriptions"
        )
    
    # AI Configuration (shown when AI descriptions is enabled)
    ai_client = None
    if use_ai_descriptions:
        st.subheader("🤖 LLM Configuration")
        
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get your API key from https://openrouter.ai"
        )
        
        # Model Selection
        col1, col2 = st.columns([2, 1])
        with col1:
            model_category = st.selectbox(
                "Model Category",
                ["Free Models", "Premium Models", "Custom Model"]
            )
        
        with col2:
            if model_category != "Custom Model":
                selected_model = st.selectbox(
                    "Select Model",
                    OPENROUTER_MODELS[model_category]
                )
            else:
                selected_model = st.text_input(
                    "Custom Model",
                    placeholder="provider/model-name",
                    help="Format: provider/model-name (e.g., mistralai/mistral-7b-instruct)"
                )
                
                if selected_model and not OpenRouterClient.validate_model_format(selected_model):
                    st.error("Invalid model format. Use: provider/model-name")
                    selected_model = None
        
        # Initialize AI client if we have valid credentials
        if api_key and selected_model:
            ai_client = OpenRouterClient(api_key, selected_model)
            
            # Test connection button
            if st.button("🔍 Test API Connection"):
                with st.spinner("Testing connection..."):
                    success, message = ai_client.test_connection()
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
    
    # Generate Button
    if st.button("🚀 Generate LLMS.txt", type="primary", use_container_width=True):
        if not urls:
            st.error("Please provide a sitemap URL or upload a CSV file.")
            return
        
        generate_llms_txt(
            urls, url_source, website_name, website_description,
            use_js_rendering, ai_client
        )


def generate_llms_txt(urls, url_source, website_name, website_description,
                     use_js_rendering, ai_client):
    """Generate the llms.txt file content"""

    # Initialize content extractor
    extractor = ContentExtractor(use_js_rendering=use_js_rendering)

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Extract URLs
        status_text.text("🔍 Extracting URLs...")

        if url_source == "Sitemap URL":
            sitemap_url = urls[0]
            extracted_urls = extractor.extract_urls_from_sitemap(sitemap_url)
        else:
            csv_file = urls[0]
            extracted_urls = extractor.extract_urls_from_csv(csv_file)

        if not extracted_urls:
            st.error("No URLs found. Please check your sitemap or CSV file.")
            return

        st.success(f"✅ Found {len(extracted_urls)} URLs")
        progress_bar.progress(0.2)

        # Step 2: Process URLs
        status_text.text("⚙️ Processing URLs...")

        def progress_callback(message, progress=None):
            status_text.text(message)
            if progress:
                progress_bar.progress(0.2 + (progress * 0.7))

        processed_results = extractor.process_urls_parallel(
            extracted_urls, ai_client, progress_callback
        )

        progress_bar.progress(0.9)

        # Step 3: Infer website info if not provided
        if not website_name or not website_description:
            status_text.text("🔍 Inferring website information...")

            # Use first URL to get site info
            first_url = extracted_urls[0]
            soup = extractor.fetch_page_content(first_url)

            if soup and not website_name:
                title_tag = soup.find('title')
                if title_tag:
                    website_name = title_tag.get_text().strip()

            if soup and not website_description:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    website_description = meta_desc['content'].strip()

        # Step 4: Generate llms.txt content
        status_text.text("📝 Generating llms.txt content...")

        llms_content = build_llms_txt_content(
            website_name or "Website",
            website_description or "A comprehensive resource",
            processed_results,
            use_js_rendering,
            bool(ai_client)
        )

        progress_bar.progress(1.0)
        status_text.text("✅ Generation complete!")

        # Display results
        display_results(llms_content, len(extracted_urls))

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)


def build_llms_txt_content(site_name: str, site_description: str,
                          categorized_results: Dict, use_js: bool, use_ai: bool) -> str:
    """Build the final llms.txt content"""

    content_lines = []

    # Header
    content_lines.append(f"# {site_name}")
    content_lines.append("")
    content_lines.append(f"> {site_description}")
    content_lines.append("")

    # Process each category
    for category, results in categorized_results.items():
        if not results:
            continue

        content_lines.append(f"## {category}")
        content_lines.append("")

        for result in results:
            title = result.get('title', 'Page')
            url = result.get('url', '')
            description = result.get('description', 'Resource information')
            md_link = result.get('md_link')

            # Build the line
            line = f"- [{title}]({url}): {description}"

            # Add markdown link if available
            if md_link:
                filename = md_link.split('/')[-1]
                line += f" ([{filename}]({md_link}))"

            content_lines.append(line)

        content_lines.append("")

    # Footer with generation info
    features_used = []
    if use_js:
        features_used.append("JavaScript Rendering")
    if use_ai:
        features_used.append("AI Descriptions")

    features_str = ", ".join(features_used) if features_used else "Standard Processing"
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content_lines.append("<!-- Generated by LLMS.txt Generator -->")
    content_lines.append(f"<!-- Date: {generation_date} -->")
    content_lines.append(f"<!-- Features: {features_str} -->")

    return "\n".join(content_lines)


def display_results(llms_content: str, total_urls: int):
    """Display the generated results"""

    st.success(f"🎉 Successfully processed {total_urls} URLs!")

    # Display content in text area
    st.subheader("📄 Generated LLMS.txt Content")
    st.text_area(
        "Your llms.txt file content:",
        value=llms_content,
        height=400,
        help="Copy this content or use the download button below"
    )

    # Download button
    st.download_button(
        label="📥 Download llms.txt",
        data=llms_content,
        file_name="llms.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total URLs", total_urls)
    with col2:
        lines = len(llms_content.split('\n'))
        st.metric("File Lines", lines)
    with col3:
        chars = len(llms_content)
        st.metric("File Size", f"{chars} chars")


def render_crawler_check_tab():
    """Render the crawler access check tab"""
    st.header("🔍 Check Crawler Access")

    st.markdown("""
    Check if your website's robots.txt file blocks common LLM crawlers.
    This helps you understand which AI systems can access your content.
    """)

    domain = st.text_input(
        "Domain Name",
        placeholder="example.com",
        help="Enter your domain without https:// or www."
    )

    if st.button("🔍 Check Crawler Access", use_container_width=True):
        if not domain:
            st.error("Please enter a domain name.")
            return

        # Clean domain input
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "").strip("/")

        with st.spinner("Checking robots.txt..."):
            result = RobotsChecker.check_crawler_access(domain, LLM_CRAWLERS)

        # Display results
        if result['error']:
            st.warning(f"⚠️ {result['error']}")
            if result['error'] == "No robots.txt file found":
                st.info("✅ No robots.txt means crawlers are generally allowed!")
        else:
            if result['accessible']:
                st.success("✅ Your site appears to be accessible to LLM crawlers!")
                st.balloons()
            else:
                st.warning("⚠️ Some LLM crawlers may be blocked:")
                for crawler in result['blocked_crawlers']:
                    st.write(f"- {crawler}")

        # Show robots.txt content if available
        if result['robots_content']:
            with st.expander("📄 View robots.txt content"):
                st.code(result['robots_content'], language="text")

        # Recommendations
        if result['blocked_crawlers']:
            st.subheader("💡 Recommendations")
            st.markdown("""
            If you want to allow LLM crawlers:
            1. Remove or modify the `Disallow: /` rules for specific crawlers
            2. Consider allowing beneficial crawlers while blocking others
            3. Use more specific disallow rules instead of blanket blocks
            4. Test your changes with this tool
            """)


def main():
    """Main application function"""
    setup_page_config()
    render_sidebar()

    # Main title
    st.markdown("""
    <div class="main-header">
        <h1>🤖 LLMS.txt Generator</h1>
        <p>Create well-structured llms.txt files to guide AI systems</p>
    </div>
    """, unsafe_allow_html=True)

    # About section
    render_about_section()

    # Main tabs
    tab1, tab2 = st.tabs(["📄 Generate LLMS.txt", "🔍 Check Crawler Access"])

    with tab1:
        render_generate_tab()

    with tab2:
        render_crawler_check_tab()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Made with ❤️ using Streamlit |
        <a href="https://llmstxt.org/" target="_blank">Learn more about LLMS.txt</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
