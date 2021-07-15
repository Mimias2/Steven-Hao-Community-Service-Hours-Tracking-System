from django.urls import path
from . import views

from django.contrib.auth import views as auth_views
from .views import(
NewHoursView,
MyHoursView,
HoursDetailView,
HoursUpdateView,
HoursDeleteView,
SchoolHoursView,
School_User_View,
mypdf,
summarypdf,
categorypdf,
schoolpdf,

)
urlpatterns = [
    # User/Profile
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='e_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='f_logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='h_password_reset.html'),
         name='password_reset'),
    path('password-reset/done',
         auth_views.PasswordResetDoneView.as_view(template_name='i_password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='j_password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='k_password_reset_complete.html'),
         name='password_reset_complete'),

    # User function urls
    path('post/new/', NewHoursView.as_view(), name='post-create'),
    path('post/my/', MyHoursView.as_view(), name='post-my'),
    path('post/<int:pk>', HoursDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', HoursUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', HoursDeleteView.as_view(), name='post-delete'),

    path('post/school/', SchoolHoursView.as_view(), name='post-school'),
    path('user/<username>', School_User_View.as_view(), name='post-user'),

    path('posted/my/freely', views.myreport, name='my-report'),
    path('posted/my/freely/pdf', mypdf.as_view(), name='my-pdf'),

    path('posted/school/freely', views.schoolreport, name='school-report'),
    path('posted/school/freely/pdf', schoolpdf.as_view(), name='school-pdf'),

    # Summary and Category Report
    path('posted/school/summary', views.summary, name='summary'),
    path('posted/school/summary/pdf', summarypdf.as_view(), name='summary-pdf'),
    path('posted/school/category', views.category, name='category'),
    path('posted/school/category/pdf', categorypdf.as_view(), name='categorypdf'),
]

