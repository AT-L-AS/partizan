document.addEventListener('DOMContentLoaded', function() {
    // ========== ФОРМА ОТЗЫВОВ ==========
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
    
    // ========== ДАТЫ ДЛЯ ПРАЗДНИКОВ ==========
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
    
    // ========== ВАЛИДАЦИЯ ФОРМ ==========
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
    
    // ========== МАСКА ДЛЯ ТЕЛЕФОНА ==========
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
            prevBtn.addEventListener('click', function() {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateSlider();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                if (currentIndex < maxIndex) {
                    currentIndex++;
                    updateSlider();
                }
            });
        }
        
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
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
        
        track.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        track.addEventListener('touchend', function(e) {
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
            sliderContainer.addEventListener('mouseenter', function() {
                isHovering = true;
                stopAutoplay();
            });
            
            sliderContainer.addEventListener('mouseleave', function() {
                isHovering = false;
                startAutoplay();
            });
        }
        
        updateSlider();
        
        window.addEventListener('beforeunload', function() {
            if (autoplayInterval) {
                clearInterval(autoplayInterval);
            }
        });
    }

    // ========== БУРГЕР-МЕНЮ ==========
    const burgerMenu = document.getElementById('burger-menu');
    const mainNav = document.getElementById('main-nav');
    
    if (burgerMenu && mainNav) {
        burgerMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            mainNav.classList.toggle('active');
            
            // Блокируем прокрутку body при открытом меню
            if (mainNav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Закрытие меню при клике на ссылку
        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Закрытие меню при клике вне его
        document.addEventListener('click', function(event) {
            if (!mainNav.contains(event.target) && !burgerMenu.contains(event.target)) {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Обработка изменения размера окна
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                burgerMenu.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // ========== СЛАЙДЕР ВОЗРАСТА (HOLIDAY) ==========
    const ageSlider = document.getElementById('child-age-slider');
    const ageValue = document.getElementById('holid-age-value');
    
    if (ageSlider) {
        ageSlider.addEventListener('input', function() {
            ageValue.textContent = this.value + ' лет';
        });
    }

    // ========== ФИЛЬТР ВОЗРАСТА (HOLIDAY) ==========
    document.getElementById('holid-age-filter-form')?.addEventListener('submit', function(e) {
        const urlParams = new URLSearchParams(window.location.search);
        const pathSegments = window.location.pathname.split('/');
        const categoryFromPath = pathSegments[pathSegments.indexOf('holidays') + 1];
        
        if (categoryFromPath && categoryFromPath !== 'holidays' && !this.querySelector('input[name="category"]')) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'category';
            input.value = categoryFromPath;
            this.appendChild(input);
        }
    });

    // ========== РЕГИСТРАЦИЯ НА ТРЕНИРОВКУ ==========
    const trainingForm = document.getElementById('training-registration-form');
    if (trainingForm) {
        trainingForm.addEventListener('submit', function(e) {
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
    }
});

