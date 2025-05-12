# snowflake-cortex-feedback
AI-powered dashboard for analyzing Google Play reviews using Snowflake Cortex &amp; Streamlit

⭐ If this helped you, give the repo a star! and buy me a coffee  https://buymeacoffee.com/reach2zeeshan


# 🧠 Customer Feedback Analyzer with Snowflake Cortex AI + Streamlit

![image](https://github.com/user-attachments/assets/cbb37d84-361b-41db-9f90-78d6a0f4659a)
![image](https://github.com/user-attachments/assets/6d25292b-7062-4076-af71-5b7981094729)
![image](https://github.com/user-attachments/assets/1ab7cf14-a80c-493b-a5f2-4e891a1105d9)
![image](https://github.com/user-attachments/assets/d7cdd1d7-9438-4eee-8314-18b0197da848)
![image](https://github.com/user-attachments/assets/651f9644-f852-4d8b-9d17-f1de195deea3)



A simple, AI-powered feedback analyzer that lets you extract Google Play Store reviews, classify them by theme, analyze sentiment, and visualize it all with rich interactive charts — **using only Snowflake + Streamlit**.

---

## 🚀 Features

- 🔍 Extract reviews from Google Play (WhatsApp by default)
- 🧠 Use **Snowflake Cortex AI** to:
  - Detect **sentiment** (positive, neutral, negative)
  - Classify text into 10+ categories (e.g., OTP, LOGIN, BUGS)
- 📊 Streamlit dashboard includes:
  - Bubble Matrix – Key Drivers
  - Treemap – Themes by Action
  - Heatmap – Sentiment Zones
  - Donut Chart – Overall Mood
- ✅ Built entirely inside the **Snowflake Data Cloud** using Snowpark & Cortex


---

## 📁 Project Structure

```bash
├── setup/                  # Snowflake SQL scripts
│   └── snowflake_schema.sql
├── data_ingestion/        # Python: extract reviews + upload to Snowflake
│   └── extract_reviews.py
├── app/                   # Streamlit app (run from Snowflake)
│   └── streamlit_dashboard.py
├── requirements.txt       # Python dependencies
├── .env.template          # Sample secrets file (DO NOT COMMIT .env)
