function submitRating(movieId, rating) {
    fetch('/rate_movie', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'movie_id': movieId,
            'rating': rating
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Rating submitted successfully!');
                // Update the stars
                document.querySelectorAll('.star').forEach(star => {
                    star.classList.toggle('active', star.dataset.rating <= rating);
                });
            } else {
                alert('Error submitting rating.');
            }
        })
        .catch(error => console.error('Error:', error));
}

document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('mouseover', function() {
        const rating = this.dataset.rating;
        document.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('hover', s.dataset.rating <= rating);
        });
    });

    star.addEventListener('mouseout', function() {
        const currentRating = document.querySelector('.stars').dataset.currentRating;
        document.querySelectorAll('.star').forEach(s => {
            s.classList.remove('hover');
            s.classList.toggle('active', s.dataset.rating <= currentRating);
        });
    });

    star.addEventListener('click', function() {
        const rating = this.dataset.rating;
        submitRating(this.dataset.movieId, rating);
    });
});
