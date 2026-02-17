// Becker-Posner Blog Archive - Client-side Search

let posts = [];
let currentFilter = 'all';

async function loadPosts() {
    try {
        const response = await fetch('data/posts.json');
        posts = await response.json();
        updateStats();
        renderPosts(posts);
    } catch (err) {
        console.error('Error loading posts:', err);
        document.getElementById('posts-container').innerHTML = 
            '<div class="no-results">Error loading posts. Please refresh.</div>';
    }
}

function updateStats() {
    const total = posts.length;
    const becker = posts.filter(p => p.author && p.author.toLowerCase().includes('becker')).length;
    const posner = posts.filter(p => p.author && p.author.toLowerCase().includes('posner')).length;
    
    document.getElementById('total-count').textContent = total;
    document.getElementById('becker-count').textContent = becker;
    document.getElementById('posner-count').textContent = posner;
}

function filterPosts() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    
    let filtered = posts;
    
    // Apply author filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(p => 
            p.author && p.author.toLowerCase().includes(currentFilter)
        );
    }
    
    // Apply search
    if (searchTerm) {
        filtered = filtered.filter(p => 
            p.searchText && p.searchText.includes(searchTerm)
        );
    }
    
    renderPosts(filtered);
}

function renderPosts(postsToRender) {
    const container = document.getElementById('posts-container');
    
    if (postsToRender.length === 0) {
        container.innerHTML = '<div class="no-results">No posts found matching your criteria.</div>';
        return;
    }
    
    // Group by year
    const byYear = {};
    postsToRender.forEach(post => {
        const year = post.year || 'Unknown';
        if (!byYear[year]) byYear[year] = [];
        byYear[year].push(post);
    });
    
    // Sort years descending
    const years = Object.keys(byYear).sort().reverse();
    
    let html = '';
    years.forEach(year => {
        html += `<div class="year-group">
            <h2 class="year-header">${year}</h2>
            <div class="posts-grid">`;
        
        byYear[year].forEach(post => {
            const authorClass = post.author ? 
                (post.author.toLowerCase().includes('becker') ? 'becker' : 
                 post.author.toLowerCase().includes('posner') ? 'posner' : '') : '';
            
            html += `
                <div class="post-card ${authorClass}">
                    <h2><a href="posts/${post.filename}.html">${post.title}</a></h2>
                    <div class="meta">
                        <span>${post.author || 'Unknown'}</span>
                        <span>${post.date}</span>
                    </div>
                </div>`;
        });
        
        html += '</div></div>';
    });
    
    container.innerHTML = html;
}

function setFilter(author) {
    currentFilter = author;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.author === author);
    });
    
    filterPosts();
}

// Debounce search input
let searchTimeout;
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(filterPosts, 200);
        });
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => setFilter(btn.dataset.author));
    });
    
    // Load posts
    loadPosts();
});
