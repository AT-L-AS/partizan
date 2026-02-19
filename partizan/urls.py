from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    path('trainings/', views.TrainingsView.as_view(), name='trainings'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('holidays/', views.HolidaysView.as_view(), name='holidays'),
    path('holidays/category/<slug:category_slug>/', views.HolidaysView.as_view(), name='holidays_by_category'),
    path('holiday/<slug:holiday_slug>/', views.HolidayDetailView.as_view(), name='holiday_detail'),
    
    # API
    path('api/get-available-dates/<int:holiday_id>/', views.get_available_dates, name='get_available_dates'),
    path('api/create-quick-order/', views.create_quick_order, name='create_quick_order'),
    path('api/create-full-order/', views.create_full_order, name='create_full_order'),
    path('api/create-review/', views.create_review, name='create_review'),
    path('api/register-training/', views.register_training, name='register_training'),
]