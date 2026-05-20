import os
import smtplib
from html import escape
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import pandas as pd
import streamlit as st


# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="MCC Expiry Messenger",
    page_icon="📨",
    layout="wide",
)

SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587


# ==============================
# MESSAGE TYPES
# ==============================

MESSAGE_TYPES = {

    "Emirates ID Expiry": {
        "document": "Emirates ID",
        "title": "MCC Emirates ID Expiry Messenger",
        "subject": "Emirates ID Expiry Soon - Renewal Required",
        "details_title": "Labour Details",
        "required_columns": {
            "previous id": "Previous ID",
            "employee name": "Employee Name",
            "supplier name": "Supplier Name",
            "visa sponsor": "Visa Sponsor",
            "email": "Email",
        },
        "message": (
            "This is to inform you that your labour's Emirates ID is going to expire soon. "
            "Kindly renew and update the valid copy of your Emirates ID at the earliest "
            "to avoid penalties or interruption of duties."
        ),
    },

    "Passport Expiry": {
        "document": "Passport",
        "title": "MCC Passport Expiry Messenger",
        "subject": "Passport Expiry Soon - Renewal Required",
        "details_title": "Passport Details",
        "required_columns": {
            "previous id": "Previous ID",
            "employee name": "Employee Name",
            "supplier name": "Supplier Name",
            "visa sponsor": "Visa Sponsor",
            "email": "Email",
        },
        "message": (
            "This is to inform you that your labour's Passport is going to expire soon. "
            "Kindly renew and update the valid copy of the Passport at the earliest."
        ),
    },

    "Trade Licence Expiry": {
        "document": "Trade Licence",
        "title": "MCC Trade Licence Expiry Messenger",
        "subject": "Trade Licence Expiry Soon - Renewal Required",
        "details_title": "Trade Licence Details",
        "required_columns": {
            "trade licence no": "Trade Licence No",
            "company name": "Company Name",
            "supplier name": "Supplier Name",
            "visa sponsor": "Visa Sponsor",
            "email": "Email",
        },
        "message": (
            "This is to inform you that your Trade Licence is going to expire soon. "
            "Kindly renew and update the valid copy at the earliest."
        ),
    },

    "Workmensation Expiry": {
        "document": "Workmensation",
        "title": "MCC Workmensation Expiry Messenger",
        "subject": "Workmensation Expiry Soon - Renewal Required",
        "details_title": "Workmensation Details",
        "required_columns": {
            "policy no": "Policy No",
            "company name": "Company Name",
            "supplier name": "Supplier Name",
            "visa sponsor": "Visa Sponsor",
            "email": "Email",
        },
        "message": (
            "This is to inform you that your Workmensation policy is going to expire soon. "
            "Kindly renew and update the valid copy at the earliest."
        ),
    },
}


# ==============================
# SIDEBAR
# ==============================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

with st.sidebar:

    st.header("Appearance")

    st.session_state.theme_mode = st.radio(
        "Choose Theme",
        ["Light", "Dark"],
        horizontal=True,
    )

    st.divider()

    st.header("Message Type")

    selected_message_type = st.selectbox(
        "Select Expiry Message",
        list(MESSAGE_TYPES.keys()),
    )

    MESSAGE_CONFIG = MESSAGE_TYPES[selected_message_type].copy()

    REQUIRED_COLUMNS = MESSAGE_CONFIG["required_columns"]

    DOCUMENT_NAME = MESSAGE_CONFIG["document"]

    st.divider()


# ==============================
# THEME
# ==============================

if st.session_state.theme_mode == "Dark":

    THEME = {
        "app_bg": "#0F172A",
        "sidebar_bg": "#111827",
        "card_bg": "#1E293B",
        "text": "#F8FAFC",
        "muted": "#CBD5E1",
        "primary": "#60A5FA",
        "border": "#334155",
        "input_bg": "#0F172A",
        "input_text": "#F8FAFC",
        "info_bg": "#1E3A5F",
        "info_text": "#DBEAFE",
    }

