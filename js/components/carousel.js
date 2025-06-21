// Carousel component
class TestimonialCarousel {
  constructor(container) {
    this.container = container;
    this.track = container.find(".carousel-track");
    this.slides = container.find(".testimonial-slide");
    this.dots = container.find(".carousel-dot");
    this.currentSlide = 0;

    this.initEvents();
    this.updateCarousel();
  }

  initEvents() {
    // Next arrow click
    this.container.find(".carousel-arrow.next").click(() => this.next());

    // Prev arrow click
    this.container.find(".carousel-arrow.prev").click(() => this.prev());

    // Dot navigation click
    this.dots.click((e) => {
      this.currentSlide = $(e.currentTarget).data("slide");
      this.updateCarousel();
    });
  }

  next() {
    if (this.currentSlide < this.slides.length - 1) {
      this.currentSlide++;
      this.updateCarousel();
    }
  }

  prev() {
    if (this.currentSlide > 0) {
      this.currentSlide--;
      this.updateCarousel();
    }
  }

  updateCarousel() {
    const newPosition = -this.currentSlide * 100;
    this.track.css("transform", `translateX(${newPosition}%)`);

    // Update dot indicators
    this.dots.removeClass("active");
    this.dots.eq(this.currentSlide).addClass("active");
  }
}

// Initialize all carousels on the page
$(document).ready(function () {
  $(".testimonial-carousel").each(function () {
    new TestimonialCarousel($(this));
  });
});
