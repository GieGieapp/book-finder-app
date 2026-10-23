/**
 * main.js - Client-Side Logic for Book Finder & Wishlist App
 */

// State Management
const state = {
    currentTab: 'search',
    lastSearchKeyword: '',
    searchResults: [],
    wishlistMap: new Map() // bookId -> bookObject
};

// DOM Elements
const dom = {
    tabSearch: document.getElementById('tab-search'),
    tabWishlist: document.getElementById('tab-wishlist'),
    viewSearch: document.getElementById('view-search'),
    viewWishlist: document.getElementById('view-wishlist'),
    wishlistCounter: document.getElementById('wishlist-counter'),
    
    // Search View Elements
    searchForm: document.getElementById('search-form'),
    searchInput: document.getElementById('search-input'),
    btnSearchSubmit: document.getElementById('btn-search-submit'),
    searchResultHeader: document.getElementById('search-result-header'),
    searchResultTitle: document.getElementById('search-result-title'),
    searchResultCount: document.getElementById('search-result-count'),
    searchLoading: document.getElementById('search-loading'),
    searchEmptyState: document.getElementById('search-empty-state'),
    searchBooksGrid: document.getElementById('search-books-grid'),
    
    // Wishlist View Elements
    btnRefreshWishlist: document.getElementById('btn-refresh-wishlist'),
    wishlistLoading: document.getElementById('wishlist-loading'),
    wishlistEmptyState: document.getElementById('wishlist-empty-state'),
    wishlistBooksGrid: document.getElementById('wishlist-books-grid'),
    btnGoSearch: document.getElementById('btn-go-search'),
    
    // Toast Container
    toastContainer: document.getElementById('toast-container')
};

/**
 * HTML string sanitation utility to prevent XSS vulnerabilities
 */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Displays floating toast notifications
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-msg toast-${type}`;
    
    let iconClass = 'fa-solid fa-circle-info';
    if (type === 'success') iconClass = 'fa-solid fa-circle-check';
    if (type === 'error') iconClass = 'fa-solid fa-circle-exclamation';

    toast.innerHTML = `
        <i class="${iconClass}"></i>
        <span>${escapeHtml(message)}</span>
    `;

    dom.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(15px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/**
 * Tab Navigation Handler
 */
function switchTab(target) {
    if (target === 'search') {
        state.currentTab = 'search';
        dom.tabSearch.classList.add('is-active');
        dom.tabSearch.setAttribute('aria-selected', 'true');
        dom.tabWishlist.classList.remove('is-active');
        dom.tabWishlist.setAttribute('aria-selected', 'false');

        dom.viewSearch.classList.remove('is-hidden');
        dom.viewWishlist.classList.add('is-hidden');
    } else {
        state.currentTab = 'wishlist';
        dom.tabWishlist.classList.add('is-active');
        dom.tabWishlist.setAttribute('aria-selected', 'true');
        dom.tabSearch.classList.remove('is-active');
        dom.tabSearch.setAttribute('aria-selected', 'false');

        dom.viewWishlist.classList.remove('is-hidden');
        dom.viewSearch.classList.add('is-hidden');

        fetchWishlist();
    }
}

/**
 * Fetches wishlist items from the backend API
 */
async function fetchWishlist(showLoader = true) {
    if (showLoader) {
        dom.wishlistLoading.classList.remove('is-hidden');
        dom.wishlistEmptyState.classList.add('is-hidden');
        dom.wishlistBooksGrid.innerHTML = '';
    }

    try {
        const response = await fetch('/api/wishlist');
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const data = await response.json();

        state.wishlistMap.clear();
        data.forEach(book => {
            state.wishlistMap.set(book.id, book);
        });

        // Update badge counter
        dom.wishlistCounter.textContent = state.wishlistMap.size;

        // Render if currently on wishlist tab
        if (state.currentTab === 'wishlist') {
            renderWishlistGrid(data);
        } else {
            // Update button states on search view
            updateSearchButtonsState();
        }
    } catch (err) {
        console.error('Failed to retrieve wishlist:', err);
        showToast('Failed to load wishlist from database.', 'error');
    } finally {
        dom.wishlistLoading.classList.add('is-hidden');
    }
}

/**
 * Renders book cards on the Wishlist tab grid
 */
function renderWishlistGrid(books) {
    dom.wishlistBooksGrid.innerHTML = '';

    if (!books || books.length === 0) {
        dom.wishlistEmptyState.classList.remove('is-hidden');
        return;
    }

    dom.wishlistEmptyState.classList.add('is-hidden');

    books.forEach(book => {
        const col = document.createElement('div');
        col.className = 'column is-12-mobile is-6-tablet is-4-desktop';
        col.innerHTML = createBookCardHTML(book, 'wishlist');
        dom.wishlistBooksGrid.appendChild(col);
    });

    initStarRatings(dom.wishlistBooksGrid);
}

/**
 * Book search orchestration via backend API
 */
async function handleSearch(keyword) {
    if (!keyword || !keyword.trim()) {
        showToast('Please enter a search keyword first.', 'error');
        dom.searchInput.focus();
        return;
    }

    const cleanKeyword = keyword.trim();
    state.lastSearchKeyword = cleanKeyword;

    // UI Updates
    dom.btnSearchSubmit.classList.add('is-loading');
    dom.searchLoading.classList.remove('is-hidden');
    dom.searchEmptyState.classList.add('is-hidden');
    dom.searchResultHeader.classList.add('is-hidden');
    dom.searchBooksGrid.innerHTML = '';

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(cleanKeyword)}`);
        if (!response.ok) {
            throw new Error(`Book search failed with status: ${response.status}`);
        }
        const books = await response.json();
        state.searchResults = books;

        renderSearchResults(books);
    } catch (err) {
        console.error('Error during book search:', err);
        showToast('Error searching for books. Please check network connection.', 'error');
        dom.searchEmptyState.classList.remove('is-hidden');
    } finally {
        dom.btnSearchSubmit.classList.remove('is-loading');
        dom.searchLoading.classList.add('is-hidden');
    }
}

