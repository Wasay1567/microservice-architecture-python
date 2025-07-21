import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json, os

def notify(message):
    """
    Sends an email notification to the receiver that the video has been downloaded.
    Args:
        message (dict): Contains 'mp3_fid', 'username' (receiver's email).
    """
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        receiver_email = message["username"]

        sender_email = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")
        subject = "Video Downloaded Notification"
        body = f"Hello,\n\nYour video with ID {mp3_fid} has been downloaded successfully.\n\nBest regards,\nNotification System"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f"Notification sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
    except Exception as err:
        print(f"Failed to send email: {e}")
