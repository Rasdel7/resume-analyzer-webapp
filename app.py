import streamlit as st
import PyPDF2
import io
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and get instant AI-powered "
            "feedback, scoring and improvement suggestions.")
st.markdown("---")

# Extract text from PDF
def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text   = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Analyze with Claude API
def analyze_resume(text, job_role):
    import anthropic
    client = anthropic.Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"]
    )

    prompt = f"""You are an expert resume reviewer and career coach 
with 20 years of experience hiring for top tech companies.

Analyze this resume for a {job_role} position and provide:

1. OVERALL SCORE (out of 100)
2. SECTION SCORES:
   - Contact Info (out of 10)
   - Summary/Objective (out of 10)
   - Skills (out of 20)
   - Experience (out of 25)
   - Education (out of 15)
   - Projects (out of 20)

3. TOP 5 STRENGTHS (what's working well)

4. TOP 5 WEAKNESSES (critical issues to fix)

5. TOP 5 SPECIFIC IMPROVEMENTS (exact changes to make)

6. ATS SCORE (out of 100) — how well it will pass 
   Applicant Tracking Systems

7. MISSING KEYWORDS for {job_role} role

8. ONE LINER VERDICT (brutally honest, one sentence)

Format your response with clear headers using ### 
Be specific, actionable and brutally honest.
Don't be generic — reference actual content from the resume.

RESUME:
{text[:4000]}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# Sidebar
st.sidebar.header("⚙️ Settings")
job_role = st.sidebar.selectbox(
    "Target Job Role:",
    [
        "Data Science Intern",
        "ML Engineer",
        "Software Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Data Analyst",
        "AI/ML Research Intern",
        "DevOps Engineer",
        "Cybersecurity Analyst"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips for Best Results")
st.sidebar.info("""
- Upload a text-based PDF
- Scanned PDFs may not work well
- Keep resume under 2 pages
- Make sure text is selectable
""")

# Main area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Your Resume")
    uploaded = st.file_uploader(
        "Upload PDF resume:",
        type=['pdf']
    )

    if uploaded:
        st.success("✅ Resume uploaded successfully!")

        # Extract text
        with st.spinner("Extracting text..."):
            text = extract_text(uploaded)

        if len(text) < 100:
            st.error("Could not extract text. "
                     "Make sure your PDF has selectable text.")
        else:
            st.markdown("### 📝 Extracted Text Preview")
            with st.expander("Click to see extracted text"):
                st.text(text[:2000] + "..." 
                        if len(text) > 2000 else text)

            word_count = len(text.split())
            char_count = len(text)
            c1, c2 = st.columns(2)
            c1.metric("Word Count", f"{word_count:,}")
            c2.metric("Characters", f"{char_count:,}")

with col2:
    st.markdown("### 🤖 AI Analysis")

    if uploaded and len(text) >= 100:
        if st.button("🔍 Analyze My Resume",
                     type="primary",
                     use_container_width=True):
            with st.spinner("AI is analyzing your resume... "
                           "This takes 10-15 seconds."):
                try:
                    analysis = analyze_resume(text, job_role)
                    st.markdown("---")
                    st.markdown(analysis)

                    # Download analysis
                    st.download_button(
                        "⬇️ Download Analysis",
                        analysis,
                        "resume_analysis.txt",
                        "text/plain"
                    )
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.info("Make sure your API key is "
                            "set in Streamlit secrets.")
    else:
        st.info("👈 Upload your resume to get started.")

st.markdown("---")

# Sample analysis section
st.markdown("### 📊 What The Analysis Covers")
cols = st.columns(4)
items = [
    ("🎯", "Overall Score", "Out of 100"),
    ("📋", "Section Scores", "6 categories rated"),
    ("💪", "Strengths", "What's working"),
    ("⚠️", "Weaknesses", "What to fix"),
    ("✏️", "Improvements", "Exact changes"),
    ("🤖", "ATS Score", "Beat the bots"),
    ("🔑", "Keywords", "Missing terms"),
    ("💬", "Verdict", "Honest feedback")
]
for i, (emoji, title, desc) in enumerate(items):
    cols[i % 4].markdown(
        f"**{emoji} {title}**\n\n{desc}")

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Powered by Claude AI | "
    "Your resume data is never stored"
)