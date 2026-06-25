from django import forms
from .models import Student, Enrollment, Announcement ,Course


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class CourseForm(forms.ModelForm):
    teacher_choice = forms.ChoiceField(
        required=False,
        label="Existing Teacher",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    teacher_name = forms.CharField(
        required=False,
        label="New Teacher Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a new teacher name'
        })
    )

    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'description', 'teacher_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        teacher_names = Course.objects.order_by('teacher_name').values_list('teacher_name', flat=True).distinct()
        choices = [('', 'Select existing teacher'), ('__new__', 'Add new teacher')]
        choices += [(name, name) for name in teacher_names if name]
        self.fields['teacher_choice'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        selected_teacher = cleaned_data.get('teacher_choice')
        new_teacher_name = cleaned_data.get('teacher_name')

        if selected_teacher and selected_teacher != '__new__':
            cleaned_data['teacher_name'] = selected_teacher
        elif selected_teacher == '__new__':
            if not new_teacher_name:
                raise forms.ValidationError('Please enter a new teacher name when adding a new teacher.')
        elif not new_teacher_name:
            raise forms.ValidationError('Please choose an existing teacher or enter a new teacher name.')

        return cleaned_data