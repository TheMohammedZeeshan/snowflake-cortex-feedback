import streamlit as st
import pandas as pd
import plotly.express as px
from snowflake.snowpark.context import get_active_session

# Page config
st.set_page_config(layout="wide")
session = get_active_session()

# Load data (ratings + reviews)
df = session.sql("""
    SELECT 
        "username",
        "rating",
        "review",
        SNOWFLAKE.CORTEX.SENTIMENT("review") AS sentiment_score,
        SNOWFLAKE.CORTEX.CLASSIFY_TEXT("review", [
            'OTP', 'ACCOUNT BLOCKED', 'LOGIN', 'INSTALLATION', 'UPDATE', 'UI',
            'NOTIFICATIONS', 'MEDIA', 'FEATURE REQUEST', 'AI', 'SPAM/MISUSE',
            'BUGS/CRASH', 'RESTORE', 'LANGUAGE', 'APP STORE ISSUE',
            'CUSTOMIZATION', 'DOWNLOAD', 'ACCOUNT RECOVERY', 'SUPPORT',
            'VOICE CHAT', 'SECURITY'
        ]):label::STRING AS classify_text_col
    FROM CUSTOMER_FEEDBACK.APP_FEEDBACK."google_play_reviews"
    WHERE "rating" IS NOT NULL AND "review" IS NOT NULL AND SNOWFLAKE.CORTEX.SENTIMENT("review") IS NOT NULL
""").to_pandas()

# Prep
df.columns = df.columns.str.lower()
df = df[df['classify_text_col'].notnull()]
df = df[df['sentiment_score'].between(-1, 1)]
df['satisfaction'] = df['sentiment_score']
df['significance'] = df['sentiment_score'].abs()
df['volume'] = 1

def assign_action(row):
    if row['satisfaction'] < 0 and row['significance'] >= 0.5:
        return 'Address Immediately'
    elif row['satisfaction'] > 0 and row['significance'] >= 0.5:
        return 'Maintain & Monitor'
    elif row['significance'] < 0.5 and row['satisfaction'] < 0:
        return 'Minimize & Reassess'
    else:
        return 'Explore'

df['action'] = df.apply(assign_action, axis=1)

agg = df.groupby('classify_text_col').agg({
    'satisfaction': 'mean',
    'significance': 'mean',
    'volume': 'count',
    'action': 'first'
}).reset_index()

# Star rating summary
ratings_df = df[['rating', 'review']].dropna()
rating_summary = ratings_df.groupby('rating').agg(cnt=('review', 'count')).reset_index()
all_ratings = pd.DataFrame({'rating': [5, 4, 3, 2, 1]})
rating_summary = all_ratings.merge(rating_summary, on='rating', how='left').fillna(0)
rating_summary['cnt'] = rating_summary['cnt'].astype(int)
total_reviews = rating_summary['cnt'].sum()
rating_summary['percent'] = round((rating_summary['cnt'] / total_reviews) * 100, 1) if total_reviews > 0 else 0.0

# Custom CSS for clean font and spacing
st.markdown("""
<style>
body {
    font-family: 'Segoe UI', sans-serif;
    font-size: 16px;
}
.caption {
    font-size: 14px;
    color: #666;
}
h3, h2, h1 {
    font-size: 28px !important;
}
.stars {
    white-space: nowrap;
    text-align: right;
    font-size: 18px;
    line-height: 1;
    max-width: 100%;
}
</style>
""", unsafe_allow_html=True)

# Layout
left, right = st.columns([1.2, 1.3])

# LEFT SIDE: Description + Review + Ratings
with left:
    st.markdown("## 🧠 CUSTOMER FEEDBACK – USING SNOWFLAKE CORTEX AI")
    st.caption("Here’s what WhatsApp users are saying:")
    sample_review = df.sample(1)['review'].values[0]
    st.markdown(f"> *{sample_review}*")

    st.markdown("### ⭐ WhatsApp Rating Breakdown")
    for _, row in rating_summary.iterrows():
        stars = "⭐" * int(row['rating'])
        percent = f"{row['percent']}%"
        count = f"{row['cnt']:.1f} Reviews"
        st.markdown(f"""
            <div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 0;'>
                <div style='flex: 0 0 18%; font-weight: 600;'>{percent}</div>
                <div style='flex: 0 0 28%; color: #555;'>{count}</div>
                <div style='flex: 0 0 40%; background: #eee; border-radius: 5px; height: 10px;'>
                    <div style='width: {row['percent']}%; height: 10px; background-color: #1f77b4; border-radius: 5px;'></div>
                </div>
                <div style='flex: 0 0 14%;' class='stars'>{stars}</div>
            </div>
        """, unsafe_allow_html=True)

