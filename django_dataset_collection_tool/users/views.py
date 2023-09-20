from django.http import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import UserResisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserResisterForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, f"{form.cleaned_data.get('username')} Account created. Please contact your administrator to assign you a role.")
            return redirect('profile')
    else:
        form = UserResisterForm()

    return render(request, 'users/register.html', {'form':form})

def terms(request):
    return render(request, 'users/terms.html')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            request.user.age = request.user.profile.age = u_form['age'].value()
            request.user.gender = request.user.profile.gender = u_form['gender'].value()
            request.user.email = request.user.profile.email = u_form['email'].value()
            request.user.first_name = request.user.profile.first_name = u_form['first_name'].value()
            request.user.last_name = request.user.profile.last_name = u_form['last_name'].value()
            request.user.groups.add(Group.objects.get(name='viewer'))
            request.user.groups.add(Group.objects.get(name='nld'))

            u_form.save()
            p_form.save()

            messages.success(request, f"Profile has been updated.")
            return redirect('random-sample')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form':u_form,
        'p_form':p_form
    }

    return render(request, 'users/profile.html', context)