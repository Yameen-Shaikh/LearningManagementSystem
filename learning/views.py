from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Subject, Chapter, Topic
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('subject_list')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})

@login_required
def level_select(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    levels = Chapter.objects.filter(subject=subject).values_list('level', flat=True).distinct()
    return render(request, 'level_select.html', {'subject': subject, 'levels': levels})

@login_required
def chapter_list(request, subject_id, level):
    subject = get_object_or_404(Subject, pk=subject_id)
    chapters = Chapter.objects.filter(subject=subject, level=level)
    return render(request, 'chapter_list.html', {'subject': subject, 'level': level, 'chapters': chapters})

@login_required
def topic_list(request, chapter_id):
    chapter = get_object_or_404(Chapter.objects.prefetch_related('topic_set__links'), pk=chapter_id)
    topics = chapter.topic_set.all()
    return render(request, 'topic_list.html', {'chapter': chapter, 'topics': topics})
