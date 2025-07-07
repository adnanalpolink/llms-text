# 🤖 LLMS.txt Generator

A comprehensive Streamlit web application that helps website owners create well-structured `llms.txt` files - a proposed standard for guiding Large Language Models (LLMs) on how to best utilize a site's content.

## ✨ Features

### Core Functionality
- **Sitemap Processing**: Automatically extract URLs from XML sitemaps (including sitemap indexes)
- **CSV Upload**: Process URLs from uploaded CSV files with intelligent column detection
- **Smart Categorization**: Automatically organize URLs into logical sections (Introduction, Guides, API Reference, etc.)
- **Parallel Processing**: Fast bulk URL processing with progress tracking

### Advanced Features
- **JavaScript Rendering**: Use Playwright for JavaScript-heavy pages (optional)
- **AI-Generated Descriptions**: Generate high-quality descriptions using OpenRouter API
- **Markdown Discovery**: Automatically find corresponding `.md` files for documentation
- **Crawler Access Check**: Verify if your robots.txt blocks LLM crawlers

### User Experience
- **Modern UI**: Clean, responsive interface with custom styling
- **Progress Tracking**: Real-time progress updates during processing
- **Error Handling**: Robust error handling with helpful messages
- **Download Support**: Easy download of generated llms.txt files

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd LLMs-File-Generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright (optional, for JavaScript rendering)**
   ```bash
   pip install playwright
   playwright install chromium
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   The app will automatically open at `http://localhost:8501`

## 📖 Usage Guide

### Basic Usage

1. **Enter Website Information** (optional)
   - Website name and description
   - If left blank, will be inferred from the first URL

2. **Choose URL Source**
   - **Sitemap URL**: Enter your XML sitemap URL
   - **CSV Upload**: Upload a CSV file with URLs

3. **Configure Enhanced Features**
   - **JavaScript Rendering**: Enable for dynamic content (requires Playwright)
   - **AI Descriptions**: Generate descriptions using LLMs (requires OpenRouter API key)

4. **Generate**: Click the generate button and wait for processing

### AI Description Setup

1. **Get OpenRouter API Key**
   - Visit [OpenRouter.ai](https://openrouter.ai)
   - Create account and get API key
   - Add credits (many models are free!)

2. **Configure in App**
   - Enter API key in the configuration section
   - Choose from free or premium models
   - Test connection before generating

### Crawler Access Check

1. **Enter Domain**: Input your domain name (e.g., `example.com`)
2. **Check Access**: See which LLM crawlers might be blocked
3. **View Results**: Get recommendations for optimization

## 🏗️ Project Structure

```
LLMs-File-Generator/
├── app.py                 # Main Streamlit application
├── content_extractor.py   # Web scraping and content processing
├── openrouter_client.py   # OpenRouter API integration
├── config.py             # Configuration and constants
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables (Optional)
- `OPENROUTER_API_KEY`: Default API key for OpenRouter
- `MAX_CONCURRENT_REQUESTS`: Maximum parallel requests (default: 10)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)

### Customization
Edit `config.py` to customize:
- Model lists and categories
- URL categorization keywords
- LLM crawler user agents
- Processing settings
- Custom CSS styling

## 📋 Requirements

### Core Dependencies
- `streamlit>=1.28.0` - Web application framework
- `requests>=2.31.0` - HTTP requests
- `beautifulsoup4>=4.12.0` - HTML parsing
- `pandas>=2.0.0` - Data processing
- `lxml>=4.9.0` - XML parsing

### Optional Dependencies
- `playwright>=1.40.0` - JavaScript rendering (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Resources

- [LLMS.txt Specification](https://llmstxt.org/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Playwright Python Documentation](https://playwright.dev/python/)

## 🐛 Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **OpenRouter API Errors**
   - Check API key validity
   - Ensure sufficient credits
   - Verify model availability

3. **Sitemap Processing Issues**
   - Verify sitemap URL accessibility
   - Check XML format validity
   - Ensure proper sitemap structure

4. **Memory Issues with Large Sites**
   - Reduce batch size in config.py
   - Process in smaller chunks
   - Consider using CSV upload for selective URLs

### Getting Help

- Check the application logs in the terminal
- Use the built-in error messages and suggestions
- Verify your input data format
- Test with a smaller dataset first

## 🎯 Roadmap

- [ ] Support for additional sitemap formats
- [ ] Bulk processing optimization
- [ ] Custom categorization rules
- [ ] Integration with more LLM providers
- [ ] Automated scheduling and updates
- [ ] Analytics and reporting features
