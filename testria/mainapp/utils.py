from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from mainapp.forms import CreateFolderForm
from mainapp.models import Folder


class CreateFolderMixin(LoginRequiredMixin, CreateView):
    model=Folder
    form_class = CreateFolderForm
    template_name = 'mainapp/create_folder.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['title']='New folder'
        return context

    def form_valid(self, form):
        folder=form.save(commit=False)
        folder.author=self.request.user
        return super().form_valid(form)