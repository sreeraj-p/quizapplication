from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from quizweb.forms import RegistrationForm,LoginForm
from django.contrib.auth import authenticate,login
from django.views.generic import TemplateView,ListView
from quiz.models import Category,Questions,QuizRecord
import random

from django.views.generic import CreateView,View,FormView



class SignUpView(CreateView):
    form_class=RegistrationForm
    model=User
    template_name="register.html"
    success_url=reverse_lazy("signin")


    def form_valid(self, form):
         messages.success(self.request,"account has been created")
         return super().form_valid(form)
    def form_invalid(self, form):
         messages.error(self.request,"failed to create account")
         return super().form_invalid(form)
    


class SignInView(FormView):
    form_class=LoginForm
    template_name="login.html"


    def post(self,request,*args,**kwargs):
         form=LoginForm(request.POST)
         if form.is_valid():
              uname=form.cleaned_data.get("username")
              pwd=form.cleaned_data.get("password")
              usr=authenticate(request,username=uname,password=pwd)
              if usr:
                   login(request,usr)
                   return redirect("home")
         return render(request,self.template_name,{"form":form})
    


class HomeView(TemplateView):
     template_name="home.html"



class QuizHomeView(View):
     def get(self,request,*args,**kwargs):
          qs=Category.objects.all()
          return render(request,"quiz-home.html",{"cats":qs})
     

     def post(self,request,*args,**kwargs):
          print(request.POST)
          cat=request.POST.get("category")
          mode=request.POST.get("mode")
          print(cat,mode)
          return redirect("question-list",cat=cat,mode=mode)
     
from django.db.models import Sum

class QuestionListView(View):
     
     def get(self,request,*args,**kwargs):
          category=kwargs.get("cat")
          mode=kwargs.get("mode")
          qs=list(Questions.objects.filter(category__name=category,mode=mode))
          
          random.shuffle(qs)
          return render(request,"question-list.html",{"questions":qs})
     
     def post(self,request,*args,**kwargs):
          data=request.POST.dict()
          data.pop("csrfmiddlewaretoken")
          question_attended=len(data)
          marks_obtained=0
          wrong_ans_count=0
          right_answer_count=0
          for q,ans in data.items():
               question=Questions.objects.get(question=q)
               right_answer_obj=question.answer
               if(right_answer_obj.options==ans):
                    marks_obtained=marks_obtained+question.mark
               else:
                    wrong_ans_count +=1
               right_answer_count=question_attended-wrong_ans_count
          print(marks_obtained,question_attended,wrong_ans_count)
          category=kwargs.get("cat")
          mode=kwargs.get("mode")
          total=Questions.objects.filter(category__name=category,mode=mode).aggregate(Sum('mark')).get('mark__sum')
          result=''
          if marks_obtained>=total/2:
               result="passed"
          else:
               result="failed"

          data=QuizRecord.objects.create(marks_obtained=marks_obtained,right_answer_count=right_answer_count,wrong_answer_count=wrong_ans_count,user=request.user)
          return render(request,'quiz-mark.html',{"marks_obtained":marks_obtained,"questions_attended":question_attended,"wrong_answer_count":wrong_ans_count,"result":result})
     



class QuizRecordView(ListView):
     model=QuizRecord
     template_name="quiz-record.html"
     context_object_name="records"


     def get_queryset(self):
          return QuizRecord.objects.filter(user=self.request.user)
     

                   


