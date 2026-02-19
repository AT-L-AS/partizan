from .models import Category, Contact

def categories(request):
    return {
        'all_categories': Category.objects.all(),
        'contact_info': Contact.objects.first(),
    }