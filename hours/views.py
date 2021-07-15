from django.shortcuts import render, get_object_or_404

from .forms import UserRegisterForm, ProfileRegisterForm, UserUpdateForm, ProfileUpdateForm, NewHoursForm
from django.contrib import messages
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,


)
from .models import Post, User, Category, Profile
from django.db.models import Sum
from datetime import datetime, timedelta

from django.http import HttpResponse  # for pdf
from django.views.generic import View  # for pdf
from .utils import render_to_pdf  # for pdf

# Home Page View
def home(Request):
    return render(Request, 'b_home.html', {'title': 'Home'})  # Call home html page and add title

# About Page View
def about(Request):
    return render(Request, 'c_about.html', {'title': 'About'})  # Call About html page and add title

# Register Page View, shows register page and its perks such as the form and data storage in table
def register(request):
    if request.method == 'POST': # Create Account
        form = UserRegisterForm(request.POST)   # User table
        p_reg_form = ProfileRegisterForm(request.POST)   # Profile table

        if form.is_valid() and p_reg_form.is_valid(): # Checks if filled in information is valid
            user = form.save()
            p_reg_form = ProfileRegisterForm(request.POST, instance=user.profile)
            p_reg_form.full_clean()
            p_reg_form.save()
            messages.success(request, f'Your account has been created! you are now able to log in!')
            return redirect('login')

    else: # Display Blank Register Forms for User to fill in when creating account
        form = UserRegisterForm()   # User table
        p_reg_form = ProfileRegisterForm()   # Profile table
    context = {
        'form': form,
        'p_reg_form': p_reg_form

    }
    return render(request, 'd_register.html', context) # Call register html page

# Checks if user is logged in
@login_required
# Profile Page functions including getting both both user and profile forms for all basic data,
# save functions, return message success messages, and redirection.
def profile(request):
    if request.method == 'POST': # Create Profile
        u_form = UserUpdateForm(request.POST, instance=request.user)   # Update user table
        p_form = ProfileUpdateForm(request.POST,   # Update profile table
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid(): # Check if filled in forms are valid
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')    # Return Message
            return redirect('profile') # Redirection to Profile page after updating
    else: # Display Blank Profile Forms for User to fill in when updating account
        u_form = UserUpdateForm(instance=request.user)   # Display user table
        p_form = ProfileUpdateForm(instance=request.user.profile)   # Display profile table
    # pass forms to corresponding html
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'g_profile.html', context) # Call profile html page

#  Allows user to log hours. New Hours View containing Post table in database and new hours form.
class NewHoursView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = NewHoursForm
    template_name = 'l_new_hours.html'

    # Set created logs to the current logged in user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# My Hours View
class MyHoursView(ListView):
    model = Post
    template_name = 'm_post_my.html'
    context_object_name = 'posts'
    ordering = ['-service_date']
    paginate_by = 5 # 5 logs per page

    # Get logged in user's data only
    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Post.objects.filter(user=user).order_by('-service_date')

    # Pass logged in user's data to html
    def get_context_data(self, **kwargs):
        context = super(MyHoursView, self).get_context_data(**kwargs)
        posts = Post.objects.filter(user=self.request.user).order_by('-service_date')
        total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
        categories = Category.objects.all().order_by('category_total_hours')

        # List categories in order;
        try:
            category_1 = categories[0:1].get()   # get first category from dataset
        except Category.DoesNotExist:   # if category doesn't exist, set it to none
            category_1 = None
        try:
            category_2 = categories[1:2].get()   # get second category from dataset
        except Category.DoesNotExist:   # if category doesn't exist, set it to none
            category_2 = None
        try:
            category_3 = categories[2:3].get()   # get third category from dataset
        except Category.DoesNotExist:   # if category doesn't exist, set it to none
            category_3 = None
        # Get user's award level based on user's total logged hours
        if total_hrs != 0 and category_1 != None and category_2 != None and category_3 != None:  # If total hours
            # doesn't equal to 0 and the category table is not empty, set category to their corresponding value
            if category_1.category_total_hours <= total_hrs and total_hrs < category_2.category_total_hours: # If
                # total hours is between category 1 and 2, set user category to category 1 text
                category = category_1.category_text
            elif category_2.category_total_hours <= total_hrs and total_hrs < category_3.category_total_hours: # If
                # total hours is between category 2 and 3, set user category to category 2 text
                category = category_2.category_text
            elif category_3.category_total_hours <= total_hrs: # If total hours is greater or equal to
                # category 3, set user category to category 3 text
                category = category_3.category_text
            else: # If total hours is less than category 1, set user category to none
                category = None
        else: # If total hours equals 0 or category table has no data, set categories to empty
            category = None
        context['total_hrs'] = total_hrs
        context['category'] = category
        return context

