from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CATEGORY = (('movie','映画'), ('drama','ドラマ'), ('anime','アニメ',), ('other','その他'))

class Work(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField("タイトル", max_length=100)
    total_episodes = models.IntegerField("総話数", blank=True, null=True)
    episode = models.IntegerField("話数", blank=True, null=True)
    watch_seconds = models.PositiveIntegerField("視聴時間(秒)", blank=True, null=True)
    text = models.TextField("メモ", blank=True)
    thumbnail = models.ImageField("サムネイル画像",  upload_to="thumbnails/", null=True, blank=True)
    category = models.CharField("カテゴリー", max_length=100, choices = CATEGORY)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # 同じユーザーが同じタイトルを複数作れない（＝別作品として増えるのを防ぐ）
            models.UniqueConstraint(fields=["user", "title"], name="uniq_user_title_work"),
        ]

    def __str__(self):
        return self.title

class EpisodeProgress(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="episodes")
    episode = models.IntegerField("話数")
    watch_seconds = models.PositiveIntegerField("視聴時間(秒)", blank=True, null=True)
    text = models.TextField("メモ", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # 同じ作品の同じ話数は1つだけ（登録し直したら更新にしたい場合に便利）
            models.UniqueConstraint(fields=["work", "episode"], name="uniq_work_episode"),
        ]

    def formatted_time(self):
        if self.watch_seconds is None:
            return "未記録"

        h, remainder = divmod(self.watch_seconds, 3600)
        m, s = divmod(remainder, 60)

        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"

    def __str__(self):
        return f"{self.work.title} - {self.episode}話"
    
class FavoriteScene(models.Model):
    episode = models.ForeignKey(
        EpisodeProgress,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    seconds = models.PositiveIntegerField("視聴時間（秒）")
    memo = models.TextField("メモ", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def formatted_time(self):
        h, remainder = divmod(self.seconds, 3600)
        m, s = divmod(remainder, 60)

        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def __str__(self):
        return f"{self.episode.work.title} 第{self.episode.episode}話"
    