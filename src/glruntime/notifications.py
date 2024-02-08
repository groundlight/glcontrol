import logging
import smtplib, ssl
import cv2

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from twilio.rest import Client
from slack_sdk import WebClient

import requests
import os

def send_notifications(det_name: str, query: str, label: str, options: dict, image, logger: logging.Logger):
    if "condition" not in options:
        logger.warn("No condition provided")
        return
    condition = options["condition"].upper() # "PASS" or "FAIL"
    if label == "YES":
        label = "PASS"
    elif label == "NO":
        label = "FAIL"

    if "stacklight" in options:
        logger.info("Sending to stacklight")
        stacklight_options = options["stacklight"]
        post_to_stacklight(det_name, query, label, stacklight_options)

    if not ((condition == "PASS" and label == "PASS") or (condition == "FAIL" and label == "FAIL")):
        logger.info("Condition not met")
        return
    
    if "email" in options:
        logger.info("Sending email")
        email_options = options["email"]
        send_email(det_name, query, image, label, email_options)
    if "twilio" in options:
        logger.info("Sending sms")
        twilio_options = options["twilio"]
        send_sms(det_name, query, label, twilio_options)
    if "slack" in options:
        logger.info("Sending slack")
        slack_options = options["slack"]
        send_slack(det_name, query, label, slack_options)

def send_email(det_name: str, query: str, image, label: str, options: dict):
    subject = f"Your detector [{det_name}] detected an anomaly"
    body = f"Your detector [{det_name}] returned a \"{label}\" result to the query [{query}].\n\nThe image of the anomaly is attached below."
    sender_email = options["from_email"]
    receiver_email = options["to_email"]
    app_password = options["email_password"]

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "image.jpg"  # In same directory as script

    _, im_buf_arr = cv2.imencode(".jpg", image)
    byte_im = im_buf_arr.tobytes()
    part = MIMEImage(byte_im)

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    host = "host" in options and options["host"] or "smtp.gmail.com"
    with smtplib.SMTP_SSL(host, 465, context=context) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, text)

def send_sms(det_name: str, query: str, label: str, options: dict):
    account_sid = options["account_sid"]
    auth_token = options["auth_token"]
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body=f"Your detector [{det_name}] returned a \"{label}\" result to the query [{query}].",
                        from_=options["from_number"],
                        to=options["to_number"]
                    )
    
def send_slack(det_name: str, query: str, label: str, options: dict):
    client = WebClient(token=options["token"])
    response = client.chat_postMessage(
        channel=options["channel_id"],
        text=f"Your detector [{det_name}] returned a \"{label}\" result to the query [{query}]."
    )

def post_to_stacklight(det_name: str, query: str, label: str, options: dict):
    if "ip" not in options:
        return
    
    ip: str = options["ip"]

    port = "8080"

    # http post to stacklight
    requests.post(f"http://{ip}:{port}/display", data=label)