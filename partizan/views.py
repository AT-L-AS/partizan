from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date, timedelta, datetime
import json
import traceback

from .models import (
    Achievement, Category, Holiday,
    QuickOrder, FullOrder, Review, TrainingRegistration
)
from .forms import QuickOrderForm, FullOrderForm, ReviewForm

class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['achievements'] = Achievement.objects.all()[:3]
            context['holidays'] = Holiday.objects.filter(active=True)[:3]
            context['reviews'] = Review.objects.filter(approved=True)
        except Exception as e:
            print(f"Ошибка в HomeView: {e}")
            context['achievements'] = []
            context['holidays'] = []
            context['reviews'] = []
        return context

class AchievementsView(ListView):
    """Страница достижений"""
    model = Achievement
    template_name = 'achievements.html'
    context_object_name = 'achievements'
    ordering = ['-date']

class TrainingsView(TemplateView):
    """Страница тренировок"""
    template_name = 'trainings.html'

class AboutView(TemplateView):
    """Страница О нас"""
    template_name = 'about.html'

class HolidaysView(ListView):
    """Страница праздников с фильтрацией"""
    model = Holiday
    template_name = 'holidays.html'
    context_object_name = 'holidays'
    
    def get_queryset(self):
        queryset = Holiday.objects.filter(active=True)
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        age = self.request.GET.get('age')
        if age and age.isdigit():
            age = int(age)
            queryset = queryset.filter(min_age__lte=age, max_age__gte=age)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        age = self.request.GET.get('age')
        if age and age.isdigit():
            context['selected_age'] = int(age)
        
        return context

class HolidayDetailView(DetailView):
    model = Holiday
    template_name = 'holiday_detail.html'
    context_object_name = 'holiday'
    slug_url_kwarg = 'holiday_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        holiday = self.object
        
        # Данные для календаря
        context['holiday_duration'] = holiday.duration
        context['today'] = date.today().isoformat()
        context['two_weeks'] = (date.today() + timedelta(days=14)).isoformat()
        
        # Получаем все заявки (они же занятые слоты) на будущие даты
        all_bookings = FullOrder.objects.filter(
            selected_date__gte=date.today()
        ).values('selected_date', 'selected_time')
        
        # Создаем словарь с информацией о доступности
        availability = {}
        
        for booking in all_bookings:
            date_str = booking['selected_date'].isoformat()
            if date_str not in availability:
                availability[date_str] = {}
            
            time_slot = booking['selected_time']
            availability[date_str][time_slot] = availability[date_str].get(time_slot, 0) + 1
        
        # Добавляем информацию для JS
        context['booked_slots_json'] = json.dumps(availability)
        context['quick_form'] = QuickOrderForm(initial={'holiday': holiday.id})
        context['full_form'] = FullOrderForm()
        
        return context

def get_available_dates(request, holiday_id):
    """API для получения доступных дат"""
    holiday = get_object_or_404(Holiday, id=holiday_id)
    
    # Получаем все заявки для этого праздника (можно не фильтровать по празднику,
    # так как слоты общие для всех, но оставим для совместимости)
    bookings = FullOrder.objects.filter(
        selected_date__gte=date.today()
    ).values('selected_date', 'selected_time')
    
    # Группируем по датам
    result = {}
    for booking in bookings:
        date_str = booking['selected_date'].isoformat()
        if date_str not in result:
            result[date_str] = []
        result[date_str].append(booking['selected_time'])
    
    return JsonResponse({'booked': result})

@csrf_exempt
def create_quick_order(request):
    """Быстрая заявка"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})
    
    try:
        phone = request.POST.get('phone', '').strip()
        holiday_id = request.POST.get('holiday_id')
        
        if not phone:
            return JsonResponse({'success': False, 'message': 'Телефон обязателен'})
        
        if not holiday_id:
            return JsonResponse({'success': False, 'message': 'ID праздника обязателен'})
        
        holiday = get_object_or_404(Holiday, id=holiday_id)
        
        order = QuickOrder.objects.create(
            holiday=holiday,
            phone=phone
        )
        
        return JsonResponse({'success': True, 'message': 'Заявка отправлена!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def create_full_order(request):
    """Полная заявка (она же занятый слот)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})
    
    try:
        # Получаем данные
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        children_count = request.POST.get('children_count')
        age_of_children = request.POST.get('age_of_children', '').strip()
        holiday_id = request.POST.get('holiday_id')
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        notes = request.POST.get('notes', '').strip()
        
        # Валидация
        missing = []
        if not full_name: missing.append('full_name')
        if not phone: missing.append('phone')
        if not children_count: missing.append('children_count')
        if not age_of_children: missing.append('age_of_children')
        if not holiday_id: missing.append('holiday_id')
        if not selected_date: missing.append('selected_date')
        if not selected_time: missing.append('selected_time')
        
        if missing:
            return JsonResponse({'success': False, 'message': f'Не заполнены: {", ".join(missing)}'})
        
        holiday = get_object_or_404(Holiday, id=holiday_id)
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # Проверяем режим работы
        weekday = date_obj.weekday()
        start_hour = int(selected_time.split(':')[0])
        
        if weekday < 5:  # Пн-Пт
            if start_hour < 9 or start_hour >= 21:
                return JsonResponse({'success': False, 'message': 'Это время вне режима работы'})
        else:  # Сб-Вс
            if start_hour < 10 or start_hour >= 22:
                return JsonResponse({'success': False, 'message': 'Это время вне режима работы'})
        
        # Проверяем доступность (максимум 2 заявки на слот)
        existing_bookings = FullOrder.objects.filter(
            selected_date=date_obj,
            selected_time=selected_time
        ).count()
        
        if existing_bookings >= 2:
            return JsonResponse({'success': False, 'message': 'Это время уже полностью занято'})
        
        # Определяем номер свободного зала
        hall_number = 1
        if existing_bookings == 1:
            # Если есть одна заявка, смотрим какой зал занят
            first_booking = FullOrder.objects.filter(
                selected_date=date_obj,
                selected_time=selected_time
            ).first()
            hall_number = 2 if first_booking.hall_number == 1 else 1
        
        # Создаем заявку (она же занятый слот)
        order = FullOrder.objects.create(
            holiday=holiday,
            full_name=full_name,
            phone=phone,
            children_count=int(children_count),
            age_of_children=age_of_children,
            notes=notes,
            selected_date=date_obj,
            selected_time=selected_time,
            hall_number=hall_number
        )
        
        return JsonResponse({'success': True, 'message': 'Зал успешно забронирован!'})
        
    except Exception as e:
        print(f"Ошибка: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'message': str(e)})

def create_review(request):
    """Создание отзыва"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Отзыв отправлен!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})

def register_training(request):
    """Запись на тренировку"""
    if request.method == 'POST':
        try:
            parent_name = request.POST.get('parent_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            child_name = request.POST.get('child_name', '').strip()
            age = request.POST.get('age', '').strip()
            age_group = request.POST.get('age_group', '')
            visit_type = request.POST.get('visit_type', 'trial')
            
            if not all([parent_name, phone, child_name, age, age_group]):
                return JsonResponse({'success': False, 'message': 'Заполните все поля'})
            
            training_reg = TrainingRegistration.objects.create(
                parent_name=parent_name,
                phone=phone,
                child_name=child_name,
                child_age=int(age),
                age_group=age_group,
                visit_type=visit_type
            )
            
            return JsonResponse({'success': True, 'message': 'Заявка отправлена!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})