from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    )
from .models import Work, EpisodeProgress, FavoriteScene
from .forms import EpisodeProgressForm

class ListViewTrackView(LoginRequiredMixin, ListView):
    template_name = 'viewtrack/viewtrack_progress.html'
    model = Work

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.filter(user=self.request.user)

        category = self.kwargs.get('category')
        if category:
            queryset = queryset.filter(category=category)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)

            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for w in context["object_list"]:# 最新エピソード（更新日が最新）
            latest = w.episodes.order_by("-updated_at").first()
            w.latest_episode = latest

            # progress計算（総話数があるときだけ）
            if latest and w.total_episodes and w.total_episodes > 0:
                pct = int(latest.episode / w.total_episodes * 100)
                # 念のため 0〜100 に丸める
                w.progress = max(0, min(100, pct))
            else:
                w.progress = 0

        return context

class DetailViewTrackView(LoginRequiredMixin, DetailView):
    template_name = 'viewtrack/viewtrack_detail.html'
    model = Work

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["episodes"] = self.object.episodes.order_by("episode")
        return context

class CreateViewTrackView(LoginRequiredMixin, CreateView):
    template_name = 'viewtrack/viewtrack_create.html'
    model = EpisodeProgress
    form_class = EpisodeProgressForm
    success_url = reverse_lazy('progress-viewtrack')

    def form_valid(self, form):
        # Work用（create.html の手入力）
        title = self.request.POST.get('title')
        category = self.request.POST.get('category')
        thumbnail = self.request.FILES.get('thumbnail')
        total_episodes = self.request.POST.get('total_episodes')

        work, created = Work.objects.get_or_create(
            user=self.request.user,
            title=title,
            defaults={
                "category": category,
                "thumbnail": thumbnail,
                "total_episodes": total_episodes,
            }
        )

        # 既存作品で総話数が未設定なら入れる（上書きしない）
        if not created and total_episodes and not work.total_episodes:
            work.total_episodes = total_episodes
            work.save()

        # EpisodeProgress をこの作品に紐付ける
        form.instance.work = work

        # 同じ話数があれば更新にしたい場合（UniqueConstraintあるなら必須）
        ep = form.cleaned_data.get("episode")
        watch_seconds = form.cleaned_data.get("watch_seconds")
        text = form.cleaned_data.get("text")

        self.object = EpisodeProgress.objects.update_or_create(
            work=work,
            episode=ep,
            defaults={"watch_seconds": watch_seconds, "text": text},
        )[0]
        return redirect(self.get_success_url())

class UpdateViewTrackView(LoginRequiredMixin, UpdateView):
    model = Work
    form_class = EpisodeProgressForm
    template_name = 'viewtrack/viewtrack_update.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user:
            raise PermissionDenied
        
        return obj
    
    def get_success_url(self):
        return reverse('detail-viewtrack', kwargs={'pk': self.object.id})
    
class DeleteViewTrackView(LoginRequiredMixin, DeleteView):
    template_name = 'viewtrack/viewtrack_confirm_delete.html'
    model = Work
    success_url = reverse_lazy('progress-viewtrack')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user:
            raise PermissionDenied
        
        return obj

@login_required(login_url='login')  # 未ログイン時のリダイレクト先
def index(request):
    latest_tracks = Work.objects.filter(user=request.user).order_by('-id')[:6]

    for w in latest_tracks:
        latest = w.episodes.order_by("-updated_at").first()
        w.latest_episode = latest

        if latest and w.total_episodes and w.total_episodes > 0:
            pct = int(latest.episode / w.total_episodes * 100)
            w.progress = max(0, min(100, pct))
        else:
            w.progress = 0
    
    fav_qs = (
        FavoriteScene.objects
        .filter(episode__work__user=request.user)
        .select_related("episode", "episode__work")
        .order_by("-created_at")
    )
    favorites_recent = fav_qs[:3]
    favorites_count = fav_qs.count()

    return render(
        request,
        'viewtrack/index.html',
        {
            'object_list': latest_tracks,
            'favorites_recent': favorites_recent,
            'favorites_count': favorites_count,
        }
    )

class UpdateEpisodeProgressView(LoginRequiredMixin, UpdateView):
    model = EpisodeProgress
    template_name = "viewtrack/episodeprogress_update.html"
    fields = ("watch_seconds", "text")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.work.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("detail-viewtrack", kwargs={"pk": self.object.work.pk})


class DeleteEpisodeProgressView(LoginRequiredMixin, DeleteView):
    model = EpisodeProgress
    template_name = "viewtrack/episodeprogress_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.work.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("detail-viewtrack", kwargs={"pk": self.object.work.pk})

class CreateFavoriteView(LoginRequiredMixin, CreateView):
    model = FavoriteScene
    fields = ("seconds", "memo")
    template_name = "viewtrack/favorite_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.episode = EpisodeProgress.objects.get(pk=self.kwargs["episode_pk"])
        if self.episode.work.user != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.episode = self.episode
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("detail-viewtrack", kwargs={"pk": self.object.episode.work.pk})

class UpdateFavoriteView(LoginRequiredMixin, UpdateView):
    model = FavoriteScene
    fields = ("seconds", "memo")
    template_name = "viewtrack/favorite_update.html"

    def get_object(self):
        obj = super().get_object()
        if obj.episode.work.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("detail-viewtrack", kwargs={"pk": self.object.episode.work.pk})


class DeleteFavoriteView(LoginRequiredMixin, DeleteView):
    model = FavoriteScene
    template_name = "viewtrack/favorite_confirm_delete.html"

    def get_object(self):
        obj = super().get_object()
        if obj.episode.work.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("detail-viewtrack", kwargs={"pk": self.object.episode.work.pk})
