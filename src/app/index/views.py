
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import Notebook, Smartphone, Category, LatestProducts



class IndexView(View):

    def get(self, request, *args, **kwargs):
        products = LatestProducts.object.get_products_for_models('notebook', 'smartphone')
        context = {
            'products': products,

        }
        return render(request, 'index/index.html', context)



class NotebookDetailView(DetailView):
    queryset = Notebook.objects.all()
    context_object_name = 'product'
    template_name = 'index/note_post.html'
    slug_url_kwarg = 'slug'


class SmartphoneDetailView(DetailView):
    queryset = Smartphone.objects.all()
    context_object_name = 'product'
    template_name = 'index/smartphone_post.html'
    slug_url_kwarg = 'slug'


class Category2DetailView(DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = "index/category_detail.html"
    slug_url_kwarg = 'slug'

class CategoryDetailView(View):

    def get(self, request, *args, **kwargs):
        slug_field = kwargs.get('slug')
        print(slug_field)
        products = LatestProducts.object.get_products_for_models(slug_field)
        context = {
            'products': products,
        }
        return render(request, 'index/index.html', context)

