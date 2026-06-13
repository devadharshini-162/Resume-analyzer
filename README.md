# ResumeIntel Pro 🎯

**ResumeIntel Pro** is an advanced AI-powered recruitment analytics engine built with Streamlit and Google Gemini. It automates the screening process by analyzing multiple resumes against a job description, providing deep insights into skill gaps, SWOT analysis, and ATS structural compliance.

## ✨ Key Features

-   **Multi-Resume Analysis**: Process multiple candidates simultaneously with efficient PDF text extraction and caching.
*   **Intelligent Match Ranking**: A dynamic leaderboard that ranks candidates based on their alignment score (Best/Moderate/Weak).
*   **Dual-Layer Analysis**:
    *   **Audit Hub**: Nested sub-tabs for Skills Matrix, SWOT Analysis, and Actionable AI Suggestions.
    *   **ATS Compliance**: Comprehensive structural audit (Keyword density, Quantification, Format integrity).
-   **AI Interaction Vault**: A built-in document assistant that allows you to chat with your PDFs to compare candidates or fetch specific details.
-   **Premium UI/UX**: Minimalist dark-slate aesthetic with Glassmorphism elements and Material Icons.

## 🛠️ Tech Stack

-   **Frontend**: Streamlit
-   **AI Engine**: Google Gemini (via `google-genai`)
-   **PDF Engine**: PyPDF
-   **Environment**: Python 3.9+

## 🚀 Getting Started

### Prerequisites
- Python installed on your system.
- A Google Gemini API Key.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/resume-intel-pro.git
   cd resume-intel-pro
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🛡️ ATS Optimization Logic
The system evaluates resumes based on:
- **Keyword Matching**: Identifying core technical and soft skills from the JD.
- **Quantification**: Detecting data-driven metrics in experience sections.
- **Structural Integrity**: Ensuring standard headers and machine-readable formatting.

---

Built with ❤️ by [Your Name]
