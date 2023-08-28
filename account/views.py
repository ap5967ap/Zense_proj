import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login as l, logout, authenticate, get_user_model
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .decorators import user_not_authenticated
from .forms import SetPasswordForm
from .tokens import account_activation_token
from .models import Account
from balance.models import Balance

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
    balance=Balance.objects.create(user=user)
    balance.save()
    return redirect('login')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        system_messages = messages.get_messages(request)
        for message in system_messages:
            pass
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
                received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(
            request, f'Problem sending email to {to_email}, check if you typed it correctly.')

@user_not_authenticated(redirect_url='home')#TODO: user dashboard
def register(request):
    if request.method == "POST":
            e1=e2=e3=e4=e5=e6=e7=''
            first=request.POST.get('first')
            last=request.POST.get('last')
            dob=datetime.datetime.strptime(request.POST.get('dob'),'%Y-%m-%d').date()
            pan=request.POST.get('pan').upper()
            phone=request.POST.get('phone')
            email=request.POST.get('email')
            username=request.POST.get('username')
            password1=request.POST.get('password1')
            password2=request.POST.get('password2')
            if not (first and last): 
                e1='Name cannot be empty'
            if dob >= datetime.datetime.now().date() or (not dob):
                e2="Date of birth cannot be greater than today's date"
            if len(pan)!=10:
                e3='Invalid PAN'
            if Account.objects.filter(pan__iexact=pan).exists():
                e3='PAN already exists'
            if len(phone)!=10:
                e4='Invalid Phone Number'
            if Account.objects.filter(email__iexact=email).exists():
                e5='Email already exists'
            if Account.objects.filter(username__iexact=username).exists():
                e6='Username already exists'
            if password1!=password2:
                e7='Passwords do not match'
            if e1 or e2 or e3 or e4 or e5 or e6 or e7:
                return render(request,'register.html',{'e1':e1,'e2':e2,'e3':e3,'e4':e4,'e5':e5,'e6':e6,'e7':e7})
            else:
                try:
                    user=Account.objects.create_user(first_name=first,last_name=last,username=username,email=email,dob=dob,pan=pan,phone=phone,password=password1)
                    user.is_active=False
                    user.save()
                    activateEmail(request,user,email)
                    return redirect('login')
                except:
                    return render(request,'register.html',{'e8':'Password must contain at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character'})

    else:
        return render(request=request,template_name="register.html")



@login_required(login_url='/account/login/')
def custom_logout(request):
    logout(request)
    return redirect("home")

@user_not_authenticated(redirect_url='home')#TODO: user dashboard
def login(request):
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            l(request, user)
            return redirect("income_summary") #TODO: user dashboard

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request=request,template_name="login.html")
    
@login_required(login_url='/account/login/')
def profile(request, username):
    user = get_user_model().objects.get(username=username)
    return HttpResponse(f"Hello {user.username}")

@login_required(login_url='/account/login/')
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            pass

    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})

@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
            user_email = request.POST.get('username')
            associated_user = get_user_model().objects.filter(Q(email=user_email) | Q(username=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, SERVER PROBLEM")
            else:
                messages.error(request, "User does not exist")
            return redirect('login')


    return render(request=request, template_name="password_reset.html")

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            password=request.POST.get('password1')
            confirm_password=request.POST.get('password2')
            if password!=confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect('password_reset_confirm',uidb64=uidb64,token=token)
            else:
                user.set_password(password)
                user.save()
                messages.success(request, "Your password has been set. You may go ahead and log in now.")
                return redirect('login')
        else:
            return render(request, 'password_reset_confirm.html', {'uid': uidb64, 'token': token })
    else:
        messages.error(request, "Link is expired")
    messages.error(request, "An error occured")
    return redirect("login")