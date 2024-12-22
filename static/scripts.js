// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Dynamic Loading
let page = 1;
const postsContainer = document.getElementById('posts-container');
const loading = document.getElementById('loading');

window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        loadMorePosts();
    }
});

function loadMorePosts() {
    if (loading.style.display === 'block') return;
    loading.style.display = 'block';
    page += 1;
    fetch(`/home?page=${page}`)
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            if (data.posts.length === 0) {
                window.removeEventListener('scroll', loadMorePosts);
                return;
            }
            data.posts.forEach(post => {
                const postTile = document.createElement('div');
                postTile.className = 'post-tile';
                postTile.innerHTML = `
                    ${post.photo ? `<img src="data:image/jpeg;base64,${btoa(post.photo)}" alt="Post Image" class="post-image">` : ''}
                    <h3>${post.title}</h3>
                    <p>${post.date} by ${post.username}</p>
                `;
                postsContainer.appendChild(postTile);
            });
        })
        .catch(error => {
            console.error('Error loading more posts:', error);
            loading.style.display = 'none';
        });
}

// Form Validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function (e) {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        let valid = true;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('invalid');
                valid = false;
            } else {
                input.classList.remove('invalid');
            }
        });
        if (!valid) {
            e.preventDefault();
            alert('Please fill out all required fields.');
        }
    });
});

// Menu Toggle
document.querySelector('.menu-toggle').addEventListener('click', function () {
    document.querySelector('nav ul').classList.toggle('show');
});