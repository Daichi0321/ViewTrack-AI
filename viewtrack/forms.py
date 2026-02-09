from django import forms
from .models import EpisodeProgress

class EpisodeProgressForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, required=False, label="時間")
    minutes = forms.IntegerField(min_value=0, max_value=59, required=False, label="分")
    seconds = forms.IntegerField(min_value=0, max_value=59, required=False, label="秒")

    class Meta:
        model = EpisodeProgress
        # watch_seconds は直接入力させない
        fields = ("episode", "text")  # ←必要なら他も追加OK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["episode"].widget.attrs.update({
            "placeholder": "※必須",
            "min": 1,
        })

        # 更新画面で初期値を分解して入れる
        total = self.instance.watch_seconds or 0
        self.fields["hours"].initial = total // 3600
        self.fields["minutes"].initial = (total % 3600) // 60
        self.fields["seconds"].initial = total % 60

    def clean(self):
        cleaned = super().clean()
        h = cleaned.get("hours") or 0
        m = cleaned.get("minutes") or 0
        s = cleaned.get("seconds") or 0
        cleaned["watch_seconds"] = h * 3600 + m * 60 + s
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.watch_seconds = self.cleaned_data["watch_seconds"]
        if commit:
            obj.save()
        return obj
