from django import forms

from .models import (
    AuthorizedEmail,
    CaseStudy,
    Event,
    GlossaryTerm,
    SeniorAdvisor,
    TargetCompany,
    Task,
    TaskComment,
    Whitepaper,
    WhitepaperComment,
)


class DateInput(forms.DateInput):
    input_type = "date"


class CorporateEmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="Email corporativo",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}),
    )

    allowed_domain = "artefact.com"

    def clean(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if email:
            self.cleaned_data["email"] = email

        if email:
            if not email.endswith(f"@{self.allowed_domain}"):
                raise forms.ValidationError("Use um email corporativo @artefact.com.")

            if not AuthorizedEmail.objects.filter(email__iexact=email, is_active=True).exists():
                raise forms.ValidationError("Este email ainda nao esta autorizado no admin.")

        return self.cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "owner_name",
            "due_date",
            "tags",
            "notes",
            "document_link",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "due_date": DateInput(),
        }


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ["user_name", "text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "event_type", "start_date", "location"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "start_date": DateInput(),
        }


class WhitepaperForm(forms.ModelForm):
    class Meta:
        model = Whitepaper
        fields = [
            "title",
            "description",
            "topic",
            "status",
            "progress",
            "author_name",
            "content",
            "document_link",
            "published_date",
            "target_audience",
            "tags",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 8}),
            "target_audience": forms.Textarea(attrs={"rows": 3}),
            "published_date": DateInput(),
        }


class WhitepaperCommentForm(forms.ModelForm):
    class Meta:
        model = WhitepaperComment
        fields = ["user_name", "text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class GlossaryTermForm(forms.ModelForm):
    class Meta:
        model = GlossaryTerm
        fields = ["term", "definition", "category", "example"]
        widgets = {
            "definition": forms.Textarea(attrs={"rows": 3}),
        }


class CaseStudyForm(forms.ModelForm):
    class Meta:
        model = CaseStudy
        fields = ["title", "category", "summary", "author", "content", "is_published"]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
            "content": forms.Textarea(attrs={"rows": 6}),
        }


class TargetCompanyForm(forms.ModelForm):
    class Meta:
        model = TargetCompany
        fields = ["name", "industry", "status", "contact_person", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class SeniorAdvisorForm(forms.ModelForm):
    class Meta:
        model = SeniorAdvisor
        fields = ["name", "expertise", "company", "linkedin", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }