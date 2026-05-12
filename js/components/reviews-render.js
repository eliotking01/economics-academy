(function () {
  function renderStars(rating) {
    var stars = '';
    for (var i = 0; i < rating; i++) {
      stars += '<span class="icon solid fa-star" aria-hidden="true"></span>';
    }
    return (
      '<div class="review-stars" aria-label="' + rating + ' out of 5 stars">' +
        stars +
      '</div>'
    );
  }

  function renderCard(review) {
    return (
      '<article class="review-card">' +
        renderStars(review.rating) +
        '<p class="review-outcome">' + review.outcome + '</p>' +
        '<blockquote class="review-quote">“' + review.quote + '”</blockquote>' +
        '<footer class="review-attribution">' +
          '<strong class="review-name">' + review.name + '</strong>' +
          '<span class="review-role">' + review.role + '</span>' +
        '</footer>' +
      '</article>'
    );
  }

  function renderReviews() {
    var container = document.getElementById('reviews-grid');
    if (!container || typeof reviews === 'undefined') return;
    container.innerHTML = reviews.map(renderCard).join('');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderReviews);
  } else {
    renderReviews();
  }
})();
