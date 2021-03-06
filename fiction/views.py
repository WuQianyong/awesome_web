from django.shortcuts import render,get_object_or_404

# Create your views here.
# from django.shortcuts import
from django.http import HttpResponse
from .models import Post,Category,Tag
from django.http import HttpResponse
from .models import Post, Category, Tag
from comments.forms import CommentForm
import markdown
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q

def index(request):
    # return HttpResponse('欢迎')
    return render(request,'index.html')
    # return render(request, 'web/fiction.html',
    #               context={
    #                   'title': '我的博客首页',
    #                   'welcome': '欢迎访问我的博客首页'
    #               }
    #               )

def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        error_msg = '请输入关键字'
        return render(request, 'web/fiction.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'web/fiction.html', {'error_msg': error_msg,
                                               'post_list': post_list})

class FictionView(ListView):
    model = Post
    template_name = 'web/fiction.html'
    context_object_name = 'post_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # 首先或的父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)

        # print(context)
        # print('1----------------------')
        # print(context)
        paginator = context.get('paginator')

        page = context.get('page_obj')

        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        print(pagination_data)
        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)
        # print(context)
        # print(context)
        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 注意此时 context 字典中已有了显示分页导航条所需的数据。
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}
        # 当前页左边 和 右边 连续的 页码号，初始值为空
        left = []
        right = []

        # 标示第1页页码后 和 最后一页前是否需要显示省略号
        left_has_more = False
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False
        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数

        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么久是[1,2,3,4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 5]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 5) if (page_number - 5) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 5) if (page_number -5) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 5]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data


# class CategoryView(ListView):
class CategoryView(FictionView):
    # model = Post
    # template_name = 'blog/fiction.html'
    # context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


class ArchivesView(FictionView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                               )


class TagView(FictionView):
    """
    标签视图 函数
    """
    model = Post
    template_name = 'web/fiction.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


#
# def index(request):
#     # return HttpResponse('欢迎访问我的博客首页')
#     post_list = Post.objects.all().order_by('-created_time')
#     return render(request, 'blog/fiction.html', context={
#         'post_list': post_list,
#
#     })

class PostDetailView(DetailView):
    model = Post
    template_name = 'web/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 撰写 get 方法的目的是每当文章被访问一次，就得将文章阅读量+1
        # get 方法返回的是一个HttpResponse 实例
        # 之所以要先 调用父类的 get 方法，是因为只有当get 方法被调用后
        # 才有self.object 属性，其值为Post 模型实例，即被访问的文章post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量+1
        self.object.increase_views()
        # 视图必须返回一个 HttpResponse 对象

        return response

    def get_object(self, queryset=None):
        # 撰写get_object 方法的目的是因为需要对post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc

        return post

    def get_context_data(self, **kwargs):
        # 撰写 get_context_data 的目的是因为除了 post 传递给模板外 DetailView
        # 还要把 评论表单、post 下的评论列表传递给模板
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context
