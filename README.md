# MCC Labour Expiry Messenger Web App

This Streamlit web app uploads an Excel file, validates columns, previews expiry reminder emails, groups labour records by supplier email, sends emails using Microsoft 365 SMTP, and creates a send report.

## Required Excel Columns

- Previous ID
- Employee Name
- Supplier Name
- Visa Sponsor
- Email

Column names are case-insensitive.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Safer Password Setup

Do not keep the app password inside the code. Set environment variables instead:

Windows PowerShell:

```powershell
$env:MCC_SENDER_EMAIL="info@mccgroupuae.ae"
$env:MCC_APP_PASSWORD="your_app_password_here"
streamlit run app.py
```

Mac/Linux:

```bash
export MCC_SENDER_EMAIL="info@mccgroupuae.ae"
export MCC_APP_PASSWORD="your_app_password_here"
streamlit run app.py
```

## Important

The uploaded original script contained an exposed app password. Change/revoke that Microsoft 365 app password immediately and create a new one.
