import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["login_anomaly_db"]
collection = db["logins"]

st.title("🔐 Login Anomaly Detection System with MongoDB")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])


def detect_anomaly(row):
    if (
        row["ip_risk"] > 0.7 or
        row["failed_attempts"] > 3 or
        row["device_change"] == 1 or
        row["hour"] < 5 or row["hour"] > 22
    ):
        return "Anomaly"
    else:
        return "Normal"


def insert_data(df):
    records = df.to_dict(orient="records")
    collection.insert_many(records)


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Uploaded Data")
    st.write(df)

    # Apply detection
    df["Result"] = df.apply(detect_anomaly, axis=1)

    st.subheader("🔍 Detection Results")
    st.write(df)

    # Store in MongoDB
    insert_data(df)
    st.success("✅ Data stored in MongoDB!")

    # Summary
    anomaly_count = (df["Result"] == "Anomaly").sum()
    normal_count = (df["Result"] == "Normal").sum()

    st.subheader("📈 Summary")
    st.write(f"Anomalies: {anomaly_count}")
    st.write(f"Normal: {normal_count}")


# Show stored data
if st.button("📂 Show Stored Records"):
    data = list(collection.find({}, {"_id": 0}))
    df_db = pd.DataFrame(data)

    st.subheader("📁 MongoDB Records")
    st.write(df_db)
    