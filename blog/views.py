from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from blog.form import PostForm
from .models import Post
from rest_framework import viewsets
from .serializers import PostSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import os
from mysite import settings


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

# Create your views here.
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()

            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_edit.html', {'form': form})

def js_test(request):
    return render(request, 'blog/js_test.html')

class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

#########수정위치#############
@csrf_exempt  # CSRF 검사를 비활성화 (테스트 용도로만 사용하세요)
def my_post_view(request):
    if request.method == "POST":
        # 현재 날짜와 시간을 기반으로 파일 이름 생성
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_path = os.path.join(settings.BASE_DIR, "requests", f"request_{timestamp}.bin")

        # "requests" 폴더가 없으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 요청 헤더를 원하는 형식으로 문자열로 생성
        headers = [
            f"{request.method} {request.path} HTTP/1.1",
            f"Authorization: {request.headers.get('Authorization', '')}",
            f"User-Agent: {request.headers.get('User-Agent', '')}",
            f"Host: {request.get_host()}",
            f"Connection: Keep-Alive",
            f"Accept-Encoding: {request.headers.get('Accept-Encoding', '')}"
        ]
        header_content = "\n".join(headers)

        # .bin 파일에 요청 헤더를 기록
        with open(file_path, 'w') as f:
            f.write(header_content)

        return JsonResponse({"message": "Data received and saved as bin file"}, status=200)
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)