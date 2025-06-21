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

// Function to set active page in navigation
function setActivePage() {
  const path = window.location.pathname;
  const pageMap = {
    "/index.html": "home",
    "/tutoring.html": "tutoring",
    "/marking.html": "marking",
    "/revision-notes/": "revision-notes",
    "/past-papers/": "past-papers",
    "/about.html": "about",
    "/contact.html": "contact",
  };

  // Find current page
  let currentPage = "";
  for (const [pathMatch, page] of Object.entries(pageMap)) {
    if (path.includes(pathMatch)) {
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
