// Carousel component with touch support
class TestimonialCarousel {
  constructor(container) {
    this.container = container;
    this.track = container.find(".carousel-track");
    this.slides = container.find(".testimonial-slide");
    this.dots = container.find(".carousel-dot");
    this.prevBtn = container.find(".carousel-arrow.prev");
    this.nextBtn = container.find(".carousel-arrow.next");
    this.currentSlide = 0;
    this.startX = 0;
    this.endX = 0;
    this.threshold = 50; // Minimum swipe distance

    this.initEvents();
    this.updateCarousel();
  }

  initEvents() {
    // Next arrow click
    this.nextBtn.click(() => this.next());

    // Prev arrow click
    this.prevBtn.click(() => this.prev());

    // Dot navigation click
    this.dots.click((e) => {
      this.currentSlide = $(e.currentTarget).data("slide");
      this.updateCarousel();
    });

    // Touch events for mobile
    this.track.on("touchstart", (e) => this.handleTouchStart(e));
    this.track.on("touchmove", (e) => this.handleTouchMove(e));
    this.track.on("touchend", () => this.handleTouchEnd());
  }

  handleTouchStart(e) {
    this.startX = e.originalEvent.touches[0].clientX;
  }

  handleTouchMove(e) {
    this.endX = e.originalEvent.touches[0].clientX;
  }

  handleTouchEnd() {
    if (this.startX - this.endX > this.threshold) {
      // Swipe left - go to next slide
      this.next();
    } else if (this.endX - this.startX > this.threshold) {
      // Swipe right - go to previous slide
      this.prev();
    }
  }

  next() {
    if (this.currentSlide < this.slides.length - 1) {
      this.currentSlide++;
      this.updateCarousel();
    } else {
      // Optional: loop back to first slide
      // this.currentSlide = 0;
      // this.updateCarousel();
    }
  }

  prev() {
    if (this.currentSlide > 0) {
      this.currentSlide--;
      this.updateCarousel();
    } else {
      // Optional: loop to last slide
      // this.currentSlide = this.slides.length - 1;
      // this.updateCarousel();
    }
  }

  updateCarousel() {
    const newPosition = -this.currentSlide * 100;
    this.track.css("transform", `translateX(${newPosition}%)`);

    // Update dot indicators
    this.dots.removeClass("active");
    this.dots.eq(this.currentSlide).addClass("active");

    // Update ARIA attributes for accessibility
    this.dots.attr("aria-selected", "false");
    this.dots.eq(this.currentSlide).attr("aria-selected", "true");
  }
}

// Initialize all carousels on the page
$(document).ready(function () {
  $(".testimonial-carousel").each(function () {
    new TestimonialCarousel($(this));
  });
});
