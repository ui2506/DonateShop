from django.shortcuts import render, redirect

def faq(request):
    return redirect('show_faq', 'default')

def show_faq(request, name):
    return render(request, f'faq/{name}.html', { 'active': name })