from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=True,
        help_text='Enter a password for the employee to sign in.'
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'role', 'is_staff', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text="Raw passwords are not stored. Use <a href=\"../password/\">this form</a> to change password."
    )

    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('email', 'name', 'role', 'status', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role', 'status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password', 'role', 'is_staff', 'is_active'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Automatically enroll employee into primary company space
        try:
            from rooms.models import Space, SpaceMember
            space = Space.objects.filter(id='space-002115').first()
            if space:
                member_role = 'Admin' if obj.role == 'Admin' else 'Member'
                SpaceMember.objects.get_or_create(
                    space=space,
                    user=obj,
                    defaults={'role': member_role, 'access': 'all_offices'}
                )
        except Exception:
            pass


