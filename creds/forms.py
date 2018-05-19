from django import forms


class StudentForm(forms.Form):

    student_name = forms.CharField(required=False)
    student_email = forms.EmailField(required=False)
    mobile = forms.IntegerField(required=False)
    course_name = forms.CharField(required=False)
    grade = forms.CharField(required=False)
    department = forms.CharField(required=False)


    