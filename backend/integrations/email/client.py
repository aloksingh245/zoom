import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings

logger = logging.getLogger(__name__)

class EmailNotificationService:
    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        if not settings.smtp_username or not settings.smtp_password:
            logger.warning(f"[SMTP MOCK] No SMTP credentials configured. Email to '{to_email}' simulated.")
            print(f"\n==================================================")
            print(f"📧 [SMTP MOCK] Email sent to: {to_email}")
            print(f"Subject: {subject}")
            print(f"==================================================\n")
            return True

        msg = MIMEMultipart()
        msg['From'] = settings.smtp_from
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.sendmail(settings.smtp_from, to_email, msg.as_string())
            logger.info(f"Notification email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification email to {to_email}: {e}")
            return False

    def send_class_assigned_notification(self, mentor_email: str, class_topic: str, date: str, start_time: str, duration: int, timezone: str, zoom_link: str):
        subject = f"📅 New Class Assigned: {class_topic} - Zoom Scheduler"
        body = f"""
        <html>
            <body>
                <h2 style="color: #4f46e5;">Class Assignment Notification</h2>
                <p>Hello,</p>
                <p>You have been assigned as the mentor for a new class session:</p>
                <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-top: 15px;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Topic:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{class_topic}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Date:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Start Time:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{start_time} ({timezone})</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Duration:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{duration} minutes</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Zoom Link:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">
                            <a href="{zoom_link}" style="color: #4f46e5; font-weight: bold;">Join Meeting</a>
                        </td>
                    </tr>
                </table>
                <br>
                <p style="color: #64748b; font-size: 12px;">Zoom Scheduler Team</p>
            </body>
        </html>
        """
        return self.send_email(mentor_email, subject, body)

    def send_class_updated_notification(self, mentor_email: str, class_topic: str, date: str, start_time: str, duration: int, timezone: str, zoom_link: str):
        subject = f"✏️ Class Updated: {class_topic} - Zoom Scheduler"
        body = f"""
        <html>
            <body>
                <h2 style="color: #eab308;">Class Update Notification</h2>
                <p>Hello,</p>
                <p>The details of a class session you are mentoring have been updated:</p>
                <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-top: 15px;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Topic:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{class_topic}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Date:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Start Time:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{start_time} ({timezone})</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Duration:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">{duration} minutes</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Zoom Link:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #0f172a;">
                            <a href="{zoom_link}" style="color: #4f46e5; font-weight: bold;">Join Meeting</a>
                        </td>
                    </tr>
                </table>
                <br>
                <p style="color: #64748b; font-size: 12px;">Zoom Scheduler Team</p>
            </body>
        </html>
        """
        return self.send_email(mentor_email, subject, body)

email_notification_service = EmailNotificationService()
