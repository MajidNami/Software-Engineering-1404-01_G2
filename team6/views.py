from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from .models import *
# from .serializers import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from .models import WikiArticle, WikiCategory, WikiTag, WikiArticleRevision, WikiArticleReports
from django.utils import timezone

from django.http import JsonResponse
from .models import WikiArticle
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

TEAM_NAME = "team6"

# --- Base views ---
@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    articles = WikiArticle.objects.using(TEAM_NAME).filter(status='published')
    return render(request, f"{TEAM_NAME}/index.html", {"articles": articles})

# 2 & 7. Article list + keyword search + category filter (requirement 12)
class ArticleListView(ListView):
    model = WikiArticle
    template_name = 'team6/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = WikiArticle.objects.using('team6').filter(status='published')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        tag = self.request.GET.get('tag')

        if q:  # Direct keyword or phrase search
            queryset = queryset.filter(Q(title_fa__icontains=q) | Q(body_fa__icontains=q))
        if cat:  # Category filter
            queryset = queryset.filter(category__slug=cat)
        if tag:  # Search by tag (requirement 6)
            queryset = queryset.filter(tags__slug=tag)
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WikiCategory.objects.using('team6').all()
        context['tags'] = WikiTag.objects.using('team6').all()
        return context

# 3. Create article
class ArticleCreateView(CreateView):
    model = WikiArticle
    fields = ['title_fa', 'place_name', 'slug', 'body_fa', 'category', 'summary']
    template_name = 'team6/article_form.html'
    success_url = '/team6/'
    login_url = '/auth/'

    def form_valid(self, form):
        # form.instance.status = 'published'
        
        # return super().form_valid(form)
        article = form.save(commit=False)

        # Logged-in user info from central authentication service
        article.author_user_id = self.request.user.id
        article.last_editor_user_id = self.request.user.id
        article.status = 'published'

        # Save to team database
        article.save(using='team6')
        form.save_m2m()

        return redirect(self.success_url)

# 4. Edit article (with creating a new revision - requirement 8)
def edit_article(request, slug):
    article = get_object_or_404(WikiArticle.objects.using('team6'), slug=slug)
    if request.method == "POST":
        # Before updating, save the current version into revision history
        WikiArticleRevision.objects.using('team6').create(
            article=article,
            revision_no=article.current_revision_no,
            body_fa=article.body_fa,
            change_note=request.POST.get('change_note', 'No note')
        )
        # Update article
        article.body_fa = request.POST.get('body_fa')
        article.current_revision_no += 1
        article.save(using='team6')
        return redirect('article_detail', slug=article.slug)
    
    return render(request, 'team6/article_edit.html', {'article': article})

# 5. Report article
def report_article(request, pk):
    if request.method == "POST":
        article = get_object_or_404(WikiArticle.objects.using('team6'), pk=pk)
        WikiArticleReports.objects.using('team6').create(
            article=article,
            reporter_user_id=request.user.id if request.user.is_authenticated else uuid.uuid4(),
            report_type=request.POST.get('type'),
            description=request.POST.get('desc')
        )
        return JsonResponse({"status": "success"})

# 8. Show article revisions
def article_revisions(request, slug):
    article = get_object_or_404(WikiArticle.objects.using('team6'), slug=slug)
    revisions = WikiArticleRevision.objects.using('team6').filter(article=article).order_now('-created_at')
    return render(request, 'team6/revisions.html', {'article': article, 'revisions': revisions})

# 10 & 11. Article detail view + summarization (LLM)
def article_detail(request, slug):
    article = get_object_or_404(WikiArticle.objects.using('team6'), slug=slug)
    article.view_count += 1
    article.save()
    return render(request, 'team6/article_detail.html', {'article': article})


def get_wiki_content(request):
    place_query = request.GET.get('place', None)
    
    if not place_query:
        return JsonResponse({"error": "place parameter is required"}, status=400)
    
    # Search by place name or title (direct search requirement)
    article = WikiArticle.objects.using('team6').filter(
        Q(place_name__icontains=place_query) | Q(title_fa__icontains=place_query)
    ).first()

    if not article:
        return JsonResponse({"message": "No content found for this place"}, status=404)

    # Build response according to the agreed format between teams
    data = {
        "id": str(article.id_article),
        "title": article.title_fa,
        "place_name": article.place_name,
        "category": article.category.title_fa,
        "tags": list(article.tags.values_list('title_fa', flat=True)),
        "summary": article.summary,
        "description": article.body_fa,
        "images": [article.featured_image_url] if article.featured_image_url else [],
        "url": article.url,
        "updated_at": article.updated_at.isoformat()
    }
    return JsonResponse(data)
