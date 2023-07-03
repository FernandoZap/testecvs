from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):

    '''
        def clean_email(self):
                email = self.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                        raise forms.ValidationError('Email já está cadastrado.')
                return email
    '''
    password1 = forms.CharField(label = 'Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label = 'Confirmação da Senha',
        widget=forms.PasswordInput
        )



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Confirmacao de Senha não confere!')
        return password2

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username','email','funcao','iduser']

class EditAccountForm(forms.ModelForm):

        class Meta:
                model = User
                fields = ['username','email','name','funcao']
