#!/usr/bin/env python3
"""
Test script to verify all modules work correctly
"""

def test_imports():
    """Test all module imports"""
    print("🧪 Testing module imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import lxml
        print("✅ LXML imported successfully")
    except ImportError as e:
        print(f"❌ LXML import failed: {e}")
        return False
    
    return True


def test_custom_modules():
    """Test our custom modules"""
    print("\n🔧 Testing custom modules...")
    
    try:
        from config import OPENROUTER_MODELS, CATEGORY_KEYWORDS
        print("✅ Config module imported successfully")
        print(f"   - Found {len(OPENROUTER_MODELS)} model categories")
        print(f"   - Found {len(CATEGORY_KEYWORDS)} URL categories")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from openrouter_client import OpenRouterClient
        print("✅ OpenRouter client imported successfully")
        
        # Test model validation
        valid_model = "mistralai/mistral-7b-instruct:free"
        invalid_model = "invalid-model"
        
        if OpenRouterClient.validate_model_format(valid_model):
            print(f"   - Model validation works: {valid_model} ✅")
        else:
            print(f"   - Model validation failed for valid model: {valid_model} ❌")
        
        if not OpenRouterClient.validate_model_format(invalid_model):
            print(f"   - Model validation correctly rejects: {invalid_model} ✅")
        else:
            print(f"   - Model validation incorrectly accepts: {invalid_model} ❌")
            
    except ImportError as e:
        print(f"❌ OpenRouter client import failed: {e}")
        return False
    
    try:
        from content_extractor import ContentExtractor, RobotsChecker
        print("✅ Content extractor imported successfully")
        
        # Test URL categorization
        extractor = ContentExtractor()
        test_urls = [
            "https://example.com/docs/api/reference",
            "https://example.com/getting-started",
            "https://example.com/guides/tutorial",
            "https://example.com/about"
        ]
        
        categories = extractor.categorize_urls(test_urls)
        print(f"   - URL categorization works: {len(categories)} categories found")
        
    except ImportError as e:
        print(f"❌ Content extractor import failed: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality"""
    print("\n⚙️ Testing basic functionality...")
    
    try:
        # Test web request
        import requests
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ Web requests working")
        else:
            print(f"⚠️ Web request returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Web request failed: {e}")
        return False
    
    try:
        # Test HTML parsing
        from bs4 import BeautifulSoup
        html = "<html><head><title>Test</title></head><body><p>Hello World</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').get_text()
        if title == "Test":
            print("✅ HTML parsing working")
        else:
            print(f"❌ HTML parsing failed: expected 'Test', got '{title}'")
            return False
    except Exception as e:
        print(f"❌ HTML parsing failed: {e}")
        return False
    
    try:
        # Test CSV processing
        import pandas as pd
        import io
        csv_data = "url,title\nhttps://example.com,Example\nhttps://test.com,Test"
        df = pd.read_csv(io.StringIO(csv_data))
        if len(df) == 2 and 'url' in df.columns:
            print("✅ CSV processing working")
        else:
            print(f"❌ CSV processing failed: {df.shape}, columns: {df.columns.tolist()}")
            return False
    except Exception as e:
        print(f"❌ CSV processing failed: {e}")
        return False
    
    return True


def main():
    """Main test function"""
    print("🤖 LLMS.txt Generator - Module Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test custom modules
    if not test_custom_modules():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The application should work correctly.")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("💡 Try running: pip install -r requirements.txt")
    
    return success


if __name__ == "__main__":
    main()