# Detailed Post View. Allows user to see each log's specific details
class HoursDetailView(DetailView):
    model = Post
    template_name = 'n_hours_detail.html'

# Update Hours View using Post table and NewHours form. Allows User to update their log, whether
# it be hours, service date, or description
class HoursUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post        # To get data from POST Table
    form_class = NewHoursForm        # To use NewHoursForm
    template_name = 'l_new_hours.html'      # To call Html page

    # Set updated logs to the current logged in user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # Checks if user logged in is updating own log
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user: # Compare Users
            return True
        return False

# Delete log View. Allows User to delete their own log
class HoursDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'o_post_confirm_delete.html'
    success_url = '/post/my'   # Redirect to MyHours after deleted post

    # Checks if user logged in is deleting own log
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

# SchoolHours View, Lists all logs in the school
class SchoolHoursView(ListView):
    model = Post
    template_name = 'p_post_school.html'
    context_object_name = 'posts'
    ordering = ['-service_date']
    paginate_by = 5 # 5 logs per page


    # Pass logged in user's data to html
    def get_context_data(self, **kwargs):
        context = super(SchoolHoursView, self).get_context_data(**kwargs)
        posts = Post.objects.all().order_by('-service_date')
        total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
        context['total_hrs'] = total_hrs
        return context