# RIGHT SIDE: Chart Panel
with right:
    st.markdown("### 📊 Explore Key Themes with AI")
    chart_type = st.radio(
        "Choose a visualization:",
        ("Bubble Matrix", "Treemap by Action", "Heatmap Quadrant","Sentiment Breakdown"),
        horizontal=True
    )

    fig = None

    if chart_type == "Bubble Matrix":
        fig = px.scatter(
            agg, x='satisfaction', y='significance', size='volume', color='action',
            hover_name='classify_text_col', hover_data=['satisfaction', 'significance', 'volume'],
            color_discrete_map={
                'Address Immediately': '#DC2626',
                'Maintain & Monitor': '#16A34A',
                'Minimize & Reassess': '#FACC15',
                'Explore': '#6B7280'
            },
            size_max=60, title="Satisfaction vs. Significance"
        )
        fig.add_shape(type="line", x0=0, x1=0, y0=0, y1=1, line=dict(dash="dot", color="gray"))
        fig.add_shape(type="line", x0=-1, x1=1, y0=0.5, y1=0.5, line=dict(dash="dot", color="gray"))
        fig.update_traces(marker=dict(opacity=0.75, line=dict(width=2, color='black')))
        fig.update_layout(legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))

    elif chart_type == "Treemap by Action":
        fig = px.treemap(
            agg, path=['action', 'classify_text_col'], values='volume', color='satisfaction',
            color_continuous_scale='RdYlGn', title="Treemap: Review Themes by Action"
        )

    elif chart_type == "Heatmap Quadrant":
        agg['satisfaction_zone'] = pd.cut(agg['satisfaction'], [-1, -0.1, 0.1, 1], labels=['Low', 'Neutral', 'High'])
        agg['significance_zone'] = pd.cut(agg['significance'], [0, 0.5, 1], labels=['Low', 'High'])
        heatmap_df = agg.groupby(['significance_zone', 'satisfaction_zone'])['classify_text_col']\
            .apply(lambda x: "<br>".join(x)).reset_index()
        heatmap_df['count'] = agg.groupby(['significance_zone', 'satisfaction_zone'])['volume'].sum().values

        fig = px.density_heatmap(
            heatmap_df, x='satisfaction_zone', y='significance_zone', z='count',
            text_auto=True, color_continuous_scale='YlOrRd',
            title="Heatmap: Sentiment Zones"
        )
        fig.update_layout(yaxis_title="Significance", xaxis_title="Satisfaction")
    
    elif chart_type == "Sentiment Breakdown":
        # Calculate sentiment categories
        def label_sentiment(score):
            if score >= 0.3:
                return "Positive"
            elif score <= -0.3:
                return "Negative"
            else:
                return "Neutral"
    
        df['sentiment_label'] = df['sentiment_score'].apply(label_sentiment)
        sentiment_counts = df['sentiment_label'].value_counts().reset_index()
        sentiment_counts.columns = ['sentiment', 'count']
        sentiment_counts['percent'] = round((sentiment_counts['count'] / sentiment_counts['count'].sum()) * 100, 1)
    
        fig = px.pie(
            sentiment_counts,
            names='sentiment',
            values='count',
            hole=0.4,
            title="Sentiment Breakdown",
            color='sentiment',
            color_discrete_map={
                'Positive': '#16A34A',
                'Neutral': '#FACC15',
                'Negative': '#DC2626'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=True)

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No chart available for selected type.")



# Drill-down Review
st.markdown("---")
st.subheader("🔎 View a Sample Review by Category")
selected_category = st.selectbox("Choose a topic:", agg['classify_text_col'].unique())
if selected_category:
    sample_reviews = df[df['classify_text_col'] == selected_category]['review'].dropna()
    if not sample_reviews.empty:
        st.markdown(f"**🗣️ {selected_category}:**")
        st.markdown(f"> {sample_reviews.sample(1).values[0]}")
    else:
        st.info("No reviews found in this category.")
