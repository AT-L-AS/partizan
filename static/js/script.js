document.addEventListener('DOMContentLoaded', function() {
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
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
                    alert(data.message);
                    this.reset();
                } else {
                    alert('Ошибка: ' + (data.message || 'Попробуйте еще раз'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при отправке отзыва');
            });
        });
    }
    
    const dateSelect = document.getElementById('date-select');
    if (dateSelect) {
        const holidayId = document.querySelector('input[name="holiday_id"]').value;
        
        fetch(`/api/get-available-dates/${holidayId}/`)
            .then(response => response.json())
            .then(data => {
                dateSelect.innerHTML = '<option value="">-- Выберите дату --</option>';
                data.dates.forEach(date => {
                    const option = document.createElement('option');
                    option.value = date.id;
                    option.textContent = date.date;
                    dateSelect.appendChild(option);
                });
            });
    }
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
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
                alert('Пожалуйста, заполните все обязательные поля');
            }
        });
    });
    
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
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
});

document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы слайдера
    const track = document.getElementById('review-track'); // Дорожка со слайдами
    const slides = document.querySelectorAll('.home-review-slide'); // Все слайды
    const prevBtn = document.getElementById('review-prev'); // Кнопка "назад"
    const nextBtn = document.getElementById('review-next'); // Кнопка "вперед"
    
    // Если нет слайдера или слайдов - выходим
    if (!track || slides.length === 0) return;
    
    // Текущие настройки
    let currentIndex = 0; // Текущий индекс
    let slidesPerView = getSlidesPerView(); // Сколько слайдов показываем
    const totalSlides = slides.length; // Всего слайдов
    const maxIndex = Math.max(0, totalSlides - slidesPerView); // Максимальный индекс
    
    /* Определяет сколько слайдов показывать в зависимости от ширины экрана    */
    function getSlidesPerView() {
        if (window.innerWidth <= 768) return 1; 
        if (window.innerWidth <= 992) return 2; 
        return 3;
    }
    
    /* Обновляет позицию слайдера */
    function updateSlider() {
        const slideWidth = slides[0].offsetWidth; // Ширина одного слайда
        const gap = 25; // Отступ между слайдами (должен совпадать с CSS)
        const translateX = currentIndex * (slideWidth + gap); // Смещение
        
        track.style.transform = `translateX(-${translateX}px)`; // Двигаем дорожку
        
        // Обновляем состояние кнопок
        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0; // Блокируем "назад" если первый слайд
        }
        
        if (nextBtn) {
            nextBtn.disabled = currentIndex >= maxIndex; // Блокируем "вперед" если последний
        }
    }
    
    // Обработчики для кнопок
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (currentIndex > 0) {
                currentIndex--; // Листаем назад
                updateSlider();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (currentIndex < maxIndex) {
                currentIndex++; // Листаем вперед
                updateSlider();
            }
        });
    }
    
    // Обработка изменения размера окна
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            const newSlidesPerView = getSlidesPerView();
            if (newSlidesPerView !== slidesPerView) {
                slidesPerView = newSlidesPerView;
                const newMaxIndex = Math.max(0, totalSlides - slidesPerView);
                currentIndex = Math.min(currentIndex, newMaxIndex); // Корректируем индекс
                updateSlider();
            } else {
                updateSlider();
            }
        }, 250);
    });
    
    // Поддержка свайпов на мобильных устройствах
    let touchStartX = 0;
    let touchEndX = 0;
    
    track.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX; // Запоминаем где начали касание
    }, { passive: true });
    
    track.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX; // Запоминаем где закончили
        handleSwipe(); // Обрабатываем свайп
    }, { passive: true });
    
    /* Обрабатывает свайп влево/вправо*/
    function handleSwipe() {
        const swipeThreshold = 50; // Минимальная длина свайпа
        const diff = touchStartX - touchEndX; // Разница между началом и концом
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0 && currentIndex < maxIndex) {
                // Свайп влево - листаем вперед
                currentIndex++;
                updateSlider();
            } else if (diff < 0 && currentIndex > 0) {
                // Свайп вправо - листаем назад
                currentIndex--;
                updateSlider();
            }
        }
    }
    
    // Автоматическая прокрутка
    let autoplayInterval;
    let isHovering = false;
    
    /* Запускает автоматическую прокрутку */
    function startAutoplay() {
        if (autoplayInterval) clearInterval(autoplayInterval);
        autoplayInterval = setInterval(() => {
            if (!isHovering && slides.length > slidesPerView) {
                if (currentIndex < maxIndex) {
                    currentIndex++; // Листаем вперед
                } else {
                    currentIndex = 0; // Возвращаемся в начало
                }
                updateSlider();
            }
        }, 2500); // Прокрутка
    }
    
    /* Останавливает автоматическую прокрутку */
    function stopAutoplay() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
        }
    }
    
    // Запускаем автопрокрутку
    startAutoplay();
    
    // Останавливаем при наведении мыши
    const sliderContainer = document.querySelector('.home-reviews-slider-container');
    if (sliderContainer) {
        sliderContainer.addEventListener('mouseenter', function() {
            isHovering = true;
            stopAutoplay(); // Останавливаем
        });
        
        sliderContainer.addEventListener('mouseleave', function() {
            isHovering = false;
            startAutoplay(); // Запускаем снова
        });
    }
    
    // Инициализация - показываем первую позицию
    updateSlider();
    
    // Очищаем интервал при уходе со страницы
    window.addEventListener('beforeunload', function() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
        }
    });
});


// holiday
document.addEventListener('DOMContentLoaded', function() {
    const ageSlider = document.getElementById('child-age-slider');
    const ageValue = document.getElementById('holid-age-value');
    
    if (ageSlider) {
        ageSlider.addEventListener('input', function() {
            ageValue.textContent = this.value + ' лет';
        });
    }
});

// Сохраняем категорию при отправке формы возраста
document.getElementById('holid-age-filter-form')?.addEventListener('submit', function(e) {
    const urlParams = new URLSearchParams(window.location.search);
    const pathSegments = window.location.pathname.split('/');
    const categoryFromPath = pathSegments[pathSegments.indexOf('holidays') + 1];
    
    // Если есть категория в URL и нет скрытого поля, добавляем
    if (categoryFromPath && categoryFromPath !== 'holidays' && !this.querySelector('input[name="category"]')) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'category';
        input.value = categoryFromPath;
        this.appendChild(input);
    }
});
   
// trainings
document.getElementById('training-registration-form').addEventListener('submit', function(e) {
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
            alert('Заявка отправлена! Мы свяжемся с вами в ближайшее время.');
            this.reset();
        } else {
            alert('Ошибка: ' + (data.message || 'Попробуйте еще раз'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке заявки');
    });
});