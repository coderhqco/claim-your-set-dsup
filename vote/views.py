from locale import YESEXPR
from operator import contains
from urllib import request
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
from django.contrib.auth.mixins import LoginRequiredMixin

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
                ("We've sent an email to the address you provided."
                "Open it and click on the link to confirm and Enter the Floor."),
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
            messages.error(
                request, 
                'Invalid Credential. Check if you have entered the right district code.',
                extra_tags='danger'
            )
            return redirect('EnterTheFloor')

        login(request,authedUser)
        return redirect('voterPage')
    else:
      messages.error(request,"Invalid Credential", extra_tags='danger')
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
class HouseKeepingPod(LoginRequiredMixin,DetailView):
    model = voteModels.Pod
    template_name = 'vote/HouseKeeping.html'

    def post(self,request, *args, **kwargs):
        pod = voteModels.Pod.objects.get(code = request.POST['pod'])
        pod.code = pod_code_generator()
        pod.save()
        messages.success(request, "The pod key has been updated.", extra_tags="success")
        return redirect('pod', pk=pod.pk)

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # check if the user is the pod delegate
        pod = voteModels.Pod.objects.get(pk = self.kwargs['pk'])
        is_delegate = False
        condidate = pod.podmember_set.filter(is_member = False).first()
        for member in pod.podmember_set.all():
            if member.is_delegate and member.user == self.request.user:
                is_delegate = True

        voted = False
        userPod = pod.podmember_set.filter(user = self.request.user)
        print("userPOD: ", userPod.count())
        for i in userPod:
            print("user: ", i.user)
            print("user pod: ", i.pod)
            print("vote count: ", i.podmember_vote_in_set.all().count())
        # for i in userPod:
        #     print("userPOD: ", i.user)
        #     print("POD: ", i.pod)
        #     print("pod vote: ", i.podmember_vote_in_set.count())

        #     for a in i.podmember_vote_in_set.all():
        #         print("codidate: ", a.condidate)
        #         print("voter: ", a.voter)

        #     for vote_in in i.podmember_vote_in_set.all():
        #         if vote_in.voter == self.request.user:
        #             print("voted in ")
        #             voted = True

        #     for vote_out in i.podmember_vote_out_set.all():
        #         if vote_out.voter == self.request.user:
        #             print("voted out")
        #             voted = True

            
        # print("voted: ", userPod.podmember_vote_in_set.all())
        # for vote in pod.podmember_set
        context['title'] = "DSU - House Keeping Page"
        context['condidate'] = condidate
        context['is_delegate'] = is_delegate
        context['voted'] = voted
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
    """
    this function creates a pod. 
    it set the userType to 1.
    it set the user as a delegate pod member
    """
    # create a pod
    pod = voteModels.Pod.objects.create(code = pod_code_generator(), district = request.user.users.district)
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
        is_member = True,
        member_number = 1,
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
                        member_number = pods.first().podmember_set.count()+1
                    )
                    podMember.save()

                    # # set the userType to 1 as joining a pod\
                    # user=request.user
                    # user.users.userType = 1
                    # user.save()

                    messages.success(
                        request, 
                        ('In order to become a member of this Pod you need to be'
                         '‘voted in’ by a majority of the existing members. ' 
                         'You can wait and see if you are voted in, or you can contact '
                         'your F-Del IRL and ask them to start a vote among existing members.'),
                        extra_tags="success"
                    )
                    return redirect('pod', pk = pods.first().pk)
                else:
                    # else of pod is active 
                    messages.error(request, 'Pod is not accepting member anymore', extra_tags='danger')
                    return redirect('joinPod')
            else:
                # else of pod_obj
                messages.error(request, 'there is not pod with this code.',extra_tags='danger')
                return redirect('joinPod')
        else:  
            # else of form is_valid
            return render(request,'vote/joinPod.html', {'form':form})

    return render(request,'vote/joinPod.html', {'form':form})


def majorityVotes(pod, member):
    pod_members = pod.podmember_set.all()
    member_vote = member.podmember_vote_in_set.all()
    print("member vote in: ", member_vote.count())
    print("pod member: ", pod_members.count())
    if member_vote.count() >= (pod_members.count()/2):
        return True
    print("returned false...")
    return False


# vote members in a pod (IN, OUT)
@login_required(login_url='EnterTheFloor')
def podVoteIN(request):
    if request.method == "POST":
        """vote the member in to become a member of the pod
            check if the vote in is 50% + 1 to become the member (majority votes)
            make sure that members can only vote in/out once"""
        member = voteModels.PodMember.objects.get(pk = request.POST.get('member'))
        voteIN = voteModels.PodMember_vote_in.objects.create(condidate = member, voter = request.user)
        voteIN.save()
        print("condidate has got a vote in. \nchecking he has the majority to be accpeted into the pod...")
        # check if he/she has got the majority votes
        if majorityVotes(member.pod, member):
            member.is_member = True
            member.save()
            print("member has been accepted in the pod")
            # set the member.user.users.userType to 1 as ih becomes the member in a pod.
            userType = member.user
            userType.users.userType = 1
            userType.save()
            print("userType have been udpated...",userType.users.userType)

        messages.success(request,'Voted in', extra_tags='success')
        return redirect('pod', pk = member.pod.pk)


# check if the member shall be remove
def removePodMember(pod, member):
    # remove when only all the members of a pod vote_in or vote_out
    pod_members = pod.podmember_set.all().filter(is_member= True)

    vote_INs = member.podmember_vote_in_set.all()
    vote_OUTs = member.podmember_vote_out_set.all()

    if (vote_INs.count() + vote_OUTs.count()) == pod_members.count():
        # now that we have all members voted for this member, 
        # we have to check if the member has the majority of vote out to be removed
        if vote_OUTs.count() >= pod_members.count()/2:
            print("he has to be removed")
            return True
            
        print("all members has voted. but the vote outs are not major.")
    print("not valid to be removed")
    return False

@login_required(login_url='EnterTheFloor')
def podVoteOUT(request):
    if request.method == "POST":
        """ vote out the member. 
            check if the vote does not have the majority, he/she has to leave the pod
            leaving means that that record has to be removed from podmember """
        member = voteModels.PodMember.objects.get(pk = request.POST.get('member'))
        voteOUT = voteModels.PodMember_vote_out.objects.create(condidate = member, voter = request.user)
        voteOUT.save()
        print("voted out: ", voteOUT)

        if not majorityVotes(member.pod, member):
            # remove the member
            if removePodMember(member.pod, member):
                # now remove the member
                member.delete()
                print("due to majority vote out to this member, it has been removed..")
            
        messages.success(request,'Voted out', extra_tags='success')
        return redirect('pod', pk = member.pod.pk)


@login_required(login_url= 'EnterTheFloor')
def removePodMember(request):
    if request.method == 'POST':
        member = voteModels.PodMember.objects.get(pk = request.POST.get('member'))
        member.delete()
        print("member removed: now set the userType to 0", member)
        
        user = member.user
        user.users.userType = 0
        user.save()
        print("userTupe: ",member.user.users.userType)
        messages.error(request, 'removed...', extra_tags='success')
        return redirect('pod', pk = member.pod.pk)

    messages.error(request, 'something went wrong.', extra_tags='danger')
    return redirect('home')