document.addEventListener('DOMContentLoaded', () => {
    // Star rating interaction
    document.querySelectorAll('.star').forEach(star => {
        star.addEventListener('click', function() {
            const container = this.closest('.star-rating');
            const value = this.dataset.value;
            container.querySelectorAll('.star').forEach((s, index) => {
                s.classList.toggle('active', index < value);
            });
            container.querySelector('#ratingValue').value = value;
        });
    });
});