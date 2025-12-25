// Copy to clipboard functionality
function copyToClipboard(text, button) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      const originalText = button.innerHTML;
      button.innerHTML = "✅ Copied!";
      button.style.background = "#10b981";

      setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = "";
      }, 2000);
    })
    .catch((err) => {
      alert("Failed to copy: " + err);
    });
}

// Search functionality
const searchInput = document.getElementById("searchInput");
const searchClear = document.getElementById("searchClear");
let currentCategory = "all";
let currentView = "grid";
let currentSort = "newest";

if (searchInput) {
  searchInput.addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase();
    filterNotes(searchTerm, currentCategory);
    updateNotesCount();
    
    // Show/hide clear button
    if (searchTerm) {
      searchClear.style.display = "block";
    } else {
      searchClear.style.display = "none";
    }
  });
}

if (searchClear) {
  searchClear.addEventListener("click", function () {
    searchInput.value = "";
    searchClear.style.display = "none";
    filterNotes("", currentCategory);
    updateNotesCount();
  });
}

// Category filter
const filterButtons = document.querySelectorAll(".filter-btn");

filterButtons.forEach((button) => {
  button.addEventListener("click", function () {
    // Remove active class from all buttons
    filterButtons.forEach((btn) => btn.classList.remove("active"));
    // Add active class to clicked button
    this.classList.add("active");

    currentCategory = this.getAttribute("data-category");
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : "";
    filterNotes(searchTerm, currentCategory);
    updateNotesCount();
  });
});

// Tag cloud click handler
document.querySelectorAll(".tag-cloud-tag").forEach((tag) => {
  tag.addEventListener("click", function () {
    const tagText = this.getAttribute("data-tag");
    if (searchInput) {
      searchInput.value = tagText;
      searchClear.style.display = "block";
      filterNotes(tagText.toLowerCase(), currentCategory);
      updateNotesCount();
    }
  });
});

// Tag click in cards
document.querySelectorAll(".tag").forEach((tag) => {
  tag.addEventListener("click", function () {
    const tagText = this.getAttribute("data-tag");
    if (searchInput) {
      searchInput.value = tagText;
      searchClear.style.display = "block";
      filterNotes(tagText.toLowerCase(), currentCategory);
      updateNotesCount();
    }
  });
});

function filterNotes(searchTerm, category) {
  const cards = document.querySelectorAll(".feature-card");

  cards.forEach((card) => {
    const text = card.textContent.toLowerCase();
    const cardCategory = card.getAttribute("data-category");
    
    // Get tags from the card
    const tagElements = card.querySelectorAll(".tag");
    const tagsText = Array.from(tagElements)
      .map((tag) => tag.textContent.toLowerCase())
      .join(" ");

    // Search in text content and tags
    const searchableText = text + " " + tagsText;
    const matchesSearch = searchTerm === "" || searchableText.includes(searchTerm);
    const matchesCategory =
      category === "all" || cardCategory === category;

    card.style.display =
      matchesSearch && matchesCategory ? "block" : "none";
  });

  // Apply sorting after filtering
  sortNotes(currentSort);
}

// Sort functionality
const sortSelect = document.getElementById("sortSelect");
if (sortSelect) {
  sortSelect.addEventListener("change", function () {
    currentSort = this.value;
    sortNotes(currentSort);
  });
}

function sortNotes(sortType) {
  const grid = document.getElementById("notesGrid");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll(".feature-card"));
  const visibleCards = cards.filter((card) => card.style.display !== "none");

  visibleCards.sort((a, b) => {
    switch (sortType) {
      case "newest":
        return parseInt(b.getAttribute("data-id") || 0) - parseInt(a.getAttribute("data-id") || 0);
      case "oldest":
        return parseInt(a.getAttribute("data-id") || 0) - parseInt(b.getAttribute("data-id") || 0);
      case "alphabetical":
        const aCommand = a.querySelector("h3")?.textContent.toLowerCase() || "";
        const bCommand = b.querySelector("h3")?.textContent.toLowerCase() || "";
        return aCommand.localeCompare(bCommand);
      case "category":
        const aCategory = a.getAttribute("data-category") || "";
        const bCategory = b.getAttribute("data-category") || "";
        return aCategory.localeCompare(bCategory);
      default:
        return 0;
    }
  });

  // Reorder cards in DOM
  visibleCards.forEach((card) => grid.appendChild(card));
}

// View toggle
const viewButtons = document.querySelectorAll(".view-btn");
const notesGrid = document.getElementById("notesGrid");

viewButtons.forEach((button) => {
  button.addEventListener("click", function () {
    viewButtons.forEach((btn) => btn.classList.remove("active"));
    this.classList.add("active");
    
    currentView = this.getAttribute("data-view");
    
    if (notesGrid) {
      if (currentView === "list") {
        notesGrid.classList.add("list-view");
      } else {
        notesGrid.classList.remove("list-view");
      }
    }
  });
});

