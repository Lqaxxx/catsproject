document.addEventListener('DOMContentLoaded', () => {
    const catImageDiv = document.getElementById('cat-image');
    const addToFavoritesBtn = document.getElementById('add-to-favorites');
    let currentCatUrl = '';

    
    document.getElementById('random-cat').addEventListener('click', async () => {
        const response = await fetch('/random_cat');
        const data = await response.json();
        if (data.error) {
            catImageDiv.innerHTML = `<p>${data.error}</p>`;
        } else {
            currentCatUrl = data;
            catImageDiv.innerHTML = `<img src="${data}" alt="Random Cat" class="cat-image">`;
        }
    });

    
    addToFavoritesBtn.addEventListener('click', async () => {
        if (currentCatUrl) {
            const response = await fetch('/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cat_url: currentCatUrl })
            });
            if (response.ok) {
                alert('Добавлено в избранное!');
            }
        }
    });
});
