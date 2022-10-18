from .models import BlogComment, Post, BlogRepost, RepostComment, BlogImages
from django import forms
from djrichtextfield.widgets import RichTextWidget


class UpdateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["content"]


class CreateForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "name": "content",
        "required": True,
        "rows": 3,
        "id": "content",
        "placeholder": "Create Post?"

    }))
    # content = forms.CharField(required=True, widget=RichTextWidget(attrs={
    #     "name": "content",
    # }))

    class Meta:
        model = Post
        fields = ["content"]


class RepostForm(forms.ModelForm):

    class Meta:
        model = BlogRepost
        fields = ["text"]


class RepostCommentBox(forms.ModelForm):

    class Meta:
        model = RepostComment
        fields = ["comment"]


class CommentBox(forms.ModelForm):

    class Meta:
        model = BlogComment
        fields = ["comment"]


class ImageForm(forms.ModelForm):

    class Meta:
        model = BlogImages
        fields = ["image", ]