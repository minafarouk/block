from django import forms


class StudentForm(forms.Form):
    student_name = forms.CharField(required=True)
    student_email = forms.EmailField(required=True)
    mobile = forms.IntegerField(required=True)
    course_name = forms.CharField(required=True)
    grade = forms.CharField(required=True)
    department = forms.CharField(required=True)
    issuer_address = forms.CharField(required=True)
    holder_address = forms.CharField(required=True)
    privkey = forms.CharField(required=True)
