from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post
from django.forms import ModelForm

# User Information Form for when a user creates/registers a new account. Includes basic
# information such as First Name, last name, username, password, and email
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    #init function is called automatically every time the class is being used to create a new object
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    # Add user table fields to registration form
    class Meta:
        model = User
        User._meta.get_field('username').validators[1].limit_value = 30
        User._meta.get_field('username').help_text = (
            'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

# Extra Profile User Information Form for when a user creates/registers a new account.
# Includes more basic user Information such as Student Number and Grade level
class ProfileRegisterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ProfileRegisterForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['student_no'].required = True
        self.fields['grade'].required = True

    # Add profile table fields to registration form
    class Meta:
        model = Profile
        fields = ['student_no', 'grade']

# When a User updates their profile information, they will change the same information
# in the User Form they used when registered
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    # Update user table fields
    class Meta:
        model = User
        User._meta.get_field('username').validators[1].limit_value = 30
        User._meta.get_field('username').help_text = (
            'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
        fields = ['username', 'first_name', 'last_name', 'email']

# When a User updates their profile, they will also change the same information/form they
# registered with including the Profile Form as shown here
class ProfileUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['student_no'].required = True
        self.fields['grade'].required = True

    # Update profile table fields
    class Meta:
        model = Profile
        fields = ['student_no', 'grade', 'image']

# Allows designated fields to use date picker widget, Used when choosing service date and free date range report
class DateInput(forms.DateInput):
    input_type = 'date'

class NewHoursForm(ModelForm):
    class Meta:
        model = Post
        fields = ['service_date', 'hours', 'desc']
        widgets = {
            'service_date': DateInput(), # Uses DateInput/date picker widget
        }