from .models import BlogComment, Post, BlogRepost, RepostComment, BlogImages
from django import forms


class UpdateForm(forms.ModelForm):
    # comment = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

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

    class Meta:
        model = Post
        fields = ["content"]


class RepostForm(forms.ModelForm):
    # text = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Quote Repost?"}))

    class Meta:
        model = BlogRepost
        fields = ["text"]


class RepostCommentBox(forms.ModelForm):
    # comment = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

    class Meta:
        model = RepostComment
        fields = ["comment"]


class CommentBox(forms.ModelForm):
    # comment = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

    class Meta:
        model = BlogComment
        fields = ["comment"]


class ImageForm(forms.ModelForm):

    class Meta:
        model = BlogImages
        fields = ["image", ]