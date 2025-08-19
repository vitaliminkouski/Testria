from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.models import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView

from mainapp.forms import CreateFolderForm, CreateSetForm, TestAnswerForm, QuestionForm
from mainapp.models import Folder, Set, Question, Answer, Block, TestSession


def index(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    sets = Set.objects.filter(author=request.user)
    data = {
        "user": request.user,
        "title": "Main page",
        "sets": sets,
        "folder_selected": -1,
    }
    return render(request, 'mainapp/set_list.html', data)


class CreateFolderView(LoginRequiredMixin, CreateView):
    model = Folder
    form_class = CreateFolderForm
    template_name = 'mainapp/create_update_folder.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New folder'
        context['button_title'] = 'Create'
        return context

    def form_valid(self, form):
        folder = form.save(commit=False)
        folder.author = self.request.user
        return super().form_valid(form)


class EditFolderView(LoginRequiredMixin, UpdateView):
    model = Folder
    form_class = CreateFolderForm
    context_object_name = 'folder'
    template_name = 'mainapp/create_update_folder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit folder'
        context['button_title'] = 'Save'
        return context

    def get_success_url(self):
        return reverse_lazy('folder_detail', kwargs={"pk": self.kwargs.get('pk')})


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    context_object_name = 'folder'
    template_name = 'mainapp/set_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = self.get_object()
        context['title'] = folder.name
        context['sets'] = Set.objects.filter(folder=folder).order_by('name')
        context['folder_selected'] = folder.pk
        return context


class DeleteFolderView(DeleteView):
    model = Folder
    context_object_name = 'folder'
    template_name = 'mainapp/folder_delete_confirm.html'
    success_url = reverse_lazy('home')


class CreateSetView(CreateView):
    model = Set
    form_class = CreateSetForm
    template_name = 'mainapp/create_set_form.html'

    def form_valid(self, form):
        set = form.save(commit=False)
        set.author = self.request.user

        folder_pk = self.kwargs.get('folder_pk')
        if folder_pk:
            try:
                folder = Folder.objects.get(pk=folder_pk)
                set.folder = folder
            except:
                messages.error(self.request, 'Folder with provided pk does not exist')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New folder'
        return context

    def get_success_url(self):
        return reverse_lazy('home')


class SetListView(ListView):
    model = Set
    template_name = 'mainapp/set_list.html'
    context_object_name = 'sets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Library'
        context['folder_selected'] = -1
        return context

    def get_queryset(self):
        return Set.objects.filter(author=self.request.user)


class DeleteSetView(LoginRequiredMixin, DeleteView):
    model = Set
    context_object_name = 'set'
    template_name = 'mainapp/delete_set_confirm.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirm delete'
        return context


TestAnswerFormSet = formset_factory(TestAnswerForm, extra=4, max_num=4)

@login_required
def create_test_question_view(request, set_id):
    set = get_object_or_404(Set, pk=set_id, author=request.user)
    if request.method == "POST":
        question_form = QuestionForm(request.POST, request.FILES)
        answers_formset = TestAnswerFormSet(request.POST, request.FILES)

        if question_form.is_valid() and answers_formset.is_valid():
            question_cd = question_form.cleaned_data
            correct_answer_num = int(question_cd.get("correct_answer"))

            # check form
            filled_answers_indexes = []
            for i, answer_form in enumerate(answers_formset, start=1):
                answer_cd = answer_form.cleaned_data
                text = answer_cd.get("text")
                image = answer_cd.get("image")
                if text or image:
                    filled_answers_indexes.append(i)

            if (len(filled_answers_indexes) < 2):
                messages.error(request, "You must fill at least two answers")
                data = {
                    "title": "New question",
                    "set": set,
                    "question_form": question_form,
                    "answer_formset": answers_formset
                }

                return render(request, "mainapp/create_test_question.html", data)
            elif (correct_answer_num not in filled_answers_indexes):
                messages.error(request, "Correct answer is not filled")
                data = {
                    "title": "New question",
                    "set": set,
                    "question_form": question_form,
                    "answer_formset": answers_formset
                }

                return render(request, "mainapp/create_test_question.html", data)

            # creating model objects
            try:
                with transaction.atomic():
                    question_block = Block.objects.create(
                        text=question_cd.get("text"),
                        image=question_cd.get("image")
                    )
                    question = Question.objects.create(
                        content=question_block,
                        set=set
                    )

                    for i, answer_form in enumerate(answers_formset):
                        answer_cd = answer_form.cleaned_data

                        text = answer_cd.get("text")
                        image = answer_cd.get("image")
                        if text or image:
                            answer_block = Block.objects.create(
                                text=text,
                                image=image
                            )
                            if(correct_answer_num==i):
                                Answer.objects.create(
                                    question=question,
                                    content=answer_block,
                                    is_correct=True
                                )
                            else:
                                Answer.objects.create(
                                    question=question,
                                    content=answer_block,
                                    is_correct=False
                                )

                return redirect('home')

            except:
                messages.error(request, "Error during creating question")
                data = {
                    "title": "New question",
                    "set": set,
                    "question_form": question_form,
                    "answer_formset": answers_formset
                }

                return render(request, "mainapp/create_test_question.html", data)


    else:
        question_form = QuestionForm()
        answers_formset = TestAnswerFormSet()

        data = {
            "title": "New question",
            "set": set,
            "question_form": question_form,
            "answer_formset": answers_formset
        }

        return render(request, "mainapp/create_test_question.html", data)

        messages.error(request, "Error during question creating")
        return redirect('home')


class EditSetView(LoginRequiredMixin, UpdateView):
    model = Set
    fields = ["name", "description"]
    template_name = "mainapp/edit_set.html"
    context_object_name = "set"

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['questions']=Question.objects.filter(set=self.get_object())
        return context

    def get_success_url(self):
        set=self.get_object()
        if set.folder:
            return reverse_lazy('folder_detail', kwargs={"pk": set.folder.pk})
        else:
            return reverse_lazy('set_list')

@login_required()
def start_test_view(request, set_id):
    test_set=get_object_or_404(Set, pk=set_id, type="test")

    active_session=TestSession.objects.filter(
        user=request.user,
        test_set=test_set,
    ).first()

    if active_session:
        return redirect('take_test_question', session_id=active_session.pk)

    session = TestSession.objects.create(
        user=request.user,
        test_set=test_set,
    )

    return redirect('take_test_question', session_id=session.pk)

@login_required()
def take_test_question_view(request, session_id):
    session=get_object_or_404(TestSession, pk=session_id, user=request.user)

    if session.is_completed:
        return redirect('test_results', session_id=session.pk)

    try:
        questions = session.test_set.questions.all()
        question=questions[session.next_question_num]
        answers=question.answers.all()

    except:
        messages.error(request, "Question not found")
        session.next_question_num += 1
        return redirect('take_test_question', session_id=session.pk)

    if request.method=="POST":
        answer_id=request.POST.get("answer")
        if not answer_id:
            messages.error(request, "Answer is not provided")
            session.next_question_num += 1
            return redirect('take_test_question', session_id=session.pk)

        correct_answer=answers.get(is_correct=True)
        if not correct_answer:
            messages.error(request, "Correct is not found")
            session.next_question_num += 1
            return redirect('take_test_question', session_id=session.pk)

        if correct_answer.pk==answer_id:
            is_answered_correct=True
        else:
            is_answered_correct=False

        data={
            "title": "Test",
            "is_feedback": True,
            "is_answered_correct": is_answered_correct,
            "correct_answer_id": correct_answer.pk,
            "selected_answer_id": answer_id,
            "question": question,
            "answers": answers,
            "session_id": session.pk
        }

        return render(request, "mainapp/test_question_pass.html", data)

    if session.next_question_num>questions.count():
        session.is_completed=True
        return redirect('test_results', session_id=session.pk)
    data={
        "title": "Test",
        "question": question,
        "answers": answers
    }
    session.next_question_num+=1
    return render(request, "mainapp/test_question_pass.html", data)



