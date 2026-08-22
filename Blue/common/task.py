



# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# import resend

# resend_Api ='re_CNzxswcn_PhRKUV2q5fhKUTeC1thuu76k'

# EMAIL_FROM ="edepaul148@gmail.com"
# def send_email(subject: str, email_to: list[str], serialized_data: dict = None, context: dict = None):
#     # Extract verification code or token
#     verification_code = None
#     token = None
#     if isinstance(serialized_data, dict):
#         verification_code = serialized_data.get("verification_code") or serialized_data.get("token")

#     # TEXT VERSION OF EMAIL
#     if verification_code:
#         body_text = f"Your verification code is: {verification_code }  "
#     elif token:
#         body_text= f"Your verification code is: {token }  "
#     else:
#         body_text = "Check the HTML version of this email."

#     # HTML VERSION OF EMAIL
#     body_html = ""
#     if context:
#         body_html = render_to_string("massage.html", context)

#     # Create email message
#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=body_text,
#         from_email=EMAIL_FROM,
#         to=email_to,
#     )

#     # Attach HTML if available
#     if body_html:
#         msg.attach_alternative(body_html, "text/html")

#     # Send email
#     msg.send(fail_silently=False)
  




  
from django.template.loader import render_to_string
import resend

resend.api_key ='re_Jw2Uyu8j_6i2su3Nn5351xhJQqotVtXDB'

# Email_from = "edepaul148@gmail.com"
Email_from = "onboarding@resend.dev"


def send_email(subject,email_to, serialized_data=None, context=None):
    verification_code = None
    token = None
    if isinstance(serialized_data,dict):
        verification_code = serialized_data.get("verification_code")
        token = serialized_data.get("token")

    if verification_code:
        body_text =f"Your verification code is {verification_code}"

    elif token:
        body_text =f"Your verification code is {token}"

    else:
        body_text="welcome"

    # body_html = ""

    body_text =  render_to_string("massage.html",context or {})


    resend.Emails.send({
        "from": Email_from,
        "to": email_to,
        "subject": subject,
        "text": body_text,
    })

        

