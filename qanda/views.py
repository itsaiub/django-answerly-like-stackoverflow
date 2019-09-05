from django.shortcuts import render, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView, DayArchiveView, RedirectView
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone
from . import models
from . import forms
# Create your views here.


class AskQuestionView(LoginRequiredMixin, CreateView):
    form_class = forms.QuestionForm
    template_name = 'qanda/ask.html'

    def get_initial(self):
        return {
            'user': self.request.user.id
        }

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            # save and rediret as usual
            return super().form_valid(form)

        elif action == 'PREVIEW':
            preview = models.Question(
                question=form.cleaned_data['question'],
                title=form.cleaned_data['title']
            )
            ctx = self.get_context_data(preview=preview)
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()


class QuestionDetailView(DetailView):
    model = models.Question
    template_name = 'qanda/question_detail.html'

    ACCEPT_FORM = forms.AnswerAcceptanceForm(initial={'accepted': True})
    REJECT_FORM = forms.AnswerAcceptanceForm(initial={'accepted': False})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'answer_form': forms.AnswerForm(initial={
                'user': self.request.user.id,
                'question': self.object.id,
            })
        })
        if self.object.can_accept_answers(self.request.user):
            ctx.update({
                'accept_form': self.ACCEPT_FORM,
                'reject_form': self.REJECT_FORM,
            })
        return ctx


class CreateAnswerView(LoginRequiredMixin, CreateView):
    form_class = forms.AnswerForm
    template_name = 'qanda/create_answer.html'

    def get_initial(self):
        return {
            'question': self.get_question().id,
            'user': self.request.user.id
        }

    def get_context_data(self, **kwargs):
        return super().get_context_data(question=self.get_question(), **kwargs)

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            # save and redirect as usual
            return super().form_valid(form)
        elif action == 'PREVIEW':
            ctx = self.get_context_data(
                preview=form.cleaned_data['answer']
            )
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()

    def get_question(self):
        return models.Question.objects.get(pk=self.kwargs['pk'])


class UpdateAnswerAcceptance(LoginRequiredMixin, UpdateView):
    form_class = forms.AnswerAcceptanceForm
    queryset = models.Answer.objects.all()

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_invalid(self, form):
        return HttpResponseRedirect(
            redirect_to=self.object.question.get_absolute_url()
        )


class DailyQuestionList(DayArchiveView):
    queryset = models.Question.objects.all()
    date_field = 'created'
    month_format = '%m'
    allow_empty = True

    template_name = 'qanda/question_archive_day.html'


class TodayQuestionList(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = timezone.now()
        return reverse(
            'qanda:daily_questions',
            kwargs={
                'day': today.day,
                'month': today.month,
                'year': today.year
            }
        )
