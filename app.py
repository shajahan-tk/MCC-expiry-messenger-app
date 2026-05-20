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
        index=0 if st.session_state.theme_mode == "Light" else 1,
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
        "button_bg": "#2563EB",
    }
else:
    THEME = {
        "app_bg": "#F3F6FA",
        "sidebar_bg": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "text": "#111827",
        "muted": "#475569",
        "primary": "#003B73",
        "border": "#CBD5E1",
        "input_bg": "#FFFFFF",
        "input_text": "#111827",
        "info_bg": "#DBEAFE",
        "info_text": "#075985",
        "button_bg": "#003B73",
    }


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
    padding-left: 3rem;
    padding-right: 3rem;
}}

[data-testid="stSidebar"] {{
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}}

[data-testid="stSidebar"] * {{
    color: #111827 !important;
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
    color: #003B73 !important;
    margin-bottom: 4px;
}}

.sub-title {{
    font-size: 17px;
    color: #475569 !important;
    margin-top: 6px;
}}

/* INPUTS */

input, textarea {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-radius: 10px !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: none !important;
}}

input:focus, textarea:focus {{
    border: 1px solid #003B73 !important;
    box-shadow: 0 0 0 1px #003B73 !important;
}}

/* SELECT BOX */

[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    box-shadow: none !important;
}}

[data-baseweb="select"] span {{
    color: #111827 !important;
}}

[data-baseweb="select"] svg {{
    fill: #111827 !important;
    color: #111827 !important;
}}

/* DROPDOWN POPUP FIX */

ul[role="listbox"] {{
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    padding: 6px !important;
}}

ul[role="listbox"] li {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-radius: 8px !important;
}}

ul[role="listbox"] li * {{
    color: #111827 !important;
}}

ul[role="listbox"] li:hover {{
    background-color: #DBEAFE !important;
    color: #003B73 !important;
}}

[data-baseweb="popover"] {{
    background-color: #FFFFFF !important;
}}

[data-baseweb="menu"] {{
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
}}

[data-baseweb="menu"] * {{
    color: #111827 !important;
}}

[data-baseweb="menu"] li {{
    background-color: #FFFFFF !important;
}}

[data-baseweb="menu"] li:hover {{
    background-color: #DBEAFE !important;
}}

/* FILE UPLOADER */

