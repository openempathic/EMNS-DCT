from django.shortcuts import render, redirect
from django.contrib import messages

from .form import UserResisterForm

def register(request):
    if request.method == 'POST':
        form = UserResisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}.")
            return redirect('audio-recorder-record')

    else:
        form = UserResisterForm()

    return render(request, 'users/register.html', {'form':form})
