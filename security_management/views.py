# Profile management views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UserProfileForm, CustomPasswordChangeForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'security_management/pages/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'security_management/pages/login.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            password_form = CustomPasswordChangeForm(user=user)
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        
        elif 'change_password' in request.POST:
            profile_form = UserProfileForm(instance=user)
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)
            
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout after password change
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = CustomPasswordChangeForm(user=user)
    
    context = {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'security_management/pages/profile.html', context)

def logout_view(request):
    logout(request)
    return render(request, 'security_management/pages/logged_out.html')