else:

    THEME = {
        "app_bg": "#F4F7FB",
        "sidebar_bg": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "text": "#111827",
        "muted": "#4B5563",
        "primary": "#003B73",
        "border": "#D9E2EC",
        "input_bg": "#FFFFFF",
        "input_text": "#111827",
        "info_bg": "#E8F2FF",
        "info_text": "#004A8F",
    }


# ==============================
# CUSTOM CSS
# ==============================

CUSTOM_CSS = f"""
<style>

html, body, .stApp {{
    background-color: {THEME["app_bg"]} !important;
    color: {THEME["text"]} !important;
}}

.main .block-container {{
    max-width: 1250px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}}

[data-testid="stSidebar"] {{
    background-color: {THEME["sidebar_bg"]} !important;
    border-right: 1px solid {THEME["border"]};
}}

[data-testid="stSidebar"] * {{
    color: {THEME["text"]} !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

h1, h2, h3, h4, h5, h6,
p, label, span, div {{
    color: {THEME["text"]} !important;
}}

.main-title {{
    font-size: 36px;
    font-weight: 800;
    color: {THEME["primary"]} !important;
    margin-bottom: 0px;
}}

.sub-title {{
    font-size: 17px;
    color: {THEME["muted"]} !important;
    margin-top: 6px;
}}

input, textarea, select {{
    background-color: {THEME["input_bg"]} !important;
    color: {THEME["input_text"]} !important;
    border-radius: 10px !important;
    border: 1px solid {THEME["border"]} !important;
}}

[data-baseweb="select"] > div {{
    background-color: {THEME["input_bg"]} !important;
    color: {THEME["input_text"]} !important;
    border: 1px solid {THEME["border"]} !important;
    border-radius: 10px !important;
}}

[data-baseweb="select"] span {{
    color: {THEME["input_text"]} !important;
}}

[data-testid="stTextArea"] textarea {{
    min-height: 170px !important;
}}

[data-testid="stFileUploader"] section {{
    background-color: {THEME["card_bg"]} !important;
    border: 1px dashed {THEME["border"]} !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}}

[data-testid="stFileUploader"] section * {{
    color: {THEME["text"]} !important;
}}

[data-testid="stFileUploader"] button {{
    background-color: {THEME["primary"]} !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}}

div[data-testid="stAlert"] {{
    background-color: {THEME["info_bg"]} !important;
    color: {THEME["info_text"]} !important;
    border-radius: 12px !important;
    border: 1px solid {THEME["border"]} !important;
}}

div[data-testid="stAlert"] * {{
    color: {THEME["info_text"]} !important;
}}

.stButton button,
.stDownloadButton button {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: 1px solid {THEME["border"]} !important;
}}

.stButton button[kind="primary"] {{
    background-color: {THEME["primary"]} !important;
    color: white !important;
    border: none !important;
}}

[data-testid="stMetric"] {{
    background-color: {THEME["card_bg"]} !important;
    border: 1px solid {THEME["border"]} !important;
    border-radius: 16px !important;
    padding: 16px !important;
}}

[data-testid="stMetric"] * {{
    color: {THEME["text"]} !important;
}}

[data-testid="stDataFrame"] {{
    background-color: {THEME["card_bg"]} !important;
    border-radius: 12px !important;
    border: 1px solid {THEME["border"]} !important;
}}

.warning-box {{
    background: #FFF7E6 !important;
    border-left: 5px solid #F59E0B !important;
    padding: 14px 18px !important;
    border-radius: 10px !important;
    color: #663C00 !important;
    font-weight: 600 !important;
}}

.warning-box * {{
    color: #663C00 !important;
}}

hr {{
    border-color: {THEME["border"]} !important;
}}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================
# FUNCTIONS
# ==============================

def normalize_excel(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def validate_columns(df, required_columns):
    return [col for col in required_columns if col not in df.columns]


def clean_data(df, required_columns):

    df = df.copy()

    df = df.dropna(subset=["email"])

    for col in required_columns:
        df[col] = df[col].astype(str).str.strip()

    df = df[df["email"] != ""]
    df = df[df["email"].str.lower() != "nan"]

    return df


def build_email_body(
    group,
    company_name,
    message_config,
    required_columns,
    custom_message,
):

    supplier_names = group["supplier name"].dropna().unique()

    supplier_text = ", ".join([str(x) for x in supplier_names])

    clean_message = escape(custom_message).replace("\n", "<br>")

    table_headers = ""

    for col, display_name in required_columns.items():

        if col != "email":

            table_headers += f"""
            <th style="border:1px solid #000;padding:8px;background:#f2f2f2;">
                {escape(display_name)}
            </th>
            """

    table_rows = ""

    for _, row in group.iterrows():

        row_cells = ""

        for col in required_columns:

            if col != "email":

                row_cells += f"""
                <td style="border:1px solid #000;padding:6px;">
                    {escape(str(row[col]))}
                </td>
                """

        table_rows += f"<tr>{row_cells}</tr>"

    body = f"""
    <html>
    <body style="font-family:Arial,sans-serif;font-size:14px;color:#222;">

        Dear Supplier,<br><br>

        {clean_message}<br><br>

        <b>Supplier Name:</b> {escape(supplier_text)}<br><br>

        <b>{escape(message_config["details_title"])}:</b><br><br>

        <table style="border-collapse:collapse;width:100%;">

            <tr>
                {table_headers}
            </tr>

            {table_rows}

        </table>

        <br>

        Your prompt action in this matter will be highly appreciated.

        <br><br>

        Regards,<br>

        <b>{escape(company_name)}</b>

    </body>
    </html>
    """

    return body


def send_email(
    sender_email,
    app_password,
    to_email,
    subject,
    body_html,
    sender_name,
):

    msg = MIMEMultipart()

    msg["Subject"] = subject

    msg["From"] = formataddr((sender_name, sender_email))

    msg["To"] = to_email

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(sender_email, app_password)

        server.sendmail(sender_email, to_email, msg.as_string())


# ==============================
# EMAIL SETTINGS
# ==============================

with st.sidebar:

    st.header("Email Settings")

    sender_email = st.text_input(
        "Sender Email",
        value=os.getenv("MCC_SENDER_EMAIL", "info@mccgroupuae.ae"),
    )

    app_password = st.text_input(
        "Microsoft 365 App Password",
        value=os.getenv("MCC_APP_PASSWORD", ""),
        type="password",
    )

    sender_name = st.text_input(
        "Sender Name",
        value="MCC GROUP",
    )

    company_name = st.text_input(
        "Company Name in Signature",
        value="MCC Group",
    )

    subject = st.text_input(
        "Email Subject",
        value=MESSAGE_CONFIG["subject"],
    )

    custom_message = st.text_area(
        "Email Description / Message",
        value=MESSAGE_CONFIG["message"],
        height=180,
    )

    st.divider()

    st.caption(
        "Tip: keep the password in environment variables, not inside the code."
    )


# ==============================
# LOGO + HEADER
# ==============================

top_col1, top_col2 = st.columns([1, 9])

with top_col1:
    st.image("logo png.png", width=120)

with top_col2:
    st.markdown(
        f"""
        <div style="padding-top:18px;">
            <div class="main-title">{escape(MESSAGE_CONFIG["title"])}</div>
            <div class="sub-title">
                Upload Excel, preview supplier emails, validate data,
                and send {escape(DOCUMENT_NAME)} expiry reminders from one dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==============================
# FILE UPLOAD
# ==============================

uploaded_file = st.file_uploader(
    f"Upload your {DOCUMENT_NAME} Excel file",
    type=["xlsx", "xls"],
)

if uploaded_file is None:

    st.info(
        "Upload an Excel file with these columns: "
        + ", ".join(REQUIRED_COLUMNS.values())
    )

    st.stop()