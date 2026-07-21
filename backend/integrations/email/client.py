import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any
from core.config import settings

logger = logging.getLogger(__name__)

class EmailNotificationService:
    def send_email(self, to_email: str, subject: str, html_body: str, ics_content: str = None, tenant_settings: Any = None) -> bool:
        print(f"\n📨 send_email() CALLED: to={to_email}, subject={subject[:50]}...", flush=True)
        
        # Resolve configurations dynamically
        smtp_host = tenant_settings.smtp_host if (tenant_settings and tenant_settings.smtp_host) else settings.smtp_host
        smtp_port = tenant_settings.smtp_port if (tenant_settings and tenant_settings.smtp_port) else settings.smtp_port
        smtp_username = tenant_settings.smtp_username if (tenant_settings and tenant_settings.smtp_username) else settings.smtp_username
        smtp_password = tenant_settings.smtp_password if (tenant_settings and tenant_settings.smtp_password) else settings.smtp_password
        smtp_from = tenant_settings.smtp_from if (tenant_settings and tenant_settings.smtp_from) else settings.smtp_from

        is_mock = (
            not smtp_username or 
            not smtp_password or 
            "test" in (smtp_host or "") or 
            smtp_host == "localhost"
        )
        
        if is_mock:
            logger.warning(f"[SMTP MOCK] No SMTP credentials configured. Email to '{to_email}' simulated.")
            print(f"\n==================================================", flush=True)
            print(f"📧 [SMTP MOCK] Email sent to: {to_email}", flush=True)
            print(f"Subject: {subject}", flush=True)
            if ics_content:
                print(f"Attachment: invite.ics (included)", flush=True)
            print(f"==================================================\n", flush=True)
            return True

        # Check if the password is a Brevo REST API Key
        is_brevo_api = smtp_password.startswith("xkeysib-")
        if is_brevo_api:
            print("   Detected Brevo REST API Key. Routing via HTTP API...", flush=True)
            import base64
            import requests

            # Parse sender display name
            sender_name = "Zoom Scheduler"
            sender_email = smtp_from

            # Base64 encode the calendar invite if provided
            attachments = []
            if ics_content:
                ics_base64 = base64.b64encode(ics_content.encode('utf-8')).decode('utf-8')
                attachments.append({
                    "name": "invite.ics",
                    "content": ics_base64
                })

            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_body,
                "attachment": attachments
            }

            headers = {
                "accept": "application/json",
                "api-key": smtp_password,
                "content-type": "application/json"
            }

            try:
                print("   Sending request to Brevo API...", flush=True)
                resp = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers, timeout=10)
                if resp.status_code in [200, 201, 202]:
                    print(f"   ✅ Email SENT via Brevo API! Message ID: {resp.json().get('messageId')}", flush=True)
                    logger.info(f"Notification email successfully sent via Brevo API to {to_email}")
                    return True
                else:
                    print(f"   ❌ Brevo API FAILED ({resp.status_code}): {resp.text}", flush=True)
                    logger.error(f"Failed to send email via Brevo API to {to_email}: {resp.status_code} - {resp.text}")
                    return False
            except Exception as e:
                print(f"   ❌ Brevo API request Exception: {e}", flush=True)
                logger.error(f"Exception sending email via Brevo API to {to_email}: {e}")
                return False

        # Fallback to standard SMTP (e.g. Gmail)
        print("   Routing email via SMTP...", flush=True)
        import email.utils
        import uuid
        import re

        msg = MIMEMultipart('mixed')
        
        domain_part = "zoom-scheduler.local"
        if smtp_from and "@" in smtp_from:
            domain_part = smtp_from.split("@")[-1]
            
        msg['From'] = f"Zoom Scheduler <{smtp_from}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = f"<{uuid.uuid4()}@{domain_part}>"
        msg['MIME-Version'] = '1.0'
        msg['Reply-To'] = smtp_from
        msg['Auto-Submitted'] = 'auto-generated'

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        text_body = html_body
        text_body = re.sub(r'</?(p|div|tr|h1|h2|h3|br)[^>]*>', '\n', text_body)
        text_body = re.sub(r'<[^>]+>', '', text_body)
        text_body = re.sub(r'[ \t]+', ' ', text_body)
        text_body = re.sub(r'\n\s*\n+', '\n\n', text_body).strip()
        
        msg_alternative.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg_alternative.attach(MIMEText(html_body, 'html', 'utf-8'))

        if ics_content:
            method = 'CANCEL' if 'METHOD:CANCEL' in ics_content else 'REQUEST'
            cal_part = MIMEText(ics_content, 'calendar; method=' + method + '; charset="UTF-8"', 'utf-8')
            del cal_part['Content-Transfer-Encoding']
            msg_alternative.attach(cal_part)

        if ics_content:
            from email.mime.base import MIMEBase
            from email import encoders
            method = 'CANCEL' if 'METHOD:CANCEL' in ics_content else 'REQUEST'
            part = MIMEBase('text', 'calendar', method=method)
            part.set_payload(ics_content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="invite.ics"')
            part.add_header('Content-Transfer-Encoding', 'base64')
            msg.attach(part)

        try:
            print(f"   Connecting to SMTP {smtp_host}:{smtp_port}...", flush=True)
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                print(f"   TLS established. Logging in...", flush=True)
                server.login(smtp_username, smtp_password)
                print(f"   Login OK. Sending email...", flush=True)
                server.sendmail(smtp_from, to_email, msg.as_string())
                print(f"   ✅ Email SENT to {to_email}!", flush=True)
            logger.info(f"Notification email successfully sent to {to_email}")
            return True
        except Exception as e:
            print(f"   ❌ SMTP FAILED: {e}", flush=True)
            logger.error(f"Failed to send notification email to {to_email}: {e}")
            return False

    def _generate_ics(self, class_id: str, topic: str, date_str: str, time_str: str, duration_mins: int, timezone_str: str, zoom_link: str, sender_email: str, recipient_email: str, is_cancel: bool = False) -> str:
        from zoneinfo import ZoneInfo
        from datetime import datetime, timedelta

        try:
            tz = ZoneInfo(timezone_str)
            dt_naive = datetime.fromisoformat(f"{date_str}T{time_str}:00")
            dt_aware = dt_naive.replace(tzinfo=tz)
            dt_utc = dt_aware.astimezone(ZoneInfo("UTC"))
            
            dt_end_utc = dt_utc + timedelta(minutes=duration_mins)
            
            start_str = dt_utc.strftime('%Y%m%dT%H%M%SZ')
            end_str = dt_end_utc.strftime('%Y%m%dT%H%M%SZ')
            now_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        except Exception as e:
            logger.error(f"Error creating calendar event time for ICS: {e}")
            return None

        summary = topic.replace('\n', ' ').replace(',', '\\,')
        description = f"Zoom Meeting: {zoom_link}\\nScheduled via Zoom Scheduler.".replace('\n', '\\n')
        uid = f"{class_id}@zoom-scheduler.local"
        
        method = "CANCEL" if is_cancel else "REQUEST"
        status = "CANCELLED" if is_cancel else "CONFIRMED"
        sequence = 1 if is_cancel else 0

        # Build organizer and attendee lines required by Gmail/Outlook to show the RSVP box
        organizer_line = f"ORGANIZER;CN=\"Zoom Scheduler\":mailto:{sender_email}"
        attendee_line = f"ATTENDEE;RSVP=TRUE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;CN=\"Mentor\":mailto:{recipient_email}"

        # Standard RFC 5545 specifies that lines in the calendar file MUST end with \r\n (CRLF)
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Zoom Scheduler//Calendar Event//EN",
            "CALSCALE:GREGORIAN",
            f"METHOD:{method}",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"SEQUENCE:{sequence}",
            f"STATUS:{status}",
            f"DTSTAMP:{now_str}",
            f"DTSTART:{start_str}",
            f"DTEND:{end_str}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{zoom_link}",
            organizer_line,
            attendee_line,
            "END:VEVENT",
            "END:VCALENDAR"
        ]
        return "\r\n".join(ics_lines)

    def send_class_assigned_notification(self, class_id: str, mentor_email: str, class_topic: str, date: str, start_time: str, duration: int, timezone: str, zoom_link: str, tenant_settings: Any = None):
        subject = f"📅 New Class Assigned: {class_topic} - Zoom Scheduler"
        body = f"""
        <html>
            <body>
                <h2 style="color: #4f46e5;">Class Assignment Notification</h2>
                <p>Hello,</p>
                <p>You have been assigned as the mentor for a new class session. An invite file is attached to this email so you can add it to your calendar.</p>
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
        sender_email = tenant_settings.smtp_from if (tenant_settings and tenant_settings.smtp_from) else settings.smtp_from
        ics = self._generate_ics(class_id, class_topic, date, start_time, duration, timezone, zoom_link, sender_email, mentor_email)
        return self.send_email(mentor_email, subject, body, ics_content=ics, tenant_settings=tenant_settings)

    def send_class_updated_notification(self, class_id: str, mentor_email: str, class_topic: str, date: str, start_time: str, duration: int, timezone: str, zoom_link: str, tenant_settings: Any = None):
        subject = f"✏️ Class Updated: {class_topic} - Zoom Scheduler"
        body = f"""
        <html>
            <body>
                <h2 style="color: #eab308;">Class Update Notification</h2>
                <p>Hello,</p>
                <p>The details of a class session you are mentoring have been updated. An updated calendar invite is attached.</p>
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
        sender_email = tenant_settings.smtp_from if (tenant_settings and tenant_settings.smtp_from) else settings.smtp_from
        ics = self._generate_ics(class_id, class_topic, date, start_time, duration, timezone, zoom_link, sender_email, mentor_email)
        return self.send_email(mentor_email, subject, body, ics_content=ics, tenant_settings=tenant_settings)

    def send_class_unassigned_notification(self, class_id: str, mentor_email: str, class_topic: str, date: str, start_time: str, timezone: str, tenant_settings: Any = None):
        subject = f"❌ Class Cancelled/Unassigned: {class_topic} - Zoom Scheduler"
        body = f"""
        <html>
            <body>
                <h2 style="color: #ef4444;">Class Unassignment Notification</h2>
                <p>Hello,</p>
                <p>Please note that you are no longer assigned as the mentor for the following class session. A cancellation invite is attached to clear your calendar.</p>
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
                </table>
                <p>If you believe this is an error, please contact the administrator.</p>
                <br>
                <p style="color: #64748b; font-size: 12px;">Zoom Scheduler Team</p>
            </body>
        </html>
        """
        sender_email = tenant_settings.smtp_from if (tenant_settings and tenant_settings.smtp_from) else settings.smtp_from
        ics = self._generate_ics(class_id, class_topic, date, start_time, 90, timezone, "", sender_email, mentor_email, is_cancel=True)
        return self.send_email(mentor_email, subject, body, ics_content=ics, tenant_settings=tenant_settings)

email_notification_service = EmailNotificationService()
