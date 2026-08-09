# Agri-RAG: Intelligent Agriculture Assistant Documentation

## 📋 Project Overview

**Agri-RAG** is an advanced Retrieval-Augmented Generation (RAG) system designed specifically for agricultural applications. The project combines computer vision, natural language processing, and specialized agricultural knowledge to help farmers and agricultural professionals diagnose plant diseases and access solutions.

The system uses a multimodal approach that can:
- Detect leaf diseases through image analysis
- Provide treatment recommendations
- Answer agricultural questions using a knowledge base
- Search for soil-related information

## 🏗️ Project Structure

```
agri/
├── data/
│   └── raw/                    # Raw data storage for the RAG system
├── src/                        # Main source code
│   └── (multimodal testing setup)
├── tests/                      # Test files
├── .gitignore                  # Git ignore configuration
├── image.png                   # Sample image for testing
├── requirements.txt            # Python dependencies
└── yolov8n.pt                  # YOLOv8 model weights for object detection
```

## 🔧 Core Technologies

### 1. **Computer Vision with YOLOv8**
- Uses YOLOv8n (nano version) for efficient object detection
- Model weights (`yolov8n.pt`) are included for plant disease detection
- Capable of analyzing leaf images to identify disease symptoms

### 2. **Multimodal RAG System**
- Combines text and image processing capabilities
- Retrieves relevant agricultural information from a knowledge base
- Generates context-aware responses for agricultural queries

### 3. **Specialized Tools**
- **Soil Search Tool**: Dedicated functionality for soil-related queries
- **Photo Analyzer**: Initial leaf image analysis pipeline

## 🚀 Features

### 1. **Leaf Disease Detection**
- Upload leaf images for automatic disease detection
- Uses YOLOv8 for identifying disease symptoms
- Provides visual analysis results

### 2. **Solution Recommendations**
- Disease-specific treatment suggestions
- Context-aware responses using RAG
- Agricultural best practices

### 3. **Soil Information System**
- `soil_search` tool for soil-related queries
- Integration with agricultural databases
- Soil health recommendations

### 4. **Conversational Interface**
- Setup for streaming chat responses
- Interactive query handling
- Real-time information retrieval

## 🛠️ Setup Instructions

### Prerequisites
```bash
Python 3.8+
pip package manager
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/taha203040/agri.git
cd agri
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify YOLOv8 model**
```bash
# Ensure yolov8n.pt is present in the root directory
ls -la yolov8n.pt
```

## 📁 Component Details

### `src/` Directory
- Contains core implementation files
- Multimodal testing setup (added May 17, 2026)
- Likely includes:
  - RAG pipeline implementation
  - Image processing modules
  - Query handling logic

### `data/raw/`
- Stores raw agricultural data
- Used for the RAG system's knowledge base
- May include:
  - Disease descriptions
  - Treatment protocols
  - Soil information
  - Crop data

### `tests/`
- Test suites for the application
- Ensures multimodal functionality works correctly

## 🔄 Development Timeline

| Date | Update |
|------|--------|
| Apr 30, 2026 | Initial photo analyzer setup |
| May 7, 2026 | Stream chat response implementation |
| May 16, 2026 | Image ignore configuration |
| May 17, 2026 | Multimodal testing setup |
| May 18, 2026 | Folder cleanup |
| Feb 9, 2026 | Soil search tool addition |

## 💻 Usage Examples

### 1. **Disease Detection**
```python
# Upload leaf image for analysis
response = agri.analyze_leaf("path/to/leaf_image.jpg")
print(f"Disease detected: {response['disease']}")
print(f"Confidence: {response['confidence']}")
print(f"Recommendation: {response['solution']}")
```

### 2. **Query Processing**
```python
# Ask agricultural questions
query = "What are the symptoms of tomato blight?"
answer = agri.query(query)
print(answer)
```

### 3. **Soil Information**
```python
# Search for soil information
soil_info = agri.soil_search("pH level for rice cultivation")
print(soil_info)
```

## 📊 Dependencies (requirements.txt)

Key libraries likely include:
- **Ultralytics YOLOv8** - Object detection
- **Transformers** - NLP capabilities
- **LangChain** - RAG framework
- **FAISS** - Vector database
- **Streamlit** - Web interface (for chat)
- **OpenCV** - Image processing
- **PyTorch** - Deep learning framework

## 🔮 Future Enhancements

1. **Expanded Disease Database** - More crop diseases and treatments
2. **Real-time Monitoring** - Continuous field monitoring capabilities
3. **Multi-language Support** - Reaching more farming communities
4. **Mobile Application** - On-field accessibility
5. **Weather Integration** - Weather-based disease prediction

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact the maintainer: taha203040



**Note**: This project is under active development. Features and capabilities are continuously being improved based on agricultural needs and technological advancements.
