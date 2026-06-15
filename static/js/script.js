document.addEventListener('DOMContentLoaded', function () {
    // ========== ФОРМА ОТЗЫВОВ ==========
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/api/create-review/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message || 'Отзыв успешно отправлен!', 'success');
                        this.reset();
                    } else {
                        showNotification(data.message || 'Ошибка при отправке отзыва', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при отправке отзыва', 'error');
                });
        });
    }

    // ========== ДАТЫ ДЛЯ ПРАЗДНИКОВ ==========
    const dateSelect = document.getElementById('date-select');
    if (dateSelect) {
        const holidayId = document.querySelector('input[name="holiday_id"]')?.value;
        if (holidayId) {
            fetch(`/api/get-available-dates/${holidayId}/`)
                .then(response => response.json())
                .then(data => {
                    dateSelect.innerHTML = '<option value="">-- Выберите дату --</option>';
                    if (data.dates && data.dates.length > 0) {
                        data.dates.forEach(date => {
                            const option = document.createElement('option');
                            option.value = date.id;
                            option.textContent = date.date;
                            dateSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Ошибка загрузки дат:', error);
                    showNotification('Ошибка загрузки дат', 'error');
                });
        }
    }

    // ========== ВАЛИДАЦИЯ ФОРМ ==========
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Пожалуйста, заполните все обязательные поля', 'error');
            }
        });
    });

    // ========== МАСКА ДЛЯ ТЕЛЕФОНА ==========
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function (e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value[0] === '7' || value[0] === '8') {
                    value = value.substring(1);
                }

                let formatted = '+7 ';
                if (value.length > 0) formatted += '(' + value.substring(0, 3);
                if (value.length > 3) formatted += ') ' + value.substring(3, 6);
                if (value.length > 6) formatted += '-' + value.substring(6, 8);
                if (value.length > 8) formatted += '-' + value.substring(8, 10);

                this.value = formatted;
            }
        });
    });

    // ========== СЛАЙДЕР ОТЗЫВОВ ==========
    const track = document.getElementById('review-track');
    const slides = document.querySelectorAll('.home-review-slide');
    const prevBtn = document.getElementById('review-prev');
    const nextBtn = document.getElementById('review-next');

    if (track && slides.length > 0) {
        let currentIndex = 0;
        let slidesPerView = getSlidesPerView();
        const totalSlides = slides.length;
        const maxIndex = Math.max(0, totalSlides - slidesPerView);

        function getSlidesPerView() {
            if (window.innerWidth <= 768) return 1;
            if (window.innerWidth <= 992) return 2;
            return 3;
        }

        function updateSlider() {
            const slideWidth = slides[0].offsetWidth;
            const gap = 25;
            const translateX = currentIndex * (slideWidth + gap);

            track.style.transform = `translateX(-${translateX}px)`;

            if (prevBtn) prevBtn.disabled = currentIndex === 0;
            if (nextBtn) nextBtn.disabled = currentIndex >= maxIndex;
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateSlider();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                if (currentIndex < maxIndex) {
                    currentIndex++;
                    updateSlider();
                }
            });
        }

        let resizeTimeout;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function () {
                const newSlidesPerView = getSlidesPerView();
                if (newSlidesPerView !== slidesPerView) {
                    slidesPerView = newSlidesPerView;
                    const newMaxIndex = Math.max(0, totalSlides - slidesPerView);
                    currentIndex = Math.min(currentIndex, newMaxIndex);
                    updateSlider();
                } else {
                    updateSlider();
                }
            }, 250);
        });

        // Свайпы
        let touchStartX = 0;
        let touchEndX = 0;

        track.addEventListener('touchstart', function (e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        track.addEventListener('touchend', function (e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0 && currentIndex < maxIndex) {
                    currentIndex++;
                    updateSlider();
                } else if (diff < 0 && currentIndex > 0) {
                    currentIndex--;
                    updateSlider();
                }
            }
        }

        // Автопрокрутка
        let autoplayInterval;
        let isHovering = false;

        function startAutoplay() {
            if (autoplayInterval) clearInterval(autoplayInterval);
            autoplayInterval = setInterval(() => {
                if (!isHovering && slides.length > slidesPerView) {
                    if (currentIndex < maxIndex) {
                        currentIndex++;
                    } else {
                        currentIndex = 0;
                    }
                    updateSlider();
                }
            }, 2500);
        }

        function stopAutoplay() {
            if (autoplayInterval) {
                clearInterval(autoplayInterval);
            }
        }

        startAutoplay();

        const sliderContainer = document.querySelector('.home-reviews-slider-container');
        if (sliderContainer) {
            sliderContainer.addEventListener('mouseenter', function () {
                isHovering = true;
                stopAutoplay();
            });

            sliderContainer.addEventListener('mouseleave', function () {
                isHovering = false;
                startAutoplay();
            });
        }

        updateSlider();

        window.addEventListener('beforeunload', function () {
            if (autoplayInterval) {
                clearInterval(autoplayInterval);
            }
        });
    }

    // ========== БУРГЕР-МЕНЮ ==========
    const burgerMenu = document.getElementById('burger-menu');
    const mainNav = document.getElementById('main-nav');

    if (burgerMenu && mainNav) {
        burgerMenu.addEventListener('click', function (e) {
            e.stopPropagation();
            this.classList.toggle('active');
            mainNav.classList.toggle('active');

            if (mainNav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        document.addEventListener('click', function (event) {
            if (mainNav.classList.contains('active') &&
                !mainNav.contains(event.target) &&
                !burgerMenu.contains(event.target)) {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 768 && mainNav.classList.contains('active')) {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    } else {
        console.log('Бургер меню не найдено');
    }

    // ========== СЛАЙДЕР ВОЗРАСТА (HOLIDAY) ==========
    const ageSlider = document.getElementById('child-age-slider');
    const ageValue = document.getElementById('holid-age-value');

    if (ageSlider && ageValue) {
        function updateAgeFromUrl() {
            const urlParams = new URLSearchParams(window.location.search);
            const ageFromUrl = urlParams.get('age');

            if (ageFromUrl) {
                ageSlider.value = ageFromUrl;
                ageValue.textContent = ageFromUrl + ' лет';
                console.log('Возраст из URL:', ageFromUrl);
            } else {
                ageValue.textContent = ageSlider.value + ' лет';
            }
        }

        updateAgeFromUrl();

        ageSlider.addEventListener('input', function () {
            ageValue.textContent = this.value + ' лет';
        });

        ageSlider.addEventListener('change', function () {
            console.log('Выбран возраст:', this.value);
        });

    } else {
    }

    // ========== РЕГИСТРАЦИЯ НА ТРЕНИРОВКУ ==========
    const trainingForm = document.getElementById('training-registration-form');
    if (trainingForm) {
        trainingForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch('/api/register-training/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Заявка отправлена! Мы свяжемся с вами в ближайшее время.', 'success');
                        this.reset();
                    } else {
                        showNotification(data.message || 'Ошибка при отправке заявки', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при отправке заявки', 'error');
                });
        });
    }
});

// Функция для отображения уведомлений
function showNotification(message, type = 'success') {
    let notificationContainer = document.querySelector('.hol_notification_container');

    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'hol_notification_container';
        document.body.appendChild(notificationContainer);
    }

    const notification = document.createElement('div');
    notification.className = `hol_notification hol_notification_${type}`;
    notification.innerHTML = `
            <div class="hol_notification_icon">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            </div>
            <div class="hol_notification_content">
                <div class="hol_notification_title">${type === 'success' ? 'Успешно!' : 'Внимание!'}</div>
                <div class="hol_notification_message">${message}</div>
            </div>
            <button class="hol_notification_close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

    notificationContainer.appendChild(notification);

    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);

    setTimeout(() => notification.classList.add('hol_notification_show'), 10);
}

class HolidayBooking {
    constructor(holidayDuration, bookedSlots, maxChildren) {
        this.holidayDuration = holidayDuration;
        this.bookedSlots = bookedSlots;
        this.maxChildren = maxChildren;
        this.currentDate = new Date();
        this.selectedDate = null;
        this.selectedTimeSlot = null;

        // Инициализируем слоты
        this.initTimeSlots();
        this.init();
    }

    initTimeSlots() {
        const is4Hours = this.holidayDuration && this.holidayDuration.includes('4');

        if (is4Hours) {
            // Для 4-часовых праздников
            this.timeSlots = {
                // Будни (Пн-Пт: 9:00-21:00)
                weekday: [
                    { value: '9:00-13:00', label: '9:00 - 13:00' },
                    { value: '13:00-17:00', label: '13:00 - 17:00' },
                    { value: '17:00-21:00', label: '17:00 - 21:00' }
                ],
                // Выходные (Сб-Вс: 10:00-22:00)
                weekend: [
                    { value: '10:00-14:00', label: '10:00 - 14:00' },
                    { value: '14:00-18:00', label: '14:00 - 18:00' },
                    { value: '18:00-22:00', label: '18:00 - 22:00' }
                ]
            };
        } else {
            // Для 2-часовых праздников
            this.timeSlots = {
                // Будни (Пн-Пт: 9:00-21:00)
                weekday: [
                    { value: '9:00-11:00', label: '9:00 - 11:00' },
                    { value: '11:00-13:00', label: '11:00 - 13:00' },
                    { value: '13:00-15:00', label: '13:00 - 15:00' },
                    { value: '15:00-17:00', label: '15:00 - 17:00' },
                    { value: '17:00-19:00', label: '17:00 - 19:00' },
                    { value: '19:00-21:00', label: '19:00 - 21:00' }
                ],
                // Выходные (Сб-Вс: 10:00-22:00)
                weekend: [
                    { value: '10:00-12:00', label: '10:00 - 12:00' },
                    { value: '12:00-14:00', label: '12:00 - 14:00' },
                    { value: '14:00-16:00', label: '14:00 - 16:00' },
                    { value: '16:00-18:00', label: '16:00 - 18:00' },
                    { value: '18:00-20:00', label: '18:00 - 20:00' },
                    { value: '20:00-22:00', label: '20:00 - 22:00' }
                ]
            };
        }
    }

    init() {
        this.renderCalendar();
        this.setupEventListeners();
        this.setupFormHandlers();
    }

    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    parseDate(dateStr) {
        const [year, month, day] = dateStr.split('-').map(Number);
        return new Date(year, month - 1, day);
    }

    isWeekend(date) {
        const day = date.getDay();
        return day === 0 || day === 6; // 0 - воскресенье, 6 - суббота
    }

    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);

        let startingDay = firstDay.getDay();
        if (startingDay === 0) startingDay = 7; // Воскресенье = 7

        let html = '';

        // Пустые ячейки для дней предыдущего месяца
        for (let i = 1; i < startingDay; i++) {
            html += '<div class="hol_calendar_day hol_empty"></div>';
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const twoWeeksLater = new Date(today);
        twoWeeksLater.setDate(today.getDate() + 14);

        for (let day = 1; day <= lastDay.getDate(); day++) {
            const date = new Date(year, month, day);
            date.setHours(0, 0, 0, 0);
            const dateStr = this.formatDate(date);

            let classes = 'hol_calendar_day';

            if (date < today || date > twoWeeksLater) {
                classes += ' hol_disabled';
            } else {
                classes += ' hol_available';
            }

            if (this.selectedDate) {
                const selectedDate = this.parseDate(this.selectedDate);
                selectedDate.setHours(0, 0, 0, 0);
                if (date.getTime() === selectedDate.getTime()) {
                    classes += ' hol_selected';
                }
            }

            if (date.getTime() === today.getTime()) {
                classes += ' hol_today';
            }

            html += `<div class="${classes}" data-date="${dateStr}">${day}</div>`;
        }

        document.getElementById('calendar-days').innerHTML = html;
        document.getElementById('current-month').textContent =
            this.getMonthName(month) + ' ' + year;

        this.updateNavButtons();
    }

    updateNavButtons() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const currentMonthYear = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const twoWeeksLater = new Date(today);
        twoWeeksLater.setDate(today.getDate() + 14);

        const prevBtn = document.getElementById('prev-month');
        const nextBtn = document.getElementById('next-month');

        const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
        if (currentMonthYear <= currentMonthStart) {
            prevBtn.disabled = true;
        } else {
            prevBtn.disabled = false;
        }

        const twoWeeksLaterMonthStart = new Date(twoWeeksLater.getFullYear(), twoWeeksLater.getMonth(), 1);
        if (currentMonthYear >= twoWeeksLaterMonthStart) {
            nextBtn.disabled = true;
        } else {
            nextBtn.disabled = false;
        }
    }

    getMonthName(month) {
        const months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ];
        return months[month];
    }

    onDateClick(dateStr) {
        this.selectedDate = dateStr;
        document.getElementById('selected-date').value = dateStr;
        this.renderCalendar();
        this.showTimeSlots(dateStr);
    }

    showTimeSlots(dateStr) {
        const [year, month, day] = dateStr.split('-').map(Number);
        const date = new Date(year, month - 1, day);
        const isWeekend = this.isWeekend(date);

        const slotsToShow = isWeekend ? this.timeSlots.weekend : this.timeSlots.weekday;
        const bookingsForDate = this.bookedSlots[dateStr] || {};

        function getHallWord(count) {
            if (count === 1) return 'место';
            if (count >= 2 && count <= 4) return 'места';
            return 'мест';
        }

        let slotsHtml = '';

        if (slotsToShow.length === 0) {
            slotsHtml = '<p class="hol_no_slots">Нет доступного времени для этой даты</p>';
        } else {
            slotsToShow.forEach(slot => {
                const bookedCount = bookingsForDate[slot.value] || 0;

                // Определяем, является ли слот 4-часовым
                const is4HourSlot = slot.value.includes('13:00') ||
                    slot.value.includes('17:00') ||
                    slot.value.includes('21:00') ||
                    slot.value.includes('14:00') ||
                    slot.value.includes('18:00') ||
                    slot.value.includes('22:00');

                let isAvailable;
                let freeHalls;

                if (is4HourSlot) {
                    // Для 4-часового слота проверяем оба входящих в него 2-часовых слота
                    const [start, end] = slot.value.split('-').map(t => parseInt(t.split(':')[0]));
                    const slot1 = `${start}:00-${start + 2}:00`;
                    const slot2 = `${start + 2}:00-${end}:00`;

                    const booked1 = bookingsForDate[slot1] || 0;
                    const booked2 = bookingsForDate[slot2] || 0;

                    // 4-часовой слот доступен, если хотя бы один из 2-часовых слотов имеет свободные места
                    // и оба слота не заполнены полностью
                    if (booked1 >= 2 || booked2 >= 2) {
                        isAvailable = false;
                        freeHalls = 0;
                    } else {
                        // Максимальное количество заявок в любом из слотов определяет доступность
                        const maxBooked = Math.max(booked1, booked2);
                        freeHalls = 2 - maxBooked;
                        isAvailable = freeHalls > 0;
                    }
                } else {
                    // Для 2-часового слота
                    isAvailable = bookedCount < 2;
                    freeHalls = 2 - bookedCount;
                }

                let remainingText;
                if (isAvailable) {
                    remainingText = `${freeHalls} ${getHallWord(freeHalls)} свободно`;
                } else {
                    remainingText = 'нет свободных мест';
                }

                let btnClass = 'hol_time_slot_btn';
                if (!isAvailable) btnClass += ' hol_disabled';
                if (this.selectedTimeSlot === slot.value) btnClass += ' hol_selected';

                slotsHtml += `
                <button type="button" class="${btnClass}" 
                        data-time="${slot.value}"
                        ${isAvailable ? '' : 'disabled'}>
                    ${slot.label}<br>
                    <small>${remainingText}</small>
                </button>
            `;
            });
        }

        const scheduleInfo = isWeekend
            ? '<div class="hol_schedule_info"><p><i class="fas fa-calendar-week"></i> Режим работы в выходные: 10:00 - 22:00</p></div>'
            : '<div class="hol_schedule_info"><p><i class="fas fa-calendar-week"></i> Режим работы в будни: 9:00 - 21:00</p></div>';

        document.getElementById('time-slots').innerHTML = slotsHtml + scheduleInfo;
        document.getElementById('time-slots-container').style.display = 'block';

        document.querySelectorAll('.hol_time_slot_btn:not(.hol_disabled)').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.hol_time_slot_btn').forEach(b =>
                    b.classList.remove('hol_selected'));
                btn.classList.add('hol_selected');
                this.selectedTimeSlot = btn.dataset.time;
                document.getElementById('selected-time').value = btn.dataset.time;
            });
        });
    }

    setupEventListeners() {
        document.getElementById('calendar-days').addEventListener('click', (e) => {
            const dayEl = e.target.closest('.hol_calendar_day');
            if (!dayEl || dayEl.classList.contains('hol_empty') ||
                dayEl.classList.contains('hol_disabled')) return;

            const date = dayEl.dataset.date;
            this.onDateClick(date);
        });

        document.getElementById('prev-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
            document.getElementById('time-slots-container').style.display = 'none';
            this.selectedDate = null;
            this.selectedTimeSlot = null;
            document.getElementById('selected-date').value = '';
            document.getElementById('selected-time').value = '';
        });

        document.getElementById('next-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
            document.getElementById('time-slots-container').style.display = 'none';
            this.selectedDate = null;
            this.selectedTimeSlot = null;
            document.getElementById('selected-date').value = '';
            document.getElementById('selected-time').value = '';
        });
    }

    setupFormHandlers() {
        document.querySelectorAll('input[type="tel"]').forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 0) {
                    if (value[0] === '7' || value[0] === '8') value = value.substring(1);
                    let formatted = '+7 ';
                    if (value.length > 0) formatted += '(' + value.substring(0, 3);
                    if (value.length > 3) formatted += ') ' + value.substring(3, 6);
                    if (value.length > 6) formatted += '-' + value.substring(6, 8);
                    if (value.length > 8) formatted += '-' + value.substring(8, 10);
                    e.target.value = formatted;
                }
            });
        });

        document.getElementById('children-count')?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            if (value > this.maxChildren) {
                e.target.value = this.maxChildren;
                showNotification(`Максимальное количество детей: ${this.maxChildren}`, 'error');
            }
            if (value < 1) {
                e.target.value = 1;
            }
        });

        // Полная заявка
        document.getElementById('full-order-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullName = document.getElementById('full-name').value.trim();
            const phone = document.getElementById('full-phone').value.trim();
            const childrenCount = document.getElementById('children-count').value.trim();
            const ageOfChildren = document.getElementById('age-of-children').value.trim();

            if (!fullName) {
                showNotification('Пожалуйста, введите ФИО', 'error');
                document.getElementById('full-name').focus();
                return;
            }

            if (!phone) {
                showNotification('Пожалуйста, введите номер телефона', 'error');
                document.getElementById('full-phone').focus();
                return;
            }

            if (!childrenCount) {
                showNotification('Пожалуйста, укажите количество детей', 'error');
                document.getElementById('children-count').focus();
                return;
            }

            if (!ageOfChildren) {
                showNotification('Пожалуйста, укажите возраст детей', 'error');
                document.getElementById('age-of-children').focus();
                return;
            }

            if (!this.selectedDate) {
                showNotification('Пожалуйста, выберите дату', 'error');
                return;
            }

            if (!this.selectedTimeSlot) {
                showNotification('Пожалуйста, выберите время', 'error');
                return;
            }

            const formData = new FormData(e.target);

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';

            try {
                const response = await fetch('/api/create-full-order/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('✅ Заявка принята на рассмотрение! Мы свяжемся с вами в ближайшее время.', 'success');
                    e.target.reset();
                    document.getElementById('selected-date').value = '';
                    document.getElementById('selected-time').value = '';
                    document.getElementById('time-slots-container').style.display = 'none';
                    this.selectedDate = null;
                    this.selectedTimeSlot = null;
                    this.renderCalendar();
                } else {
                    showNotification(data.message || 'Ошибка при отправке заявки', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Произошла ошибка при отправке. Попробуйте позже.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });

        // Быстрая заявка
        document.getElementById('quick-order-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();

            const phone = document.getElementById('quick-phone').value.trim();
            if (!phone) {
                showNotification('Пожалуйста, введите номер телефона', 'error');
                document.getElementById('quick-phone').focus();
                return;
            }

            const formData = new FormData(e.target);

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';

            try {
                const response = await fetch('/api/create-quick-order/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('✅ Заявка принята на рассмотрение! Ожидайте звонка.', 'success');
                    e.target.reset();
                } else {
                    showNotification(data.message || 'Ошибка при отправке заявки', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Произошла ошибка при отправке. Попробуйте позже.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });

        document.querySelectorAll('.hol_tab_btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.hol_tab_btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.hol_tab_content').forEach(c => c.classList.remove('active'));

                btn.classList.add('active');
                const tabId = btn.dataset.tab;
                document.getElementById(tabId + '-tab').classList.add('active');
            });
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const holidayData = document.getElementById('holiday-data');
    if (holidayData) {
        const duration = holidayData.dataset.duration;
        const maxChildren = parseInt(holidayData.dataset.maxChildren) || 10;
        let bookedSlots = {};

        try {
            bookedSlots = JSON.parse(holidayData.dataset.bookedSlots || '{}');
            console.log('Загруженные слоты:', bookedSlots);
        } catch (e) {
            console.error('Ошибка парсинга занятых слотов:', e);
        }

        new HolidayBooking(duration, bookedSlots, maxChildren);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value[0] === '7' || value[0] === '8') value = value.substring(1);
                let formatted = '+7 ';
                if (value.length > 0) formatted += '(' + value.substring(0, 3);
                if (value.length > 3) formatted += ') ' + value.substring(3, 6);
                if (value.length > 6) formatted += '-' + value.substring(6, 8);
                if (value.length > 8) formatted += '-' + value.substring(8, 10);
                e.target.value = formatted;
            }
        });
    }
});


function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}