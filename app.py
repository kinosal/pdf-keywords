"""Streamlit app to analyze pdf files with keywords."""

# Import from 3rd party libraries
import streamlit as st
import pdftotext

# Page start

st.set_page_config(page_title="PDF Keywords")

st.title("Count keywords in pdf files")

presets = {
    "Product Data Analyst": {
        "keywords": "product,data,analy,sql,python,numpy,pandas,visual,stat,hypoth,test,experiment,math,science,athena,s3,regress,classif,intel,machine,learn,sagemaker,copenhagen",
        "priority": "sql,python,pandas",
    },
    "Data Engineer": {
        "keywords": "data,engineer,product,lake,warehouse,pipeline,machine,learn,architect,process,stat,aws,python,spark,kafka,cassandra,druid,snowflake,redshift,s3,athena,airflow,etl,elt,sagemaker,copenhagen",
        "priority": "kafka,cassandra,druid",
    }
}

preset = st.selectbox("Select a keyword preset", presets.keys())

keywords = st.text_input(
    label="Enter comma-separated keywords", value=presets[preset]["keywords"]
)

priority = st.multiselect(
    label="Select the most important keywords to receive more weight",
    options=keywords.split(","),
    default=[
        word for word in presets[preset]["priority"].split(",")
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
        pdf = pdftotext.PDF(file)
        text = "\n\n".join(pdf).lower()

        counts = []
        total = 0
        weighted = 0
        unique = 0
        for word in keywords.split(","):
            count = text.count(word.lower())
            counts.append({
                "keyword": word,
                "count": count,
                "%": count / len(text.split(" ")),
            })
            total += count
            weighted += factor * count if word in priority else count
            unique += 1 if count > 0 else 0

        ratio = total / len(text.split(" "))
        analysis.append({
            "file": file.name,
            "counts": counts,
            "total": total,
            "ratio": ratio,
            "weighted": weighted,
            "unique": unique,
            "score": 2 * unique + weighted + int(400 * ratio),
        })

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