/**
 * Renders search results on the Search tab grid
 */
function renderSearchResults(books) {
    dom.searchBooksGrid.innerHTML = '';

    if (!books || books.length === 0) {
        dom.searchResultHeader.classList.remove('is-hidden');
        dom.searchResultTitle.textContent = `Search: "${state.lastSearchKeyword}"`;
        dom.searchResultCount.textContent = '0 books';

        dom.searchBooksGrid.innerHTML = `
            <div class="column is-12">
                <div class="status-box">
                    <div class="status-icon"><i class="fa-solid fa-face-meh"></i></div>
                    <h3 class="status-title">No books found</h3>
                    <p class="status-text">Try using more generic keywords or verify book title spelling.</p>
                </div>
            </div>
        `;
        return;
    }

    dom.searchResultHeader.classList.remove('is-hidden');
    dom.searchResultTitle.textContent = `Results for "${state.lastSearchKeyword}"`;
    dom.searchResultCount.textContent = `${books.length} books found`;

    books.forEach(book => {
        const col = document.createElement('div');
        col.className = 'column is-12-mobile is-6-tablet is-4-desktop';
        col.innerHTML = createBookCardHTML(book, 'search');
        dom.searchBooksGrid.appendChild(col);
    });

    initStarRatings(dom.searchBooksGrid);
}

/**
 * HTML Card Component Template for Books
 */
function createBookCardHTML(book, viewType) {
    const authors = Array.isArray(book.authors) ? book.authors.join(', ') : (book.authors || 'Unknown Author');
    const isInWishlist = state.wishlistMap.has(book.id);
    const ratingValue = parseFloat(book.rating) || 0;
    const thumbnail = book.thumbnail || 'https://via.placeholder.com/128x192?text=No+Cover';
    const description = book.description || 'No summary description available for this book.';

    let actionButtonHTML = '';
    if (viewType === 'wishlist') {
        actionButtonHTML = `
            <button 
                class="button is-small btn-action-primary btn-remove" 
                onclick="removeFromWishlist('${escapeHtml(book.id)}')"
                title="Remove book from wishlist"
            >
                <i class="fa-solid fa-trash-can mr-1"></i> Remove
            </button>
        `;
    } else {
        if (isInWishlist) {
            actionButtonHTML = `
                <button 
                    class="button is-small btn-action-primary btn-in-wishlist" 
                    id="btn-wishlist-${escapeHtml(book.id)}"
                    disabled
                >
                    <i class="fa-solid fa-check mr-1"></i> In Wishlist
                </button>
            `;
        } else {
            // Encode book data safely into attribute
            const bookJsonStr = escapeHtml(JSON.stringify(book));
            actionButtonHTML = `
                <button 
                    class="button is-small is-primary is-outlined btn-action-primary" 
                    id="btn-wishlist-${escapeHtml(book.id)}"
                    data-book="${bookJsonStr}"
                    onclick="addToWishlist(this)"
                >
                    <i class="fa-regular fa-heart mr-1"></i> Wishlist
                </button>
            `;
        }
    }

    const infoLinkBtn = book.info_link ? `
        <a href="${escapeHtml(book.info_link)}" target="_blank" rel="noopener noreferrer" class="button is-small is-light" title="View details">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
        </a>
    ` : '';

    return `
        <div class="book-card" data-book-id="${escapeHtml(book.id)}">
            <div class="book-cover-container">
                <img 
                    class="book-cover-img" 
                    src="${escapeHtml(thumbnail)}" 
                    alt="${escapeHtml(book.title)}"
                    loading="lazy"
                    onerror="this.onerror=null;this.src='https://via.placeholder.com/128x192?text=No+Cover';"
                >
            </div>
            <div class="book-body">
                <h3 class="book-title" title="${escapeHtml(book.title)}">${escapeHtml(book.title)}</h3>
                <p class="book-author" title="${escapeHtml(authors)}">
                    <i class="fa-solid fa-user-pen mr-1"></i>${escapeHtml(authors)}
                </p>
                
                <div class="rating-wrapper">
                    <div class="star-rating" data-rating="${ratingValue}"></div>
                    <span class="rating-number">${ratingValue.toFixed(1)}</span>
                </div>

                <p class="book-desc" title="${escapeHtml(description)}">
                    ${escapeHtml(description)}
                </p>

                <div class="book-footer-actions">
                    ${actionButtonHTML}
                    ${infoLinkBtn}
                </div>
            </div>
        </div>
    `;
}

