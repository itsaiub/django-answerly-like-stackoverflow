from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseBadRequest

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
