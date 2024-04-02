from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
import random

from django.utils.safestring import mark_safe  # Import mark_safe function
import markdown2  # Import Markdown converter

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title):
    content = util.get_entry(title)
    if content == None:
        return render(request, "encyclopedia/notFound.html")
    html_content = markdown2.markdown(content)  # Convert Markdown to HTML
    return render(request, "encyclopedia/entryPage.html", {
        "title": title.capitalize(),
        "content": mark_safe(html_content)
    })

def search(request):
    entries = util.list_entries()
    entries_lower = [entry.lower() for entry in entries]
    substrings= []
    if 'q' in request.GET:
        query = request.GET["q"].lower()
        for entry in entries_lower:
            if query in entry:
                if entry in ["html", "css"]:
                    substrings.append(entry.upper())
                else:
                    substrings.append(entry.capitalize())
        if query in entries_lower:
            return redirect('encyclopedia:title', title=query)
        else:
            return render(request, "encyclopedia/search.html", {
                "results": substrings
            })
        

class NewPageForm(forms.Form):
    title = forms.CharField()
    markdown = forms.CharField(widget=forms.Textarea(attrs={"id": "markdown", "name": "markdown"}))

def create(request):
    entries = util.list_entries()
    exists = False
    if request.method == "POST":
        form = NewPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            for entry in entries:
                if title.lower() == entry.lower():
                    exists = True
                    return render(request, "encyclopedia/newPage.html",{
                         "form": form,
                        "exists": exists
                    })
            markdown = form.cleaned_data["markdown"]
            util.save_entry(title.capitalize(),markdown)
            return HttpResponseRedirect(reverse("encyclopedia:title", args=[title]))
        else:
            return render(request, "encyclopedia/newPage.html",{
                "form": form,
                "exists": exists
             })
    return render(request, "encyclopedia/newPage.html",{
        "form": NewPageForm()
    })

class EditPageForm(forms.Form):
    markdown = forms.CharField(widget=forms.Textarea(attrs={"id": "markdown", "name": "markdown"}))


def edit(request,title):
    content = util.get_entry(title)
    form = EditPageForm(initial={'markdown': content})
    
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["markdown"]
            util.save_entry(title, new_content)
            return HttpResponseRedirect(reverse("encyclopedia:title", args=[title]))
        else:
            return render(request, "encyclopedia/editPage.html",{
                "title": title.capitalize(),
                "form": form
            })
    return render(request, "encyclopedia/editPage.html",{
        "title": title.capitalize(),
        "form": form
    })

def randomPage(request):
    entries = util.list_entries()
    randomPage = random.randint(0, len(entries) - 1)
    return redirect('encyclopedia:title', title=entries[randomPage])

