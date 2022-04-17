from email.message import EmailMessage
from lib2to3.pgen2.tokenize import generate_tokens
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User #for save in the database
# for authunication
from django.contrib.auth import authenticate,login,logout
# for message
from django.contrib import messages
from login import settings
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode

# Create your views here.
def home(request):
    return render(request,"loginapp/index.html")

def signup(request):

    if request.method=="POST":

        # username=request.POST.get('username')
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        password=request.POST['password']
        confirm=request.POST['pass2']

        # VALIDATION
        if User.objects.filter(username=username):
            messages.error(request,"username already eexist")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request,"email already exist ")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request,"username must be under 10 characters")

        if password!=confirm:
            messages.error(request,"please enter right password")


        if not username.isalnum():
            messages.error(request,"username must be alpha numeric")
            return redirect('home')

        
        myuser=User.objects.create_user(username,email,password)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.is_active=False
        myuser.save()

        messages.success(request,"hurray your  account has been succesfully created.")

        # here i write code for email

        subject="welcome to mahajan coder app"
        message="hello"+myuser.first_name+"!! \n"+ "welcome to mahajan coder \n thank you for visiting in our website\n we have sent you the confiramtion link please click on it to activate your account\n \n thank you"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True) #fail silently =true means if fail to send in that case not crash
#email for confirmation
        current_site=get_current_site(request)
        email_subject="confirm your account"
        message2=render_to_string('email_confiramtion.html',{'name':myuser.first_name,'domain':current_site.domain,'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),'token':generate_token.make_token(myuser)})

        email=EmailMessage(
            email_subject,message2,settings.EMAIL_HOST_USER,[myuser.email],
        )
        email.fail_silently=True
        email.send()
        return redirect('signin')

    return render(request,"loginapp/signup.html")

def signin(request):

    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']


        # we will authunicate this user
        user=authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,"loginapp/index.html",{'fname':fname})
        else:
            messages.error(request,"bad input")
            return redirect('home')
    return render(request,"loginapp/signin.html")

def signout(request):
    logout(request)
    messages.success(request,"Logged out succesfully")
    return redirect('home')



def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None
    
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')
    

    