[data-testid="stFileUploader"] section {{
    background-color: #FFFFFF !important;
    border: 1px dashed #CBD5E1 !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}}

[data-testid="stFileUploader"] section * {{
    color: #111827 !important;
}}

[data-testid="stFileUploader"] button {{
    background-color: #003B73 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
}}

[data-testid="stFileUploader"] button * {{
    color: #FFFFFF !important;
}}

/* ALERT */

div[data-testid="stAlert"] {{
    background-color: #DBEAFE !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 12px !important;
}}

div[data-testid="stAlert"] * {{
    color: #075985 !important;
}}

/* BUTTONS */

.stButton button,
.stDownloadButton button {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: none !important;
}}

.stButton button[kind="primary"] {{
    background-color: #003B73 !important;
    color: #FFFFFF !important;
    border: none !important;
}}

.stButton button[kind="primary"] * {{
    color: #FFFFFF !important;
}}

/* METRICS */

[data-testid="stMetric"] {{
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 16px !important;
}}

[data-testid="stMetric"] * {{
    color: #111827 !important;
}}

/* DATAFRAME */

[data-testid="stDataFrame"] {{
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
}}

/* WARNING BOX */

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
    border-color: #E2E8F0 !important;
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


def build_email_body(group, company_name, message_config, required_columns, custom_message):
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
            <tr>{table_headers}</tr>
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


def send_email(sender_email, app_password, to_email, subject, body_html, sender_name):
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

    st.caption("Tip: keep the password in environment variables, not inside the code.")


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


# ==============================
# READ EXCEL
# ==============================

try:
    raw_df = pd.read_excel(uploaded_file)
    df = normalize_excel(raw_df)

except Exception as exc:
    st.error(f"Could not read Excel file: {exc}")
    st.stop()


# ==============================
# VALIDATE
# ==============================

missing_cols = validate_columns(df, REQUIRED_COLUMNS)

if missing_cols:
    missing_names = [REQUIRED_COLUMNS[col] for col in missing_cols]

    st.error("Missing required columns: " + ", ".join(missing_names))
    st.write("Columns found:", list(df.columns))
    st.stop()


# ==============================
# CLEAN DATA
# ==============================

clean_df = clean_data(df, REQUIRED_COLUMNS)

if clean_df.empty:
    st.warning("No valid rows found after cleaning email column.")
    st.stop()


# ==============================
# METRICS
# ==============================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(clean_df))
col2.metric("Supplier Emails", clean_df["email"].nunique())
col3.metric("Suppliers", clean_df["supplier name"].nunique())

if "visa sponsor" in clean_df.columns:
    col4.metric("Visa Sponsors", clean_df["visa sponsor"].nunique())
else:
    col4.metric("Message Type", DOCUMENT_NAME)


# ==============================
# DATA PREVIEW
# ==============================

st.subheader("Data Preview")

st.dataframe(
    clean_df[list(REQUIRED_COLUMNS.keys())],
    use_container_width=True,
)


# ==============================
# EMAIL PREVIEW
# ==============================

st.subheader("Email Preview")

email_options = list(clean_df["email"].dropna().unique())

selected_email = st.selectbox(
    "Choose supplier email to preview",
    email_options,
)

preview_group = clean_df[clean_df["email"] == selected_email]

preview_body = build_email_body(
    group=preview_group,
    company_name=company_name,
    message_config=MESSAGE_CONFIG,
    required_columns=REQUIRED_COLUMNS,
    custom_message=custom_message,
)

st.components.v1.html(
    preview_body,
    height=520,
    scrolling=True,
)


# ==============================
# SEND EMAILS
# ==============================

st.subheader("Send Emails")

st.markdown(
    f"""
    <div class="warning-box">
        Before sending, check the preview and make sure the Excel data is correct.
        Current Message Type: {escape(DOCUMENT_NAME)}
    </div>
    """,
    unsafe_allow_html=True,
)

send_col1, send_col2 = st.columns(2)

with send_col1:
    preview_only = st.button(
        "Run Preview Only",
        use_container_width=True,
    )

with send_col2:
    send_now = st.button(
        f"Send {DOCUMENT_NAME} Emails Now",
        type="primary",
        use_container_width=True,
    )


# ==============================
# SEND LOGIC
# ==============================

if preview_only or send_now:
    if not sender_email or not app_password:
        st.error("Sender email and Microsoft 365 app password are required.")
        st.stop()

    grouped = clean_df.groupby("email", sort=False)

    progress = st.progress(0)
    status = st.empty()
    results = []

    total = len(grouped)

    for index, (to_email, group) in enumerate(grouped, start=1):
        status.info(f"Processing {index}/{total}: {to_email}")

        body = build_email_body(
            group=group,
            company_name=company_name,
            message_config=MESSAGE_CONFIG,
            required_columns=REQUIRED_COLUMNS,
            custom_message=custom_message,
        )

        try:
            if not preview_only:
                send_email(
                    sender_email=sender_email,
                    app_password=app_password,
                    to_email=to_email,
                    subject=subject,
                    body_html=body,
                    sender_name=sender_name,
                )

            results.append(
                {
                    "Email": to_email,
                    "Supplier": ", ".join(group["supplier name"].dropna().unique()),
                    "Records": len(group),
                    "Status": "Preview Only" if preview_only else "Sent",
                }
            )

        except Exception as exc:
            results.append(
                {
                    "Email": to_email,
                    "Supplier": ", ".join(group["supplier name"].dropna().unique()),
                    "Records": len(group),
                    "Status": f"Failed - {exc}",
                }
            )

        progress.progress(index / total)

    status.success("Completed")

    results_df = pd.DataFrame(results)

    st.subheader("Sending Report")

    st.dataframe(
        results_df,
        use_container_width=True,
    )

    csv_data = results_df.to_csv(index=False).encode("utf-8")

    filename = (
        f"mcc_{DOCUMENT_NAME.lower().replace(' ', '_')}_"
        f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    st.download_button(
        "Download Report CSV",
        csv_data,
        filename,
        "text/csv",
        use_container_width=True,
    )