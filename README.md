# AI-Powered Medical Image Analysis

This is a Streamlit-based web application that uses Google Gemini AI to analyze medical images such as X-rays, MRIs, CT scans, and Ultrasounds. It generates structured diagnostic reports, patient-friendly explanations, and research-backed insights.

## Features

- Upload and analyze multiple medical images  
- Structured AI-generated reports with findings and diagnoses  
- Patient-friendly summaries and literature references  
- Export reports as TXT or PDF  
- Compare multiple analyses side by side  

## Setup

1. Clone the repository  
2. Create a `.env` file with your Gemini API key:  
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Install dependencies:  
   ```
   pip install -r requirements.txt
   ```
4. Run the app:  
   ```
   streamlit run medical.py
   ```

## License

This project is licensed under the MIT License. For educational and research use only.
