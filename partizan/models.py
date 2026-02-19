from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    """Категории праздников"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание", blank=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name

class Holiday(models.Model):
    """Праздники"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                related_name='holidays', verbose_name="Категория")
    title = models.CharField(max_length=200, verbose_name="Название праздника")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    image = models.ImageField(upload_to='holidays/', verbose_name="Фото")
    duration = models.CharField(max_length=50, verbose_name="Длительность")
    description = models.TextField(verbose_name="Описание")
    price = models.IntegerField(verbose_name="Цена (₽)", default=0)
    min_age = models.IntegerField(verbose_name="Минимальный возраст", default=3)
    max_age = models.IntegerField(verbose_name="Максимальный возраст", default=12)
    max_children = models.IntegerField(verbose_name="Максимум детей", default=10)
    active = models.BooleanField(default=True, verbose_name="Активный")
    
    class Meta:
        verbose_name = "Праздник"
        verbose_name_plural = "Праздники"
    
    def __str__(self):
        return self.title

class HolidayDate(models.Model):
    """Доступные даты и временные слоты для праздников"""
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, 
                               related_name='dates', verbose_name="Праздник")
    date = models.DateField(verbose_name="Дата")
    
    # Временные слоты
    TIME_SLOTS_2H = [
        ('10:00-12:00', '10:00 - 12:00'),
        ('12:00-14:00', '12:00 - 14:00'),
        ('14:00-16:00', '14:00 - 16:00'),
        ('16:00-18:00', '16:00 - 18:00'),
        ('18:00-20:00', '18:00 - 20:00'),
    ]
    
    TIME_SLOTS_4H = [
        ('10:00-14:00', '10:00 - 14:00'),
        ('14:00-18:00', '14:00 - 18:00'),
        ('18:00-22:00', '18:00 - 22:00'),
    ]
    
    TIME_SLOTS = TIME_SLOTS_2H + TIME_SLOTS_4H
    
    time_slot = models.CharField(
        max_length=20,
        choices=TIME_SLOTS,
        verbose_name="Временной слот",
        default='10:00-12:00'
    )
    
    max_bookings = models.IntegerField(
        verbose_name="Максимум заявок",
        default=2 
    )
    
    current_bookings = models.IntegerField(default=0, verbose_name="Текущие заявки")
    available = models.BooleanField(default=True, verbose_name="Доступно")
    
    class Meta:
        verbose_name = "Дата и время праздника"
        verbose_name_plural = "Даты и время праздников"
        unique_together = ['holiday', 'date', 'time_slot']
        ordering = ['date', 'time_slot']
    
    def __str__(self):
        return f"{self.holiday.title} - {self.date} {self.time_slot}"
    
    def is_available(self):
        return self.available and self.current_bookings < self.max_bookings
    
    def get_time_slot_display(self):
        all_slots = dict(self.TIME_SLOTS)
        return all_slots.get(self.time_slot, self.time_slot)
    
class Achievement(models.Model):
    """Достижения в спорте"""
    title = models.CharField(max_length=200, verbose_name="Название достижения")
    description = models.TextField(verbose_name="Описание достижения") 
    
    date = models.DateField(verbose_name="Дата достижения")
    image = models.ImageField(upload_to='achievements/', verbose_name="Фото", blank=True, null=True)
    
    PLACE_CHOICES = [
        (1, '1 место 🥇'),
        (2, '2 место 🥈'),
        (3, '3 место 🥉'),
        (4, 'Участие'),
        (5, 'Победа в номинации'),
    ]
    
    place = models.IntegerField(
        choices=PLACE_CHOICES, 
        verbose_name="Место/награда",
        default=1
    )
    
    city = models.CharField(
        max_length=100, 
        verbose_name="Город проведения",
        default="Москва"
    )
    
    competition_name = models.CharField(
        max_length=200, 
        verbose_name="Название соревнования",
        blank=True,
        default=""  # Добавляем default
    )
    
    age_category = models.CharField(
        max_length=100, 
        verbose_name="Возрастная категория",
        blank=True,
        default=""  # Добавляем default
    )
    
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
        ordering = ['-date', 'order']
    
    def __str__(self):
        return self.title
    
    def get_place_icon(self):
        """Получить иконку для места"""
        icons = {
            1: '🥇',
            2: '🥈', 
            3: '🥉',
            4: '🎯',
            5: '🏆'
        }
        return icons.get(self.place, '🏅')
    
    def get_place_text(self):
        """Получить текст для места"""
        texts = {
            1: '1 место',
            2: '2 место',
            3: '3 место',
            4: 'Участие',
            5: 'Победа в номинации'
        }
        return texts.get(self.place, 'Участие')



class Review(models.Model):
    """Отзывы"""
    name = models.CharField(max_length=100, verbose_name="Имя")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    approved = models.BooleanField(default=False, verbose_name="Одобрен")
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}/5"

class QuickOrder(models.Model):
    """Быстрая заявка"""
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, verbose_name="Праздник")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    processed = models.BooleanField(default=False, verbose_name="Обработано")
    
    class Meta:
        verbose_name = "Быстрая заявка"
        verbose_name_plural = "Быстрые заявки"
    
    def __str__(self):
        return f"{self.holiday.title} - {self.phone}"

class FullOrder(models.Model):
    """Полная заявка"""
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, verbose_name="Праздник")
    holiday_date = models.ForeignKey(HolidayDate, on_delete=models.CASCADE, verbose_name="Дата")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    children_count = models.IntegerField(verbose_name="Количество детей")
    age_of_children = models.CharField(max_length=200, verbose_name="Возраст детей")
    notes = models.TextField(verbose_name="Примечания", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    processed = models.BooleanField(default=False, verbose_name="Обработано")
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    
    def __str__(self):
        return f"{self.full_name} - {self.holiday.title}"

class Contact(models.Model):
    """Контакты"""
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    working_hours = models.CharField(max_length=100, verbose_name="Режим работы")
    vk_link = models.URLField(verbose_name="ВКонтакте", blank=True)
    telegram_link = models.URLField(verbose_name="Telegram", blank=True)
    instagram_link = models.URLField(verbose_name="Instagram", blank=True)
    
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
    
    def __str__(self):
        return "Контакты"
    

class TrainingRegistration(models.Model):
    """Заявки на тренировки"""
    GROUP_CHOICES = [
        ('under_13', 'Дети до 13 лет'),
        ('13_16', 'Подростки 13-16 лет'),
        ('adult', 'Взрослые 17+'),
    ]
    
    VISIT_CHOICES = [
        ('trial', 'Пробное занятие (бесплатно)'),
        ('single', 'Разовое посещение (700 ₽)'),
        ('subscription', 'Абонемент 8 занятий (4 000 ₽)'),
    ]
    
    parent_name = models.CharField(max_length=200, verbose_name="Имя родителя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    child_name = models.CharField(max_length=200, verbose_name="Имя ребенка")
    child_age = models.IntegerField(verbose_name="Возраст ребенка")
    age_group = models.CharField(max_length=20, choices=GROUP_CHOICES, verbose_name="Группа")
    visit_type = models.CharField(max_length=20, choices=VISIT_CHOICES, verbose_name="Тип посещения", default='trial')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    processed = models.BooleanField(default=False, verbose_name="Обработано")
    
    class Meta:
        verbose_name = "Заявка на тренировку"
        verbose_name_plural = "Заявки на тренировки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.parent_name} - {self.child_name} ({self.created_at.strftime('%d.%m.%Y')})"