import streamlit as st
import pandas as pd
import datetime
import json
from pathlib import Path

import sys
from pathlib import Path

# Try to import Option Menu, with standard selectbox as fallback
try:
    from streamlit_option_menu import option_menu
except ImportError:
    option_menu = None

# Add project root to Python path to ensure 'app' imports work correctly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import our wrappers
from app.models.Sentiment import get_sentiment
from app.models.Issue import escalateit
from app.models.Response import automate_response

# Central configuration paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TICKETS_DB_PATH = DATA_DIR / "local_tickets_db.json"

# Function to save ticket locally for robustness (fallback for MongoDB)
def save_ticket_locally(title, body, sentiment, escalation, response):
    tickets = []
    if TICKETS_DB_PATH.exists():
        try:
            with open(TICKETS_DB_PATH, "r") as f:
                tickets = json.load(f)
        except Exception:
            tickets = []
            
    new_ticket = {
        "id": len(tickets) + 1,
        "title": title,
        "body": body,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "escalation": escalation,
        "response": response
    }
    tickets.append(new_ticket)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(TICKETS_DB_PATH, "w") as f:
        json.dump(tickets, f, indent=4)
    return new_ticket

# Fetch local tickets
def load_local_tickets():
    if TICKETS_DB_PATH.exists():
        try:
            with open(TICKETS_DB_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    # Seed default mock tickets for UI demo when empty
    default_tickets = [
        {
            "id": 1,
            "title": "System offline error",
            "body": "The server has been completely down since 3 PM. Critical issue!",
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).isoformat(),
            "sentiment": "Slightly Negative",
            "escalation": "Escalation Keyword Found: 'critical'",
            "response": "Re: System offline error\n\nDear Customer,\n\nWe apologize for the inconvenience..."
        },
        {
            "id": 2,
            "title": "Love the new updates",
            "body": "Really happy with the new features in the dashboard, great work team!",
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat(),
            "sentiment": "Slightly Positive",
            "escalation": False,
            "response": "Re: Love the new updates\n\nDear Customer,\n\nThank you for the amazing feedback..."
        }
    ]
    return default_tickets

