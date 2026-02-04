# programs/emails.py

import sib_api_v3_sdk
from django.conf import settings
from django.template.loader import render_to_string
from sib_api_v3_sdk.rest import ApiException

def send_brevo_email(subject, template_name, context, to_email):
    print(f"DEBUG: Attempting to send email to {to_email}...")
    
    html_content = render_to_string(template_name, context)
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": settings.DEFAULT_FROM_EMAIL, "name": "Gym System"},
        subject=subject,
        html_content=html_content,
    )  

    try:
        # Puraana: send_trans_email
        # Naya (Correct): send_transac_email
        api_instance.send_transac_email(send_smtp_email) 
        print("DEBUG: Email successfully sent to Brevo API!")
        return True
    except ApiException as e:
        print(f"Brevo API Error: {e}")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        return False