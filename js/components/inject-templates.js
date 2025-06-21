// Function to inject templates and set active page
function injectTemplates() {
  // Inject header
  fetch("/templates/header.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("header-placeholder").outerHTML = data;
      setActivePage();
    });

  // Inject footer
  fetch("/templates/footer.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("footer-placeholder").outerHTML = data;
    });
}

// Updated setActivePage function
function setActivePage() {
  const path = window.location.pathname;
  const pageMap = {
    "/revision-notes/": "revision-notes",
    "/revision-notes/index.html": "revision-notes",
    "/past-papers/": "past-papers",
    "/past-papers/index.html": "past-papers",
    "/tutoring.html": "tutoring",
    "/marking.html": "marking",
    "/about.html": "about",
    "/contact.html": "contact",
    "/index.html": "home",
    "/": "home", // Add root path
  };

  // Find current page - check for most specific matches first
  let currentPage = "";
  for (const [pathMatch, page] of Object.entries(pageMap)) {
    if (path.endsWith(pathMatch)) {
      currentPage = page;
      break;
    }
  }

  // Set active class
  if (currentPage) {
    const activeElement = document.querySelector(
      `[data-page="${currentPage}"]`
    );
    if (activeElement) {
      activeElement.classList.add("current");
    }
  }
}

// Run when DOM is loaded
document.addEventListener("DOMContentLoaded", injectTemplates);