def main():
    st.set_page_config(
        page_title="Core Support Analytics & Prevention System",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Premium CSS injection
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .main {
            background-color: #0d0f12;
            color: #e2e8f0;
            padding: 1.5rem;
        }
        
        /* Custom card styling */
        .metric-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #3b82f6;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin-top: 0.25rem;
            background: linear-gradient(to right, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-title {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
        }
        
        /* Banner Header */
        .banner {
            background: linear-gradient(90deg, #1d4ed8 0%, #1e1b4b 100%);
            border-radius: 12px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border: 1px solid #2563eb;
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.15);
        }
        
        .banner h1 {
            color: #ffffff !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .banner p {
            color: #bfdbfe;
            font-size: 1.1rem;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation Sidebar
    st.sidebar.markdown("<h2 style='text-align: center; color: #60a5fa;'>🛡️ Shield Core</h2>", unsafe_allow_html=True)
    
    options = ["Issue Prevention Dashboard", "Sentiment Analysis", "Issue Escalation", "Automated Response"]
    icons = ["shield-check", "emoji-smile", "arrow-up-circle", "chat-dots"]
    
    if option_menu:
        with st.sidebar:
            selected = option_menu(
                menu_title="Navigation",
                options=options,
                icons=icons,
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#0f172a"},
                    "icon": {"color": "#60a5fa", "font-size": "18px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1e293b", "color": "#e2e8f0"},
                    "nav-link-selected": {"background-color": "#2563eb"},
                }
            )
    else:
        selected = st.sidebar.selectbox("Navigate System", options)
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("<small style='color: #64748b;'>Customer Support Ticket Automation<br>Infosys Springboard Internship</small>", unsafe_allow_html=True)

    # 1. ISSUE PREVENTION DASHBOARD
    if selected == "Issue Prevention Dashboard":
        st.markdown("""
            <div class='banner'>
                <h1>Issue Prevention Dashboard</h1>
                <p>Real-time ticket intelligence, preventative risk monitoring, and automated performance logs.</p>
            </div>
        """, unsafe_allow_html=True)
        
        tickets = load_local_tickets()
        total_tickets = len(tickets)
        escalated_tickets = [t for t in tickets if t.get("escalation") is not False]
        total_escalated = len(escalated_tickets)
        
        # Calculate sentiments
        positives = len([t for t in tickets if "positive" in str(t.get("sentiment")).lower()])
        negatives = len([t for t in tickets if "negative" in str(t.get("sentiment")).lower()])
        neutrals = total_tickets - positives - negatives
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Total Tickets</div>
                    <div class='metric-value'>{total_tickets}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Escalations</div>
                    <div class='metric-value' style='color:#ef4444;'>{total_escalated}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Negative Sentiment</div>
                    <div class='metric-value' style='color:#f97316;'>{negatives}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Positive Sentiment</div>
                    <div class='metric-value' style='color:#22c55e;'>{positives}</div>
                </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 Ticket Analysis & Key Trends")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Sentiment Distribution")
            chart_df = pd.DataFrame({
                "Count": [positives, neutrals, negatives]
            }, index=["Positive", "Neutral", "Negative"])
            st.bar_chart(chart_df)
            
        with chart_col2:
            st.markdown("#### Escalation Ratios")
            esc_df = pd.DataFrame({
                "Count": [total_tickets - total_escalated, total_escalated]
            }, index=["Standard", "Escalated"])
            st.bar_chart(esc_df)

        st.subheader("📋 Recent Customer Activity Log")
        if tickets:
            df_display = pd.DataFrame(tickets)
            st.dataframe(
                df_display[["id", "timestamp", "title", "sentiment", "escalation"]],
                use_container_width=True
            )
        else:
            st.info("No tickets currently logged. Go to the forms to process new queries.")

    # 2. SENTIMENT ANALYSIS
    elif selected == "Sentiment Analysis":
        st.subheader("😊 Instant Sentiment Analyzer")
        st.write("Determine the customer's sentiment from their ticket details.")
        
        with st.form("sentiment_form"):
            title = st.text_input("Ticket Subject", placeholder="e.g. Broken app payment loop")
            body = st.text_area("Ticket Body / Details", placeholder="Enter the customer query text...")
            submit = st.form_submit_button("Analyze Sentiment")
            
        if submit:
            if not title or not body:
                st.warning("Please fill in both the Subject and Body.")
            else:
                with st.spinner("Running Hugging Face NLP pipeline..."):
                    res = get_sentiment(title, body)
                    sentiment = res.get("sentiment", "Neutral")
                    score = res.get("score", 0.5)
                    
                    st.success("Analysis Complete!")
                    st.write(f"**Sentiment Category**: {sentiment}")
                    st.write(f"**Model Confidence**: {score:.2%}")
                    
                    # Persist ticket interaction
                    save_ticket_locally(title, body, sentiment, False, "")

    # 3. ISSUE ESCALATION
    elif selected == "Issue Escalation":
        st.subheader("🚨 Real-Time Escalation Checker")
        st.write("Check if a support ticket triggers automated priority escalation.")
        
        with st.form("escalation_form"):
            title = st.text_input("Ticket Subject", placeholder="e.g. Critical database error")
            body = st.text_area("Ticket Body / Details", placeholder="Enter query text details...")
            submit = st.form_submit_button("Check Escalation Status")
            
        if submit:
            if not title or not body:
                st.warning("Please fill in both fields.")
            else:
                reason = escalateit(title, body)
                if reason:
                    st.error(f"🚨 Escalated! Reason: {reason}")
                else:
                    st.success("✔️ Normal Priority. No immediate escalation triggered.")
                    
                # Save state
                sent = get_sentiment(title, body).get("sentiment", "Neutral")
                save_ticket_locally(title, body, sent, reason, "")

    # 4. AUTOMATED RESPONSE
    elif selected == "Automated Response":
        st.subheader("✉️ GenAI Response Auto-Drafter")
        st.write("Generate a personalized template email response based on customer sentiment.")
        
        with st.form("response_form"):
            title = st.text_input("Ticket Subject", placeholder="e.g. Refund request pending")
            body = st.text_area("Ticket Body", placeholder="e.g. I ordered last week but didn't get any update.")
            name = st.text_input("Customer Name", value="Valued Customer")
            submit = st.form_submit_button("Draft Response")
            
        if submit:
            if not title or not body:
                st.warning("Please enter Subject and Body.")
            else:
                with st.spinner("Processing automated templates..."):
                    subject, reply = automate_response(title, body, customer_name=name)
                    sentiment = get_sentiment(title, body).get("sentiment", "Neutral")
                    escalation = escalateit(title, body)
                    
                    st.success("Drafting Successful!")
                    st.markdown("### Generated Email Draft")
                    st.text_area("Subject Header", value=subject, height=50)
                    st.text_area("Body Template", value=reply, height=300)
                    
                    # Store final generated interaction
                    save_ticket_locally(title, body, sentiment, escalation, f"{subject}\n\n{reply}")

if __name__ == "__main__":
    main()
