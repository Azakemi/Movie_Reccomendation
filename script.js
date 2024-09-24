const searchBtn = document.getElementById('search-btn');
const movieTitleInput = document.getElementById('movie-title');
const searchResults = document.getElementById('search-results');
const resultsHeading = document.getElementById('results-heading');
const navBar = document.getElementById('nav-bar');
const backToSearch = document.getElementById('back-to-search');

searchBtn.addEventListener('click', async () => {
    const movieTitle = movieTitleInput.value.trim();
    if (movieTitle) {
        try {
            const recommendations = await getRecommendations(movieTitle);
            displayRecommendations(recommendations);
        } catch (error) {
            console.error(error);
            searchResults.innerHTML = '<p>Error fetching recommendations.</p>';
        }
    } else {
        searchResults.innerHTML = '<p>Please enter a movie title.</p>';
    }
});

backToSearch.addEventListener('click', () => {
    searchResults.innerHTML = '';
    resultsHeading.style.display = 'none';
    navBar.style.display = 'none'; // Hide navigation bar
    movieTitleInput.value = '';
});

async function getRecommendations(movieTitle) {
    const response = await fetch('/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: movieTitle }),
    });
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const recommendations = await response.json();
    return recommendations;
}

function displayRecommendations(recommendations) {
    searchResults.innerHTML = '';
    if (recommendations.length === 0) {
        searchResults.innerHTML = '<p>No recommendations found.</p>';
    } else {
        resultsHeading.style.display = 'block'; // Show the results heading
        navBar.style.display = 'block'; // Show the navigation bar
        const genresSet = new Set();
        const companiesSet = new Set();

        recommendations.forEach((recommendation) => {
            const genreList = JSON.parse(recommendation.genres);
            const companyList = JSON.parse(recommendation.production_companies);
            genreList.forEach(genre => genresSet.add(genre.name));
            companyList.forEach(company => companiesSet.add(company.name));
            const recommendationHTML = `
                <div class="recommendation" style="margin: 15px 0; padding: 10px; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; background: rgba(255, 255, 255, 0.1);">
                    <h2 style="font-size: 22px; color: white;">🎬 Title: ${recommendation.original_title}</h2>
                    <p style="color: white;">🎭 Genres: <strong>${Array.from(genresSet).join(', ')}</strong></p>
                    <p style="color: white;">🏢 Production Companies: <strong>${Array.from(companiesSet).join(', ')}</strong></p>
                    <p style="color: white;">🌐 Original Language: <strong>${recommendation.original_language}</strong></p>
                    <p style="color: white;">📝 Overview: <em>${recommendation.overview}</em></p>
                </div>
            `;
            searchResults.innerHTML += recommendationHTML;
        });
    }
    searchResults.style.display = 'block';
}
