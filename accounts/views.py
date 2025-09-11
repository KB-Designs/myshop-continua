from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm as SignUpForm
from django.contrib.auth import login, authenticate

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # save user
            # authenticate with cleaned data
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(
                request,
                username=user.username,
                password=raw_password
            )
            if user is not None:
                login(request, user)  # now backend is set ✅
            return redirect("shop:product_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

