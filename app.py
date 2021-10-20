"""Streamlit app to analyze pdf files with keywords."""

# Import from standard library
from typing import List, Dict

# Import from 3rd party libraries
import streamlit as st
import pdftotext


# Define global functions and variables
def analyze_pdf(
    file: st.uploaded_file_manager.UploadedFile,
    keywords: List[str],
    priority: List[str],
    factor: int,
) -> Dict:
    """Analyze keywords in pdf files.
    Args:
        file: pdf file uploaded with streamlit
        keywords: list with keywords to count
        priority: list with keywords to weigh more
        factor: factor by which to increase priority weight
    Returns:
        dict with keyword analytics
    """
    pdf = pdftotext.PDF(file)
    text = "\n\n".join(pdf).lower()
    n_words = len(text.split(" "))

    counts = []
    total, weighted, unique = 0, 0, 0
    for word in keywords:
        count = text.count(word.lower())
        counts.append({
            "keyword": word, "count": count, "%": count / n_words
        })
        total += count
        weighted += factor * count if word in priority else count
        unique += 1 if count > 0 else 0

    return {
        "file": file.name,
        "counts": counts,
        "total": total,
        "ratio": total / n_words,
        "weighted": weighted,
        "unique": unique,
        "score": 2 * unique + weighted + int(400 * total / n_words),
    }


# Keywords to include for all presets
GENERAL_PRESETS = {
    "keywords": [
        "data",
        "product",
        "scien",
        "python",
        "stat",
        "math",
        "aws",
        "s3",
        "athena",
        "copenhagen",
    ]
}


# Keywords to include for specific presets
SPECIFIC_PRESETS = {
    "Data Analyst": {
        "keywords": [
            "analy",
            "descri",
            "predict",
            "prescri",
            "sql",
            "numpy",
            "pandas",
            "visual",
            "hypoth",
            "test",
            "experiment",
            "regress",
            "classif",
            "intel",
        ],
        "priority": ["sql", "python", "pandas"],
    },
    "Data Engineer": {
        "keywords": [
            "engineer",
            "machine",
            "learn",
            "lake",
            "warehouse",
            "pipeline",
            "architect",
            "process",
            "spark",
            "kafka",
            "cassandra",
            "druid",
            "snowflake",
            "redshift",
            "airflow",
            "etl",
            "elt",
        ],
        "priority": ["kafka", "cassandra", "druid"],
    },
    "Data Scientist": {
        "keywords": [
            "machine",
            "learn",
            "descri",
            "predict",
            "prescri",
            "process",
            "model",
            "infer",
            "sagemaker",
            "pytorch",
            "tensorflow",
            "scikit",
            "regress",
            "classif",
            "bayes",
            "frequen",
        ],
        "priority": ["learn", "model"],
    },
}


# Render streamlit page
st.set_page_config(page_title="PDF Keywords")

st.title("Count keywords in pdf files")

preset = st.selectbox("Select a keyword preset", SPECIFIC_PRESETS.keys())

keywords = st.text_input(
    label="Enter comma-separated keywords",
    value=", ".join(
        GENERAL_PRESETS["keywords"] + SPECIFIC_PRESETS[preset]["keywords"]
    )
)

priority = st.multiselect(
    label="Select the most important keywords to receive more weight",
    options=keywords.split(", "),
    default=[
        word for word in SPECIFIC_PRESETS[preset]["priority"]
        if word in keywords
    ],
)

factor = st.number_input(label="Enter the weight factor", value=2)

files = st.file_uploader(
    "Choose one or multiple pdf files", type="pdf", accept_multiple_files=True
)

if files and keywords:
    analysis = []
    for file in files:
        analysis.append(
            analyze_pdf(file, keywords.split(", "), priority, factor)
        )

    st.markdown("""---""")
    st.subheader("Summary")
    st.write("score = 2 unique + weighted + int(400 ratio)")
    st.table(
        data=sorted([
            {k: v for k, v in d.items() if k != "counts"} for d in analysis
        ], key=lambda x: x["score"], reverse=True)
    )

    for file in analysis:
        st.markdown("""---""")
        st.subheader(file["file"])
        st.table(
            data=sorted(file["counts"], key=lambda x: x["count"], reverse=True)
        )
        st.write(f"""
            Total keyword count: {file['total']} (ratio: {file['ratio'] * 100:.2f}%)\n
            Weighted keyword count: {file['weighted']}\n
            Unique keyword count: {file['unique']}\n
            Score (2 unique + weighted + int(400 ratio)):
            {2 * file['unique'] + file['weighted'] + int(400 * file['ratio'])}
        """)