// Update notes count
function updateNotesCount() {
  const visibleCards = document.querySelectorAll(".feature-card[style='display: block'], .feature-card:not([style*='display: none'])");
  const countElement = document.getElementById("visibleCount");
  if (countElement) {
    countElement.textContent = visibleCards.length;
  }
}

// Form collapse/expand
const formToggle = document.getElementById("formToggle");
const formContent = document.getElementById("formContent");

if (formToggle && formContent) {
  formToggle.addEventListener("click", function () {
    formContent.classList.toggle("collapsed");
    formToggle.classList.toggle("collapsed");
    
    const toggleText = formToggle.querySelector(".toggle-text");
    if (toggleText) {
      toggleText.textContent = formContent.classList.contains("collapsed") ? "Expand" : "Collapse";
    }
  });
}

// Form mode toggle (Quick Add vs Advanced)
const modeButtons = document.querySelectorAll(".mode-btn");
const quickMode = document.getElementById("quickMode");
const advancedMode = document.getElementById("advancedMode");
const commandInput = document.getElementById("commandInput");
const categorySelect = document.getElementById("categorySelect");

modeButtons.forEach((button) => {
  button.addEventListener("click", function () {
    modeButtons.forEach((btn) => btn.classList.remove("active"));
    this.classList.add("active");
    
    const mode = this.getAttribute("data-mode");
    
    if (mode === "quick") {
      quickMode.style.display = "block";
      advancedMode.style.display = "none";
      // Switch to textarea for quick mode
      const quickDesc = document.getElementById("quickDescription");
      if (quickDesc) {
        quickDesc.required = true;
      }
      const descInput = document.getElementById("description-input");
      if (descInput) {
        descInput.required = false;
      }
    } else {
      quickMode.style.display = "none";
      advancedMode.style.display = "block";
      // Switch to rich text editor for advanced mode
      const quickDesc = document.getElementById("quickDescription");
      if (quickDesc) {
        quickDesc.required = false;
      }
      const descInput = document.getElementById("description-input");
      if (descInput) {
        descInput.required = true;
      }
    }
  });
});

// Handle form submission for quick mode
const noteForm = document.getElementById("noteForm");
if (noteForm) {
  noteForm.addEventListener("submit", function (e) {
    const activeMode = document.querySelector(".mode-btn.active")?.getAttribute("data-mode");
    
    if (activeMode === "quick") {
      const quickDesc = document.getElementById("quickDescription");
      if (quickDesc && quickDesc.value.trim()) {
        // Convert plain text to HTML for consistency
        const htmlDesc = quickDesc.value.replace(/\n/g, "<br>");
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "description";
        hiddenInput.value = htmlDesc;
        noteForm.appendChild(hiddenInput);
      }
    }
  });
}

// FAB (Floating Action Button)
const fab = document.getElementById("fabAdd");
const fabMenu = document.getElementById("fabMenu");

if (fab && fabMenu) {
  fab.addEventListener("click", function () {
    fab.classList.toggle("active");
    fabMenu.classList.toggle("active");
  });

  // Close FAB menu when clicking outside
  document.addEventListener("click", function (e) {
    if (!fab.contains(e.target) && !fabMenu.contains(e.target)) {
      fab.classList.remove("active");
      fabMenu.classList.remove("active");
    }
  });

  // FAB menu items
  document.querySelectorAll(".fab-item").forEach((item) => {
    item.addEventListener("click", function () {
      const action = this.getAttribute("data-action");
      
      if (action === "quick-add") {
        // Scroll to form and set quick mode
        document.getElementById("add-note").scrollIntoView({ behavior: "smooth" });
        setTimeout(() => {
          const quickBtn = document.querySelector('.mode-btn[data-mode="quick"]');
          if (quickBtn) quickBtn.click();
        }, 500);
      } else if (action === "full-form") {
        // Scroll to form and set advanced mode
        document.getElementById("add-note").scrollIntoView({ behavior: "smooth" });
        setTimeout(() => {
          const advancedBtn = document.querySelector('.mode-btn[data-mode="advanced"]');
          if (advancedBtn) advancedBtn.click();
        }, 500);
      }
      
      fab.classList.remove("active");
      fabMenu.classList.remove("active");
    });
  });
}

// Smooth scroll to add note section
document
  .querySelector(".btn-quick-add")
  ?.addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("add-note").scrollIntoView({
      behavior: "smooth",
    });
  });

// Initialize notes count
document.addEventListener("DOMContentLoaded", function () {
  updateNotesCount();
  
  // Add data-id to cards for sorting
  const cards = document.querySelectorAll(".feature-card");
  cards.forEach((card, index) => {
    // Try to get ID from edit link if available
    const editLink = card.querySelector(".edit");
    if (editLink) {
      const href = editLink.getAttribute("href");
      const match = href.match(/\/edit\/(\d+)/);
      if (match) {
        card.setAttribute("data-id", match[1]);
      }
    }
  });
});
