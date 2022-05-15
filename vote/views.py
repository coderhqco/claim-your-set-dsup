from optparse import Values
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import DetailView
from vote import models as voteModels
from vote import forms as voteForms
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from vote.token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_list_or_404, get_object_or_404

def entry_code_generator():
    """
    this is the entry code generator. 
    It uses random and checks for the database. 
    return the code if it's not taken
    """
    import random
    code  = str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code = code.upper()
    is_exist = User.objects.filter(username = code).exists()
    
    if is_exist:
        entry_code_generator()
    return code


def ClaimYourSeat(request):
    """this is the user creation function. It create a user and assign entry code and relevent info"""
    form = voteForms.ClaimYourSeatForm()
    if request.method == 'POST':
        form = voteForms.ClaimYourSeatForm(request.POST or None)
        if form.is_valid():
            # set the username to 5 digit random unique and set password
            user = form.save(commit=False)
            user.username = entry_code_generator()
            user.email = form.cleaned_data.get('email')
            user.is_active = False
            user.save()

            user.users.legalName = form.cleaned_data.get('legalName')
            user.users.address = form.cleaned_data.get('address')
            usersDistrict = voteModels.Districts.objects.get(code = form.cleaned_data.get('district').upper())
            if usersDistrict:
                user.users.district = usersDistrict
            
            # set the is_reg true of the user is going to vote within 30 days
            if request.POST.get('is_reg1'):
                user.users.is_reg = True

            user.save()
            messages.success(
                request,
                "We've sent an email to the address you provided. Open it and click on the link to confirm and Enter the Floor.",
                extra_tags='success' 
            )

            # send email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('vote/accountActiveEmail.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage( mail_subject,  message,  to=[to_email] )
            email.send()

            # redirect to confirmation page
            return render(request, 'vote/signUpConfirm.html')
        else:
            return render(request, 'vote/ClaimYourSeat.html',{'form':form})
    return render(request, 'vote/ClaimYourSeat.html',{'form':form})


def activate(request, uidb64, token):
    """after the claiming your seat, this function handles the activation of user via email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        users = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        users = None
    if users is not None and account_activation_token.check_token(users, token):
        users.is_active = User.objects.filter(id=uid).update(is_active=True, is_staff= True)
        login(request, users)
        messages.success(request,"Successfully Registered and Activated.")
        return render(request, 'vote/activationConfirmation.html',{'entry_code':users.username})
    else:
        return HttpResponse('Activation link is invalid!')

        
def EnterTheFloor(request):
  """
  this is the login function. it asks for a POST request 
  and looks for districts code, entry_code and password.
  """
  if request.method == "POST":
    district = request.POST.get('district').upper()
    userName = request.POST.get('userName').upper()
    upass = request.POST.get('password')
    authedUser = authenticate(request,  username=userName, password=upass)

    if authedUser is not None:

        # authenticate if has the same district code
        if authedUser.users.district.code != district:
            messages.error(request, 'Invalid Credential. Check if you have entered the right district code.')
            return redirect('EnterTheFloor')

        login(request,authedUser)
        return redirect('voterPage')
    else:
      messages.error(request,"Invalid Credential")
      return redirect('EnterTheFloor')
          
  return render(request,"vote/EnterTheFloor.html")

def userLogout(request):
  logout(request)
  return redirect('/')

@login_required(login_url = 'EnterTheFloor')
def voterPage(request):
    podMember = False

    # get the user if he/she is a member of a pod
    if request.user.users.userType ==1:
        podMember = voteModels.PodMember.objects.get(user = request.user)
        
    data={
        'pod': podMember,
        'title': 'Voter Page',
    }
    return render(request, 'vote/VoterPage.html',data)   
    


# this the home page of a pod
class HouseKeepingPod(DetailView):
    model = voteModels.Pod
    template_name = 'vote/HouseKeeping.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "House Keeping Page"
        return context


def pod_code_generator():
    """
    this is the pod code generator. 
    It uses random and checks for the database. 
    return the code if it's not taken
    """
    import random
    code  = str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code = code.upper()
    is_exist = voteModels.Pod.objects.filter(code = code).exists()
    
    if is_exist:
        pod_code_generator()
    return code

@login_required(login_url='EnterTheFloor')
def CreatePod(request):
    # check the request.user if the user can create a pod
    # check if the user has not being a member of any kind. 
    
    # create a pod
    pod = voteModels.Pod.objects.create(code = pod_code_generator())
    pod.save()

    # set the userType attribute of the creator to 1
    user = request.user
    user.users.userType +=1
    user.save()

    # add the user to pod member as delegate
    pod_member_obj = voteModels.PodMember.objects.create(
        user = request.user, 
        pod = pod, 
        is_delegate = True,
        is_member = True
    )
    pod_member_obj.save()

    return redirect('pod', pk = pod.pk)


def pod_joining_validation(user,pod):
    """
    this function validate weather a user can enter a pod.
    It check if pod is active.
    It check if user is already a member
    It check if userType is 0
    """
    result = True
    if not pod.is_active():
        result = False

    podmembers = pod.podmember_set.all()
    if podmembers.filter(user = user):
        result = False
    
    if user.users.userType > 0:
        result = False
        
    return result


@login_required(login_url='EnterTheFloor')
def joinPod(request):
    form = voteForms.JoinPodMemberForm()
    if request.method =="POST":
        form = voteForms.JoinPodMemberForm(request.POST or None)
        if form.is_valid():
            invitationCode = form.cleaned_data.get('invitationCode').upper()
            # check if pod exist
            pods = voteModels.Pod.objects.filter(code = invitationCode)
            if pods.exists():
                # check if user can join the pod
                if pod_joining_validation(request.user, pods.first()):
                    podMember = voteModels.PodMember.objects.create(
                        user = request.user,
                        pod = pods.first(),
                        is_member = False,
                        is_delegate = False,
                    )
                    podMember.save()
                    return redirect('pod', pk = pods.first().pk)
                else:
                    # else of pod is active 
                    messages.error(request, 'Pod is not accepting member anymore')
                    return redirect('joinPod')
            else:
                # else of pod_obj
                messages.error(request, 'there is not pod with this code.')
                return redirect('joinPod')
        else:  
            # else of form is_valid
            return render(request,'vote/joinPod.html', {'form':form})

    return render(request,'vote/joinPod.html', {'form':form})