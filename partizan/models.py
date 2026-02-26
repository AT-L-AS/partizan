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
    duration = models.CharField(max_length=50, verbose_name="Длительность")  # "2 часа" или "4 часа"
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
    
    def is_4_hours(self):
        """Проверяет, длится ли праздник 4 часа"""
        return '4' in self.duration

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
        default=""
    )
    
    age_category = models.CharField(
        max_length=100, 
        verbose_name="Возрастная категория",
        blank=True,
        default=""
    )
    
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
        ordering = ['-date', 'order']
    
    def __str__(self):
        return self.title
    
    def get_place_icon(self):
        icons = {
            1: '🥇',
            2: '🥈', 
            3: '🥉',
            4: '🎯',
            5: '🏆'
        }
        return icons.get(self.place, '🏅')
    
    def get_place_text(self):
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
    """Быстрая заявка (только телефон)"""
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
    """ПОЛНАЯ ЗАЯВКА = ЗАНЯТЫЙ СЛОТ"""
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, verbose_name="Праздник")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    children_count = models.IntegerField(verbose_name="Количество детей")
    age_of_children = models.CharField(max_length=200, verbose_name="Возраст детей")
    notes = models.TextField(verbose_name="Примечания", blank=True)
    
    # Поля для слота
    selected_date = models.DateField(verbose_name="Выбранная дата")
    selected_time = models.CharField(max_length=20, verbose_name="Выбранное время")
    hall_number = models.IntegerField(verbose_name="Номер зала", default=1)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    processed = models.BooleanField(default=False, verbose_name="Обработано")
    
    class Meta:
        verbose_name = "Заявка на праздник"
        verbose_name_plural = "Заявки на праздники"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.holiday.title} - {self.selected_date} {self.selected_time}"

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
        return f"{self.parent_name} - {self.child_name}"