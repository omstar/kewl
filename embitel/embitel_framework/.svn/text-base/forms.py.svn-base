from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import authenticate
from embitel_framework.models import Groups
    
from django.utils.safestring import mark_safe

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=75, required=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),max_length=100, required=True)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if not email or not password:
            return self.cleaned_data
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                pass
            else:
                user=None
        except User.DoesNotExist:
            user=None

        if user is None:
            self._errors["email"] = self.error_class(["Incorrect email/password!"])

        else:
            if not user.is_active:
                self._errors["email"] = self.error_class(["Inactive Account!"])

        #user = authenticate(email=email, password=password)
        return self.cleaned_data

class RegistrationForm(forms.Form):
    """
    forms used for registration.
    """
    register_email = forms.EmailField(label="register_email", max_length=60, required=True)
    register_password = forms.CharField(label="register_password", max_length=15, required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="confirm_password", max_length=15, required=True,
                                       widget=forms.PasswordInput)
    # You can add a function to clean password (if any password restrictions)
    def clean_register_email(self):
        email = self.cleaned_data.get('register_email')
        try:
 
            user = User.objects.get(email=email)
            self._errors["register_email"] = self.error_class(["Account with this email id already exists!"])
        except:
            try:
                group_object = Groups.objects.get(email=email)
                if group_object.group_name in ['HR'] or email == 'prakash.p@embitel.com':
                    pass
                else:
                    self._errors["register_email"] = self.error_class([mark_safe("You are not allowed to register! <br> Please contact our team for assistance!")])
            except:
                self._errors["register_email"] = self.error_class([mark_safe("You are not allowed to register! <br> Please contact our team for assistance!")])
        return self.cleaned_data
            
    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('register_password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(("The two password fields didn't match."))
        return password2

class UploadP12Certificate(forms.Form):
    app_name = forms.CharField(label='app_name', max_length=100, widget=forms.TextInput,required=True)
    p12_certificate =  forms.FileField(label='p12_certificate', required=True)
    user_id =  forms.IntegerField(label='User id', required=False) # this field is just to pass the user id
    def clean(self, *args, **kwargs):
        from embitel_framework.models import P12Certificate
        app_name = self.cleaned_data.get('app_name')
        if app_name and P12Certificate.objects.filter(app_name=app_name, user__id=self.user_id):
            self._errors["app_name"] = self.error_class(["You have already uploaded p12 certificate with the same app name!"])
        return self.cleaned_data


class ConfigureNotificationsForm(forms.Form):
    import datetime
    subject = forms.CharField(label="Subject", widget=forms.Textarea(attrs={'cols': 30, 'rows': 2}), required=True)
    message = forms.CharField(label='Message',  max_length=200, widget=forms.Textarea(attrs={'cols': 30, 'rows': 4}), required=True)
    location = forms.CharField(label="Location", widget=forms.TextInput,  required=False)
    start_time = forms.DateTimeField(label='Start Time',  widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'autocomplete':'off'}),required=False, help_text=mark_safe('Format: yyyy-mm-dd hr:min'))#, initial=datetime.datetime.now())
    end_time = forms.DateTimeField(label='End Time',  widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'autocomplete':'off'}),required=False, help_text=mark_safe('Format: yyyy-mm-dd hr:min'))#, intial=datetime.datetime.now())
    def clean(self, *args, **kwargs):
        return self.cleaned_data


