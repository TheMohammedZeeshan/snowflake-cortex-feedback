-- Create a database to store customer feedback
CREATE DATABASE CUSTOMER_FEEDBACK;

-- Create a schema within the customer feedback database
CREATE SCHEMA CUSTOMER_FEEDBACK.APP_FEEDBACK;

-- Enable Cortex cross-region support for AWS US region
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_US';

-- Create a masking policy to hide usernames from non-admin roles
CREATE OR REPLACE MASKING POLICY user_mask AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN') THEN '******'
    ELSE val
  END;

-- Preview 10 records from the reviews table
SELECT *
FROM CUSTOMER_FEEDBACK.APP_FEEDBACK."google_play_reviews"
LIMIT 10;

-- Analyze negative sentiment reviews and classify them into categories using Cortex
SELECT 
  "username",
  "review", 
  SNOWFLAKE.CORTEX.SENTIMENT("review") AS sentiment_score,
  SNOWFLAKE.CORTEX.CLASSIFY_TEXT("review", [
    'OTP', 'ACCOUNT BLOCKED', 'LOGIN', 'INSTALLATION', 'UPDATE', 'UI',
    'NOTIFICATIONS', 'MEDIA', 'FEATURE REQUEST', 'AI', 'SPAM/MISUSE',
    'BUGS/CRASH', 'RESTORE', 'LANGUAGE', 'APP STORE ISSUE',
    'CUSTOMIZATION', 'DOWNLOAD', 'ACCOUNT RECOVERY', 'SUPPORT',
    'VOICE CHAT', 'SECURITY'
  ]):label::STRING AS CLASSIFY_TEXT_COL
FROM CUSTOMER_FEEDBACK.APP_FEEDBACK."google_play_reviews"
WHERE SNOWFLAKE.CORTEX.SENTIMENT("review") < 0;
