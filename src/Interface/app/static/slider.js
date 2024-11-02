class MovieSlider {
    constructor(options) {
        this.container = document.getElementById(options.containerId);
        if (!this.container) {
            throw new Error(`Container with id ${options.containerId} not found`);
        }
        
        // Clear any existing content
        this.container.innerHTML = '';
        
        this.slider = document.createElement('div');
        this.slider.className = 'slides';
        this.container.appendChild(this.slider);
        
        this.prevBtn = document.createElement('button');
        this.prevBtn.className = 'slider-btn prev';
        this.prevBtn.innerHTML = '<span class="material-icons">arrow_back</span>';
        this.container.appendChild(this.prevBtn);
        
        this.nextBtn = document.createElement('button');
        this.nextBtn.className = 'slider-btn next';
        this.nextBtn.innerHTML = '<span class="material-icons">arrow_forward</span>';
        this.container.appendChild(this.nextBtn);
        
        this.dotsContainer = document.createElement('div');
        this.dotsContainer.className = 'dots';
        this.container.appendChild(this.dotsContainer);
        
        this.moviePaths = options.moviePaths;
        this.currentSlide = 0;
        this.isAnimating = false;
        
        this.init();
    }

    init() {
        this.addEventListeners();
        this.adjustSlides();
        window.addEventListener('resize', () => this.adjustSlides());
    }

    updateSlider() {
        this.slider.style.transform = `translateX(-${this.currentSlide * 100}%)`;
        this.dotsContainer.querySelectorAll('.dot').forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentSlide);
        });
        
        this.prevBtn.style.display = this.currentSlide === 0 ? 'none' : 'flex';
        this.nextBtn.style.display = this.currentSlide === this.slider.children.length - 1 ? 'none' : 'flex';
    }

    goToSlide(index) {
        if (!this.isAnimating && index !== this.currentSlide) {
            this.isAnimating = true;
            this.currentSlide = index;
            this.updateSlider();
            setTimeout(() => {
                this.isAnimating = false;
            }, 500);
        }
    }

    getItemsPerSlide() {
        const width = window.innerWidth;
        if (width < 440) return 1;
        if (width < 660) return 2;
        if (width < 880) return 3;
        if (width < 1100) return 4;
        if (width < 1300) return 5;
        return 6;
    }

    createSlideHTML(slide) {
        return `
            <div class="slide" data-index="${slide.index}">
                <div class="movie-grid">
                    ${slide.movies.map(movie => `
                        <div class="movie-card" onclick="window.location.href='/movie/${movie.id}'">
                            <img 
                                src="https://image.tmdb.org/t/p/w220_and_h330_face${movie.poster_path}"
                                alt="${movie.title} poster"
                                class="movie-image"
                                loading="lazy"
                            >
                            <div class="movie-info">
                                <h3>${movie.title}</h3>
                                <p>Rating: ${movie.vote_average}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createDotsHTML(slidesCount) {
        return Array.from({ length: slidesCount }, (_, index) => `
            <button class="dot ${index === 0 ? 'active' : ''}" 
                    data-index="${index}" 
                    aria-label="Go to slide ${index + 1}">
                <span class="material-icons">circle</span>
            </button>
        `).join('');
    }

    adjustSlides() {
        const itemsPerSlide = this.getItemsPerSlide();
        const slides = [];
        
        for (let i = 0; i < this.moviePaths.length; i += itemsPerSlide) {
            slides.push({
                index: slides.length,
                movies: this.moviePaths.slice(i, i + itemsPerSlide)
            });
        }

        this.slider.innerHTML = slides.map(slide => this.createSlideHTML(slide)).join('');
        this.dotsContainer.innerHTML = this.createDotsHTML(slides.length);
        
        this.currentSlide = 0;
        this.updateSlider();
        this.setupDotListeners();
    }

    setupDotListeners() {
        this.dotsContainer.querySelectorAll('.dot').forEach((dot, index) => {
            dot.addEventListener('click', () => this.goToSlide(index));
        });
    }

    addEventListeners() {
        this.prevBtn.addEventListener('click', () => {
            if (this.currentSlide > 0) {
                this.goToSlide(this.currentSlide - 1);
            }
        });

        this.nextBtn.addEventListener('click', () => {
            if (this.currentSlide < this.slider.children.length - 1) {
                this.goToSlide(this.currentSlide + 1);
            }
        });
    }

    destroy() {
        // Remove event listeners
        window.removeEventListener('resize', () => this.adjustSlides());
        
        // Clear container
        this.container.innerHTML = '';
    }
}

// Initialize the slider when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.sliderInstance = new MovieSlider({
        containerId: 'slider-container',
        moviePaths: moviePaths
    });
});

