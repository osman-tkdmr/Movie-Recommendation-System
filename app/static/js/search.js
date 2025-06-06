let currentPage = 1;

function searchMovies(page = 1) {
    const searchQuery = document.querySelector('.search-input').value;
    const genreFilter = document.getElementById('genre-filter').value;
    const yearFilter = document.getElementById('year-filter').value;
    const ratingFilter = document.getElementById('rating-filter').value;
    
    // Determine search type based on filters
    let searchType = 'title';
    if (genreFilter) {
        searchType = 'genre';
    }

    if (searchQuery.length < 3 && !genreFilter && !yearFilter && !ratingFilter) {
        alert('Please enter at least 3 characters or select a filter.');
        return;
    }

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            search_query: searchQuery, 
            search_type: searchType, 
            page: page,
            genre: genreFilter,
            year: yearFilter,
            rating: ratingFilter
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            displaySearchResults(data.paths, data.total_results, data.page, data.per_page);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displaySearchResults(results, totalResults, page, perPage) {
    const searchResultsContainer = document.getElementById('search-results');
    searchResultsContainer.innerHTML = '';

    if (results.length === 0) {
        searchResultsContainer.innerHTML = '<p>No results found. Try different search criteria.</p>';
        openModal('search-results-modal');
        return;
    }

    results.forEach(result => {
        const movieCard = document.createElement('div');
        movieCard.classList.add('slim-movie-card');
        movieCard.onclick = () => window.location.href = `/movie/${result.id}`;

        const movieImage = document.createElement('img');
        movieImage.src = `https://image.tmdb.org/t/p/w220_and_h330_face${result.poster_path}`;
        movieImage.alt = result.title;
        movieImage.classList.add('slim-movie-image');

        const movieInfo = document.createElement('div');
        movieInfo.classList.add('slim-movie-info');

        const movieTitle = document.createElement('h3');
        movieTitle.textContent = result.title;

        const movieReleaseDate = document.createElement('p');
        movieReleaseDate.textContent = `Release Date: ${result.release_date}`;

        const movieRating = document.createElement('p');
        movieRating.textContent = `Rating: ${result.vote_average}`;

        movieInfo.appendChild(movieTitle);
        movieInfo.appendChild(movieReleaseDate);
        movieInfo.appendChild(movieRating);
        movieCard.appendChild(movieImage);
        movieCard.appendChild(movieInfo);
        searchResultsContainer.appendChild(movieCard);
    });

    const paginationContainer = document.createElement('div');
    paginationContainer.classList.add('pagination-container');

    const totalPages = Math.ceil(totalResults / perPage);

    if (page > 1) {
        const prevButton = document.createElement('button');
        prevButton.textContent = 'Previous';
        prevButton.onclick = () => searchMovies(page - 1);
        paginationContainer.appendChild(prevButton);
    }

    if (page < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.textContent = 'Next';
        nextButton.onclick = () => searchMovies(page + 1);
        paginationContainer.appendChild(nextButton);
    }

    searchResultsContainer.appendChild(paginationContainer);

    openModal('search-results-modal');
}

function toggleClearButton() {
    const searchInput = document.querySelector('.search-input');
    const clearButton = document.querySelector('.clear-button');
    
    if (searchInput.value.length > 0) {
        clearButton.style.display = 'block';
    } else {
        clearButton.style.display = 'none';
    }
}

function clearSearch() {
    const searchInput = document.querySelector('.search-input');
    const clearButton = document.querySelector('.clear-button');
    
    searchInput.value = '';
    clearButton.style.display = 'none';
}
