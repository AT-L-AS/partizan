from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from partizan.models import Holiday, HolidayDate
import calendar

class Command(BaseCommand):
    help = 'Создает доступные даты для праздников на месяц вперед'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Количество дней вперед')

    def handle(self, *args, **options):
        days_ahead = options['days']
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        holidays = Holiday.objects.filter(active=True)
        created_count = 0
        
        for holiday in holidays:
            # Определяем длительность праздника
            duration = holiday.duration
            is_4_hours = '4 часа' in duration or '4.5 часа' in duration or '5 часов' in duration
            
            # Выбираем слоты в зависимости от длительности
            if is_4_hours:
                time_slots = ['10:00-14:00', '14:00-18:00', '18:00-22:00']
            else:
                time_slots = ['10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00']
            
            current_date = today
            while current_date <= end_date:
                # Проверяем день недели для времени работы
                weekday = current_date.weekday()  # 0-6 (пн-вс)
                
                for time_slot in time_slots:
                    # Проверяем по времени работы
                    start_hour = int(time_slot.split(':')[0])
                    
                    # Будни: 9-21
                    if weekday < 5:  # Пн-Пт
                        if start_hour < 9 or start_hour >= 21:
                            continue
                    # Выходные: 10-19
                    else:  # Сб-Вс
                        if start_hour < 10 or start_hour >= 19:
                            continue
                    
                    # Создаем слот, если его нет
                    obj, created = HolidayDate.objects.get_or_create(
                        holiday=holiday,
                        date=current_date,
                        time_slot=time_slot,
                        defaults={
                            'max_bookings': 3,
                            'current_bookings': 0,
                            'available': True
                        }
                    )
                    if created:
                        created_count += 1
                
                current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Создано {created_count} временных слотов на {days_ahead} дней вперед')
        )