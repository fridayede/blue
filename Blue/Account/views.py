import email


from datetime import datetime, timedelta 
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login

# from Blue.common.task import send_email
from common.task import send_email


from .models import User,pendingUser,Token
from RE.models import Referral
from . models import TokenType

from django.shortcuts import render,redirect
# for decorator
from functools import wraps


# for generating random verification code
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password 






def register_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('can_verify'):
            messages.error(request, "You must register first.")
            return redirect("/Account/login/")
        return view_func(request, *args, **kwargs)
    return wrapper






def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("/Account/login/")

        try:
            if not email.endswith("@gmail.com"):
                messages.error(request, "Only Gmail addresses are allowed.")
                return redirect("/Account/login/")

            user = authenticate(request, username=email, password=password)

            if user:
                auth_login(request, user)  # ✅ fixed
                return redirect("Home:clam")
            else:
                messages.error(request, "Invalid email or password.")
                return redirect("/Account/login/")

        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong.")
            return redirect("/Account/login/")

    return render(request, 'login.html')








def register(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        comfirm_password=request.POST.get("confirm_password")

        ref_code = request.GET.get("ref")

        if ref_code:
            request.session["ref_code"] = ref_code


        try:
           
            if not email or not password or not comfirm_password:
                messages.error(request, "All fields are required.")
                return redirect("/Account/register/")
        
            if not email.endswith("@gmail.com"):
                    messages.error(request, "Only Gmail addresses are allowed.")
                    return redirect("/Account/register/")
        

            if password != comfirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect("/Account/register/")

            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with that email already exists.")
                return redirect("/Account/register/")

        except Exception as e:
            print(e)
            messages.error(request, f"An error occurred: {e}")
            return redirect("/Account/register/")


        try:
            code = get_random_string(length=6, allowed_chars="AEIOU0123456789")
            pendingUser.objects.update_or_create(
                email=email, 
                defaults={"verification_code": code,
                          "password": make_password(password),
                        #   "password": password1,
                        #   "name": name,
                           'created_at': timezone.now() ,
                          'is_verified': False
                          }
            )
            send_email(
            subject="Verify your email....",
            email_to=[email],
            
            # serialized_data={"verification_code": code},
            context={"verification_code": code},
           
        )
            # ✅ IMPORTANT: allow access to verify page
            request.session['can_verify'] = True
            request.session['verify_email'] = email
            messages.success(request, "Verification code sent to your email.")
            return redirect("/Account/verifyEmail/")
        except Exception as e2:
            print(f"An error occurred in registration: {e2}")
            messages.error(request, f"An error occurred:")
            return redirect("/Account/register/")
    return render(request,'register.html')


# @register_required
# def verifyEmail(request):
#     if request.method == "POST":
#         # email = request.POST.get("email")
#         code = request.POST.get("verification_code")

#         if not request.session.get('can_verify'):
#             return redirect("/Account/login/")

#         # 🔒 extra safety (email must match registration)
#         session_email = request.session.get('verify_email')

#         if not session_email:
#             messages.error(request, "Session expired. Please register again.")
#             return redirect("/Account/register/")

#         try:
#             pending_user = pendingUser.objects.filter(email=session_email, verification_code=code).first()
#             if pending_user:
#                 User.objects.create(
#                     email=pending_user.email,
#                     password=pending_user.password
#                         # name=pending_user.name,
#                     )
#                 pending_user.delete()
#                  # 🚫 REMOVE permission after success
#                 request.session.pop('can_verify', None)
#                 request.session.pop('verify_email', None)
#                 messages.success(request, "Email verified successfully. You can now log in.")
#                 return redirect("/Account/login/")
#             else:
#                 messages.error(request, "Invalid verification code.")
#                 return redirect("/Account/verifyEmail/")
#         except Exception as e:
#             print(f"An error occurred during email verification: {e}")
#             messages.error(request, f"An error occurred: ")
#             return redirect("/Account/verifyEmail/")

#     return render(request, "verifyEmail.html")






@register_required
def verifyEmail(request):
    if request.method == "POST":
        # email = request.POST.get("email")
        code = request.POST.get("verification_code")

        if not request.session.get('can_verify'):
            return redirect("/Account/login/")

        # 🔒 extra safety (email must match registration)
        session_email = request.session.get('verify_email')

        if not session_email:
            messages.error(request, "Session expired. Please register again.")
            return redirect("/Account/register/")

        try:
            pending_user = pendingUser.objects.filter(
                email=session_email,
                verification_code=code
            ).first()

            if pending_user:

                # =========================
                # 1. CREATE USER
                # =========================
                user = User.objects.create(
                    email=pending_user.email,
                    password=pending_user.password
                )

                pending_user.delete()

                # =========================
                # 2. CREATE REFERRAL ENTRY
                # =========================
                from .models import Referral  # safe local import

                Referral.objects.create(user=user)

                # =========================
                # 3. HANDLE REFERRAL LINK
                # =========================
                ref_code = request.session.get("ref_code")

                if ref_code:
                    try:
                        referrer = Referral.objects.get(code=ref_code)

                        my_referral = Referral.objects.get(user=user)

                        my_referral.referred_by = referrer.user
                        my_referral.save()

                        referrer.referral_count += 1
                        referrer.save()

                    except Referral.DoesNotExist:
                        pass

                # =========================
                # 4. CLEAN SESSION
                # =========================
                request.session.pop('can_verify', None)
                request.session.pop('verify_email', None)
                request.session.pop('ref_code', None)

                messages.success(
                    request,
                    "Email verified successfully. You can now log in."
                )
                return redirect("/Account/login/")

            else:
                messages.error(request, "Invalid verification code.")
                return redirect("/Account/verifyEmail/")

        except Exception as e:
            print(f"An error occurred during email verification: {e}")
            messages.error(request, f"An error occurred: ")
            return redirect("/Account/verifyEmail/")

    return render(request, "verifyEmail.html")



def resetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:

            if not email:
                print("1")
                messages.error(request, "Email requird")
                return redirect("/Account/resetPassword/")
            if not email.endswith("@gmail.com"):
                messages.error(request, "Only Gmail addresses are allowed.")
                return redirect("/Account/resetPassword/")
            try:
                user = User.objects.get(email=email)

            
            except Exception as a:
                print(a)
                print("2")
                messages.error(request,"invalid details try again")
                return redirect("/Account/resetPassword/")
            if user:
                token_value = get_random_string(length=6, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

            Token.objects.create(
            user=user,
            token=token_value,
            token_type=TokenType.PASSWORD_RESET
            )

            send_email(
            subject="Password Reset Code",
            email_to=[email],
            serialized_data={"token": token_value},
            context={"token": token_value}
            )
            request.session['can_verify'] = True
            request.session['newPassword'] = email
            return redirect("/Account/newPassword/")
        except Exception as over:
            print(over)
            return redirect("/Account/resetpassword/")
    return render(request, 'resetPassword.html')








def newPassword(request):
    if request.method == "POST":
        token = request.POST.get("token")
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not request.session.get('can_verify'):
            return redirect("/Account/login/")

        session_email = request.session.get('newPassword')

        if not session_email:
            messages.error(request, "Session expired. Please try again.")
            return redirect("/Account/resetPassword/")

        try:
            user = User.objects.get(email=session_email)
            token_obj = Token.objects.filter(user=user, token=token, token_type=TokenType.PASSWORD_RESET).first()

            if not token_obj:
                messages.error(request, "Invalid or expired token.")
                return redirect("/Account/newPassword/")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect("/Account/newPassword/")

            user.password = make_password(new_password)
            user.save()
            token_obj.delete()
             # 🚫 REMOVE permission after success
            request.session.pop('can_verify', None)
            request.session.pop('newPassword', None)
            messages.success(request, "Password reset successfully. You can now log in.")
            return redirect("/Account/login/")
        except Exception as e:
            print(f"An error occurred during password reset: {e}")
            messages.error(request, f"An error occurred: ")
            return redirect("/Account/newPassword/")

    return render(request, "newPassword.html")





from django.contrib.auth import logout


def logout(request):
    return redirect("Account:login")  # change "login" to your login URL name