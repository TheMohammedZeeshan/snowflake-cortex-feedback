from google_play_scraper import reviews
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# STEP 1: Google Play review extraction
app_id = "com.whatsapp"
result, _ = reviews(
    app_id,
    lang='en',
    country='us',
    count=200,
    filter_score_with=None
)

df = pd.DataFrame(result)[['userName', 'score', 'content', 'at']]
df.columns = ['username', 'rating', 'review', 'date']

# STEP 2: Snowflake connection setup
connection_parameters = {
    "account": "PASTE_HERE",          # e.g. abcd-xy12345
    "user": "PASTE_HERE",
    "password": "PASTE_HERE",
    "role": "ACCOUNTADMIN",                # Optional
    "warehouse": "COMPUTE_WH",
    "database": "CUSTOMER_FEEDBACK",
    "schema": "APP_FEEDBACK"
}

session = Session.builder.configs(connection_parameters).create()

# STEP 3: Create table (if not exists)
session.sql("""
    CREATE TABLE IF NOT EXISTS CUSTOMER_FEEDBACK.APP_FEEDBACK.google_play_reviews (
        username STRING,
        rating INT,
        review STRING,
        date TIMESTAMP_NTZ
    )
""").collect()

# STEP 4: Write DataFrame to Snowflake
session.write_pandas(df, "google_play_reviews", auto_create_table=False, overwrite=True)

print("✅ Successfully sent 200 reviews to Snowflake table 'google_play_reviews'")