# Detailed User View. Allows User to see others' logs
class School_User_View(ListView):
    model = Post
    template_name = 'q_post_user.html'
    context_object_name = 'posts'
    ordering = ['-service_date']    # Sort by latest service date
    paginate_by = 5 # 5 logs per page

    # Get selected user's logs after clicking on a username
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user=user).order_by('-service_date')

    # Pass selected user's data to html
    def get_context_data(self, **kwargs):
        context = super(School_User_View, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        posts = Post.objects.filter(user=user).order_by('-service_date')
        total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
        categories = Category.objects.all().order_by('category_total_hours')
        # List categories in order;
        try:
            category_1 = categories[0:1].get()  # get first category from dataset
        except Category.DoesNotExist:  # if category doesn't exist, set it to none
            category_1 = None
        try:
            category_2 = categories[1:2].get()  # get second category from dataset
        except Category.DoesNotExist:  # if category doesn't exist, set it to none
            category_2 = None
        try:
            category_3 = categories[2:3].get()  # get third category from dataset
        except Category.DoesNotExist:  # if category doesn't exist, set it to none
            category_3 = None
        # Get user's award level based on user's total logged hours
        if total_hrs != 0 and category_1 != None and category_2 != None and category_3 != None:  # If total hours
            # doesn't equal to 0 and the category table is not empty, set category to their corresponding value
            if category_1.category_total_hours <= total_hrs and total_hrs < category_2.category_total_hours:  # If
                # total hours is between category 1 and 2, set user category to category 1 text
                category = category_1.category_text
            elif category_2.category_total_hours <= total_hrs and total_hrs < category_3.category_total_hours:  # If
                # total hours is between category 2 and 3, set user category to category 2 text
                category = category_2.category_text
            elif category_3.category_total_hours <= total_hrs:  # If total hours is greater or equal to
                # category 3, set user category to category 3 text
                category = category_3.category_text
            else:  # If total hours is less than category 1, set user category to none
                category = None
        else:  # If total hours equals 0 or category table has no data, set categories to empty
            category = None
        context['user'] = user
        context['total_hrs'] = total_hrs
        context['category'] = category
        return context

# My Free Date Range Report is a filter report. User can choose time frame showing their logs and total hours.
# It includes calendar widget picker.
def myreport(request, *args, **kwargs):
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    date1 = datetime.strptime(startDate, "%m/%d/%Y").date() # 2 Ranges
    date2 = datetime.strptime(endDate, "%m/%d/%Y").date()
    user = request.user
    service_date = 'Service Date: '
    posts = Post.objects.filter(user=user, service_date__range=[date1, date2]).order_by('-service_date')   # Get
    # all logs from selected date range
    total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
    reporting_date = datetime.today().date
    context = {
        'posts': posts,
        'report_title': "My Community Service Hours Report",
        'user': user,
        'service_date': service_date,
        'date1': date1,
        'between_date': " -- ",
        'date2': date2,
        'total_hrs': total_hrs,
        'reporting_date': reporting_date,
    }
    return render(request, 'r_myreport.html', context)

# My Free Date report in Pdf format. it includes calendar widget picker
class mypdf(View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        service_date = 'Service Date: '
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        date1 = datetime.strptime(startDate, "%m/%d/%Y").date() # start date of range
        date2 = datetime.strptime(endDate, "%m/%d/%Y").date() # end date of range
        posts = Post.objects.filter(user=user, service_date__range=[date1, date2]).order_by('-service_date') # Filter
        # by user and date range
        total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
        reporting_date = datetime.today().date  # Today
        context = {
            'posts': posts,
            'report_title_1': "Community Service Hours",
            'report_title_2': 'My Community Service Hours Report',
            'user': user,
            'service_date': service_date,
            'date1': date1,
            'between_date': ' -- ',
            'date2': date2,
            'total_hrs': total_hrs,
            'reporting_date': reporting_date,
        }
        pdf = render_to_pdf('r_mypdf.html', context)    # Call render_to_pdf function from utils
        return HttpResponse(pdf, content_type='application/pdf')

# Category Table Report. Shows all three current levels in CSA awards program and
# their corresponding hours
def category(request, *args, **kwargs):
    categories = Category.objects.all().order_by('category_total_hours')    # Filter by total hours, least is first
    reporting_date = datetime.today().date  # Today
    context = {
        'categories': categories,
        'report_title': "Community Service Awards Ranks",
        'reporting_date': reporting_date,
    }
    return render(request, 's_category.html', context)

# Chapter Category Table report in Pdf format
class categorypdf(View):
    def post(self, request, *args, **kwargs):
        categories = Category.objects.all().order_by('category_total_hours')
        reporting_date = datetime.today().date
        context = {
            'categories': categories,
            'report_title': "Community Service Awards Ranks",
            'reporting_date': reporting_date,
        }
        pdf = render_to_pdf('s_categorypdf.html', context)    # Call render_to_pdf function from utils
        return HttpResponse(pdf, content_type='application/pdf')

# Summary Hours Report. show all Users' basic information, hour total, and
# corresponding award level. Summary of each users' award level
def summary(request, *args, **kwargs):
    users = User.objects.all()  # All Users
    profiles = Profile.objects.all()    # ALl Profiles and data
    posts = Post.objects.values('user_id').annotate(total_hours=Sum('hours')).values('user_id', 'total_hours').order_by(
        '-total_hours') # Get all hours of each user and sum, user with most hours is on top
    categories = Category.objects.all().order_by('category_total_hours')
    # List categories in order;
    try:
        category_1 = categories[0:1].get()   # get first category from dataset
    except Category.DoesNotExist:   # if category doesn't exist, set it to none
        category_1 = None
    try:
        category_2 = categories[1:2].get()   # get second category from dataset
    except Category.DoesNotExist:
        category_2 = None
    try:
        category_3 = categories[2:3].get()   # get third category from dataset
    except Category.DoesNotExist:
        category_3 = None
    reporting_date = datetime.today().date
    # Pass values to html
    context = {
        'users': users,
        'profiles': profiles,
        'posts': posts,
        'category_1': category_1,
        'category_2': category_2,
        'category_3': category_3,
        'report_title': "School Community Service Awards Report",
        'reporting_date': reporting_date,
    }
    return render(request, 't_summary.html', context)

# Chapter Summary Hours report in Pdf format
class summarypdf(View):
    def post(self, request, *args, **kwargs):
        users = User.objects.all()
        profiles = Profile.objects.all()
        posts = Post.objects.values('user_id').annotate(total_hours=Sum('hours')).values('user_id','total_hours').order_by(
            '-total_hours')
        categories = Category.objects.all().order_by('category_total_hours')
        # List categories in order;
        try:
            category_1 = categories[0:1].get()   # get first category from dataset
        except Category.DoesNotExist:   # if category doesn't exist, set it to none
            category_1 = None
        try:
            category_2 = categories[1:2].get()   # get second category from dataset
        except Category.DoesNotExist:
            category_2 = None
        try:
            category_3 = categories[2:3].get()   # get third category from dataset
        except Category.DoesNotExist:
            category_3 = None
        reporting_date = datetime.today().date
        context = {
            'users': users,
            'profiles': profiles,
            'posts': posts,
            'category_1': category_1,
            'category_2': category_2,
            'category_3': category_3,
            'report_title': "School Community Service Awards Report",
            'reporting_date': reporting_date,
        }
        pdf = render_to_pdf('t_summarypdf.html', context)   # Call render_to_pdf function from utils
        return HttpResponse(pdf, content_type='application/pdf')


# School Free Date Range Report. Choose date range and shows all members'
# logs within chosen time frame. Displays total amount of hours and includes calendar widget
def schoolreport(request, *args, **kwargs):
    service_date = 'Service Date: '
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    date1 = datetime.strptime(startDate, "%m/%d/%Y").date() # start date of range
    date2 = datetime.strptime(endDate, "%m/%d/%Y").date()   # end date of range
    posts = Post.objects.filter(service_date__range=[date1, date2]).order_by('-service_date') # Sort by latest
    # service date
    total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0
    reporting_date = datetime.today().date
    # Pass values to html
    context = {
        'posts': posts,
        'report_title': 'School Community Service Hours Report',
        'service_date': service_date,
        'date1': date1,
        'between_date': ' -- ',
        'date2': date2,
        'total_hrs': total_hrs,
        'reporting_date': reporting_date,
    }
    return render(request, 'u_schoolreport.html', context)


# School Free Date Range report in Pdf format. Includes a calendar widget
class schoolpdf(View):
    def post(self, request, *args, **kwargs):
        service_date = 'Service Date: '
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        date1 = datetime.strptime(startDate, "%m/%d/%Y").date() # start date of range
        date2 = datetime.strptime(endDate, "%m/%d/%Y").date() # end date of range
        posts = Post.objects.filter(service_date__range=[date1, date2]).order_by('-service_date')
        total_hrs = list(posts.aggregate(Sum('hours')).values())[0] or 0 # Sum of hours
        reporting_date = datetime.today().date
        # Pass values to html
        context = {
            'posts': posts,
            'report_title_1': 'School Community Service',
            'report_title_2': 'School Community Service Hours Report',
            'service_date': service_date,
            'date1': date1,
            'between_date': ' -- ',
            'date2': date2,
            'total_hrs': total_hrs,
            'reporting_date': reporting_date,
        }
        pdf = render_to_pdf('u_schoolpdf.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

