from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from .models import *
from .forms import *
from django.utils import timezone
from datetime import date

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['achievements'] = Achievement.objects.all()[:3]
        context['holidays'] = Holiday.objects.filter(active=True)[:3]
        context['reviews'] = Review.objects.filter(approved=True)
        return context

class AchievementsView(ListView):
    model = Achievement
    template_name = 'achievements.html'
    context_object_name = 'achievements'
    ordering = ['-date']

class TrainingsView(TemplateView):
    template_name = 'trainings.html'

class AboutView(TemplateView):
    template_name = 'about.html'

class HolidaysView(ListView):
    model = Holiday
    template_name = 'holidays.html'
    context_object_name = 'holidays'
    
    def get_queryset(self):
        queryset = Holiday.objects.filter(active=True)
        
        # Фильтр по категории
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Фильтр по возрасту
        age = self.request.GET.get('age')
        if age and age.isdigit():
            age = int(age)
            queryset = queryset.filter(min_age__lte=age, max_age__gte=age)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Добавляем текущий возраст в контекст для шаблона
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
        
        from datetime import date
        
        # Получаем доступные слоты
        available_slots = HolidayDate.objects.filter(
            holiday=holiday,
            date__gte=date.today()
        ).order_by('date', 'time_slot')
        
        # Группируем по датам
        grouped_dates = {}
        
        for slot in available_slots:
            if slot.is_available():
                date_str = slot.date.strftime('%d.%m.%Y')
                weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                weekday = weekdays[slot.date.weekday()]
                date_display = f"{date_str} ({weekday})"
                
                if date_display not in grouped_dates:
                    grouped_dates[date_display] = []
                
                grouped_dates[date_display].append({
                    'id': slot.id,
                    'time': slot.get_time_slot_display(),
                    'available': slot.max_bookings - slot.current_bookings,
                    'max_bookings': slot.max_bookings,
                    'raw_time': slot.time_slot
                })
        
        context['available_dates_grouped'] = [
            {'date': date_str, 'slots': slots} 
            for date_str, slots in grouped_dates.items()
        ]
        
        context['quick_form'] = QuickOrderForm(initial={'holiday': holiday.id})
        context['full_form'] = FullOrderForm()
        return context

def get_available_dates(request, holiday_id):
    """Получить доступные даты и время для праздника"""
    holiday = get_object_or_404(Holiday, id=holiday_id)
    
    # Получаем все доступные слоты
    available_slots = HolidayDate.objects.filter(
        holiday=holiday,
        available=True,
        date__gte=date.today()
    ).order_by('date', 'time_slot')
    
    # Группируем по датам
    dates_dict = {}
    for slot in available_slots:
        if slot.is_available():
            date_str = slot.date.strftime('%d.%m.%Y')
            if date_str not in dates_dict:
                dates_dict[date_str] = []
            
            dates_dict[date_str].append({
                'id': slot.id,
                'time': slot.time_slot,
                'available': slot.max_bookings - slot.current_bookings
            })
    
    # Формируем ответ
    result = []
    for date_str, slots in dates_dict.items():
        result.append({
            'date': date_str,
            'slots': slots
        })
    
    return JsonResponse({'dates': result})

def create_quick_order(request):
    if request.method == 'POST':
        form = QuickOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            holiday_id = request.POST.get('holiday_id')
            if holiday_id:
                order.holiday_id = holiday_id
                order.save()
                return JsonResponse({'success': True, 'message': 'Заявка отправлена!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Ошибка'})

def create_full_order(request):
    """Создание полной заявки с проверкой лимита в 2 заявки"""
    if request.method == 'POST':
        try:
            form = FullOrderForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                holiday_id = request.POST.get('holiday_id')
                date_id = request.POST.get('date_id')
                
                if not holiday_id or not date_id:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Не выбрана дата или праздник'
                    })
                
                holiday = get_object_or_404(Holiday, id=holiday_id)
                holiday_date = get_object_or_404(HolidayDate, id=date_id)
                
                # Проверяем, доступен ли слот (максимум 2 заявки)
                if holiday_date.is_available():
                    # Проверяем, не превышен ли лимит
                    if holiday_date.current_bookings >= holiday_date.max_bookings:
                        holiday_date.available = False
                        holiday_date.save()
                        return JsonResponse({
                            'success': False, 
                            'message': 'К сожалению, это время уже занято. Выберите другое.'
                        })
                    
                    # Сохраняем заявку
                    order.holiday = holiday
                    order.holiday_date = holiday_date
                    order.save()
                    
                    # Увеличиваем счетчик и проверяем лимит
                    holiday_date.current_bookings += 1
                    if holiday_date.current_bookings >= holiday_date.max_bookings:
                        holiday_date.available = False
                    holiday_date.save()
                    
                    return JsonResponse({
                        'success': True, 
                        'message': 'Заявка успешно отправлена! Мы свяжемся с вами для подтверждения.'
                    })
                else:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Это время уже недоступно. Выберите другой слот.'
                    })
            
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
            
        except Exception as e:
            print(f"Ошибка при создании заявки: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': 'Произошла ошибка при отправке заявки'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Метод не поддерживается'
    })

def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Отзыв отправлен!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Ошибка'})

# НОВЫЙ VIEW ДЛЯ ЗАЯВОК НА ТРЕНИРОВКИ
def register_training(request):
    """Обработка заявки на тренировку с сохранением в БД"""
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            parent_name = request.POST.get('parent_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            child_name = request.POST.get('child_name', '').strip()
            age = request.POST.get('age', '').strip()
            age_group = request.POST.get('age_group', '')
            visit_type = request.POST.get('visit_type', 'trial')
            
            # Валидация
            if not all([parent_name, phone, child_name, age, age_group]):
                return JsonResponse({
                    'success': False,
                    'message': 'Заполните все поля'
                })
            
            # Создаем запись в БД
            training_reg = TrainingRegistration.objects.create(
                parent_name=parent_name,
                phone=phone,
                child_name=child_name,
                child_age=int(age),
                age_group=age_group,
                visit_type=visit_type
            )
            
            print(f"✅ Заявка #{training_reg.id} сохранена в БД")
            
            return JsonResponse({
                'success': True,
                'message': 'Заявка отправлена!'
            })
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Ошибка: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})