/**
 * Initializes rater-js star rating plugin on elements
 */
function initStarRatings(container) {
    if (typeof raterJs !== 'function') {
        console.warn('raterJs plugin not loaded.');
        return;
    }

    const ratingElements = container.querySelectorAll('.star-rating');
    ratingElements.forEach(el => {
        // Prevent double initialization
        if (el.dataset.initialized === 'true') return;

        const ratingVal = parseFloat(el.getAttribute('data-rating')) || 0;
        try {
            raterJs({
                element: el,
                rating: ratingVal,
                readOnly: true,
                starSize: 18
            });
            el.dataset.initialized = 'true';
        } catch (e) {
            console.error('Failed to initialize raterJs:', e);
        }
    });
}

/**
 * Synchronizes wishlist button states across search results grid
 */
function updateSearchButtonsState() {
    const buttons = dom.searchBooksGrid.querySelectorAll('[id^="btn-wishlist-"]');
    buttons.forEach(btn => {
        const bookId = btn.id.replace('btn-wishlist-', '');
        if (state.wishlistMap.has(bookId)) {
            btn.className = 'button is-small btn-action-primary btn-in-wishlist';
            btn.innerHTML = '<i class="fa-solid fa-check mr-1"></i> In Wishlist';
            btn.disabled = true;
            btn.removeAttribute('onclick');
        }
    });
}

/**
 * Adds book to wishlist via POST /api/wishlist
 */
async function addToWishlist(buttonElement) {
    const bookDataRaw = buttonElement.getAttribute('data-book');
    if (!bookDataRaw) return;

    let bookData;
    try {
        bookData = JSON.parse(bookDataRaw);
    } catch (e) {
        console.error('Error parsing book payload:', e);
        return;
    }

    // Set button loading indicator
    buttonElement.classList.add('is-loading');

    try {
        const response = await fetch('/api/wishlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookData)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(`"${bookData.title}" added to wishlist!`, 'success');
            state.wishlistMap.set(bookData.id, bookData);
            dom.wishlistCounter.textContent = state.wishlistMap.size;

            // Update button visual state
            buttonElement.className = 'button is-small btn-action-primary btn-in-wishlist';
            buttonElement.innerHTML = '<i class="fa-solid fa-check mr-1"></i> In Wishlist';
            buttonElement.disabled = true;
            buttonElement.removeAttribute('onclick');
        } else {
            showToast(result.error || 'Failed to add book to wishlist.', 'error');
        }
    } catch (err) {
        console.error('Error adding to wishlist:', err);
        showToast('Server connection failed while adding to wishlist.', 'error');
    } finally {
        buttonElement.classList.remove('is-loading');
    }
}

/**
 * Removes book from wishlist via DELETE /api/wishlist/<id>
 */
async function removeFromWishlist(bookId) {
    if (!confirm('Are you sure you want to remove this book from your wishlist?')) {
        return;
    }

    try {
        const response = await fetch(`/api/wishlist/${encodeURIComponent(bookId)}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            const removedBook = state.wishlistMap.get(bookId);
            const bookTitle = removedBook ? removedBook.title : 'Book';
            showToast(`"${bookTitle}" removed from wishlist.`, 'info');

            state.wishlistMap.delete(bookId);
            dom.wishlistCounter.textContent = state.wishlistMap.size;

            // Re-render wishlist grid
            renderWishlistGrid(Array.from(state.wishlistMap.values()));
        } else {
            showToast(result.error || 'Failed to remove book.', 'error');
        }
    } catch (err) {
        console.error('Error removing from wishlist:', err);
        showToast('An error occurred while removing from server.', 'error');
    }
}

// Global scope binding for inline event listeners
window.removeFromWishlist = removeFromWishlist;
window.addToWishlist = addToWishlist;

/**
 * Event Listeners Initialization
 */
document.addEventListener('DOMContentLoaded', () => {
    // Tab Clicks
    dom.tabSearch.addEventListener('click', () => switchTab('search'));
    dom.tabWishlist.addEventListener('click', () => switchTab('wishlist'));
    dom.btnGoSearch.addEventListener('click', () => {
        switchTab('search');
        dom.searchInput.focus();
    });

    // Refresh Wishlist Button
    dom.btnRefreshWishlist.addEventListener('click', () => {
        fetchWishlist(true);
        showToast('Wishlist refreshed.', 'info');
    });

    // Search Form Submit
    dom.searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSearch(dom.searchInput.value);
    });

    // Initial load: retrieve initial wishlist counter
    fetchWishlist(false);
});
