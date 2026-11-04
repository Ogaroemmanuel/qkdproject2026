"""SMTP delivery for registration verification codes."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

import streamlit as st


def send_verification_email(recipient: str, code: str) -> None:
    """Send a one-time registration code using SMTP values from Streamlit secrets."""
    try:
        config = st.secrets["email"]
        host = str(config["smtp_host"])
        port = int(config.get("smtp_port", 587))
        username = str(config["smtp_username"])
        password = str(config["smtp_password"])
        sender = str(config.get("from_address", username))
        use_ssl = bool(config.get("use_ssl", False))
    except Exception as exc:
        raise RuntimeError(
            "Email delivery is not configured. Add an [email] section to .streamlit/secrets.toml."
        ) from exc

    message = EmailMessage()
    message["Subject"] = "Your SD-QKD Security Lab verification code"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        f"Your verification code is {code}.\n\n"
        "It expires in 10 minutes and can be used once. "
        "If you did not request an account, you can ignore this email."
    )

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=20) as server:
                server.login(username, password)
                server.send_message(message)
        else:
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise RuntimeError("The verification email could not be sent. Check the SMTP settings and try again.") from exc
