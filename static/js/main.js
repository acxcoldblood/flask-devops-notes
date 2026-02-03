// Copy to clipboard functionality
function copyToClipboard(text, button) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      const originalText = button.innerHTML;
      button.innerHTML = "✅ Copied!";
      button.classList.add("success");

      setTimeout(() => {
        button.innerHTML = originalText;
        button.classList.remove("success");
      }, 2000);
    })
    .catch((err) => {
      alert("Failed to copy: " + err);
    });
}

// Search functionality
const searchInput = document.getElementById("searchInput");
const searchClear = document.getElementById("searchClear");
const searchBtn = document.getElementById("searchBtn");

// Dark Mode Toggle Logic
function initDarkMode() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Check local storage or preference
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add('dark-mode');
    } else {
        document.documentElement.classList.remove('dark-mode');
    }
}

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark-mode');
    const theme = document.documentElement.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initDarkMode);

// Local Find Globals
let localMatches = [];
let localMatchIndex = -1;

let currentCategory = "all";
let currentView = "grid";
let currentSort = "newest";

// Keyboard Shortcuts (Cmd/Ctrl + K)
document.addEventListener('keydown', function(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    if (searchInput) {
      searchInput.focus();
    }
  }
});

if (searchInput) {
  // Auto-focus on desktop (if width > 768px)
  if (window.innerWidth > 768) {
     searchInput.focus();
  }
  
  const searchWrapper = searchInput.closest(".search-input-wrapper");
  
  // Handle Focus/Blur for visual hints
  searchInput.addEventListener('focus', () => {
    if (searchWrapper) searchWrapper.classList.add('focused');
  });
  
  searchInput.addEventListener('blur', () => {
    if (searchWrapper) searchWrapper.classList.remove('focused');
  });

  searchInput.addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase();
    
    if (document.getElementById("notesGrid")) {
        // Dashboard: Filter
        filterNotes(searchTerm, currentCategory);
        updateNotesCount();
    } else {
        // Other Pages: Local Find
        performLocalFind(this.value);
    }
    
    // Show/hide clear button and toggle wrapper class
    if (searchClear && searchWrapper) {
      if (searchTerm) {
        searchClear.style.display = "block";
        searchWrapper.classList.add("has-clear");
      } else {
        searchClear.style.display = "none";
        searchWrapper.classList.remove("has-clear");
      }
    }
  });

  // Allow Enter key to trigger search and scroll
  searchInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      
      const notesGrid = document.getElementById("notesGrid");
      
      if (notesGrid) {
          scrollToNotes();
      } else {
          // Find Next Match on page
          findNextMatch();
      }
    }
  });
}

if (searchBtn) {
  searchBtn.addEventListener("click", function () {
    scrollToNotes();
  });
}

function scrollToNotes() {
  const notesSection = document.getElementById("notes-section");
  if (notesSection) {
    // Get header height for proper offset
    const navbar = document.querySelector(".top-header");
    const navbarHeight = navbar ? navbar.offsetHeight : 100;
    
    // Calculate position with offset
    const elementPosition = notesSection.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - navbarHeight - 20;
    
    // Smooth scroll to the notes section
    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  }
}

if (searchClear) {
  const searchWrapper = searchInput ? searchInput.closest(".search-input-wrapper") : null;
  
  searchClear.addEventListener("click", function (e) {
    e.stopPropagation();
    searchInput.value = "";
    searchClear.style.display = "none";
    if (searchWrapper) {
      searchWrapper.classList.remove("has-clear");
    }
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

// Reset filters
const resetFiltersBtn = document.getElementById("resetFilters");
if (resetFiltersBtn) {
  resetFiltersBtn.addEventListener("click", function () {
    currentCategory = "all";
    filterButtons.forEach((btn) => btn.classList.remove("active"));
    const allBtn = document.querySelector('.filter-btn[data-category="all"]');
    if (allBtn) allBtn.classList.add("active");

    if (searchInput) {
      searchInput.value = "";
      const searchWrapper = searchInput.closest(".search-input-wrapper");
      if (searchWrapper) searchWrapper.classList.remove("has-clear");
    }
    if (searchClear) {
      searchClear.style.display = "none";
    }

    filterNotes("", currentCategory);
    updateNotesCount();
  });
}

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
  // Check for search param from URL (Global Search)
  const urlParams = new URLSearchParams(window.location.search);
  const searchParam = urlParams.get('search') || urlParams.get('q');
  
  if (searchParam && searchInput) {
      searchInput.value = searchParam;
      // Trigger filter if on dashboard
      if (document.getElementById("notesGrid")) {
          filterNotes(searchParam.toLowerCase(), currentCategory);
          // Show clear button
          if (searchClear) {
              searchClear.style.display = "block";
              const wrapper = searchInput.closest(".search-input-wrapper");
              if (wrapper) wrapper.classList.add("has-clear");
          }
          // Optional: Scroll to results
          setTimeout(scrollToNotes, 500);
      }
  }

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

// ==========================================
// Local "Find on Page" Logic
// ==========================================

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function clearHighlights() {
    document.querySelectorAll(".search-match").forEach(span => {
        const parent = span.parentNode;
        parent.replaceChild(document.createTextNode(span.textContent), span);
        parent.normalize();
    });
    localMatches = [];
    localMatchIndex = -1;
}

function performLocalFind(term) {
    clearHighlights();
    
    if (!term) return;
    
    const context = document.querySelector("main");
    if (!context) return; // Should allow searching outside main? Maybe. But main is content.
    
    // Create TreeWalker to find text nodes
    const walker = document.createTreeWalker(context, NodeFilter.SHOW_TEXT, {
        acceptNode: function(node) {
            // Skip if hidden
            if (node.parentElement.offsetParent === null) return NodeFilter.FILTER_REJECT;
            // Skip scripts, inputs, etc
            const tag = node.parentElement.tagName;
            if (['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT', 'SELECT'].includes(tag)) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
        }
    });

    const regex = new RegExp(escapeRegExp(term), 'gi');
    let node;
    const nodesToReplace = [];

    // Collect matching nodes first to avoid messing up walker during modification
    while(node = walker.nextNode()) {
        if (regex.test(node.nodeValue)) {
             nodesToReplace.push(node);
        }
    }
    
    // Replace text
    nodesToReplace.forEach(node => {
        const text = node.nodeValue;
        const fragment = document.createDocumentFragment();
        let lastIdx = 0;
        let match;
        
        // Reset regex state
        regex.lastIndex = 0;
        
        // Manual match loop to handle indices
        // Using string.matchAll or exec loop
        while ((match = regex.exec(text)) !== null) {
            // Text before match
            fragment.appendChild(document.createTextNode(text.substring(lastIdx, match.index)));
            
            // Match
            const span = document.createElement('span');
            span.className = 'search-match bg-yellow-400 text-black px-0.5 rounded shadow-sm';
            span.textContent = match[0];
            fragment.appendChild(span);
            localMatches.push(span);
            
            lastIdx = regex.lastIndex;
        }
        
        // Remaining text
        fragment.appendChild(document.createTextNode(text.substring(lastIdx)));
        node.replaceWith(fragment);
    });

    // Scroll to first match
    if (localMatches.length > 0) {
        localMatchIndex = 0;
        localMatches[0].scrollIntoView({behavior: 'smooth', block: 'center'});
        localMatches[0].classList.add('ring', 'ring-2', 'ring-accent-500'); // Highlight current
    }
}

function findNextMatch() {
    if (localMatches.length === 0) return;
    
    // Remove current highlight from old
    if (localMatchIndex >= 0 && localMatchIndex < localMatches.length) {
         localMatches[localMatchIndex].classList.remove('ring', 'ring-2', 'ring-accent-500');
    }
    
    localMatchIndex = (localMatchIndex + 1) % localMatches.length;
    const match = localMatches[localMatchIndex];
    
    match.scrollIntoView({behavior: 'smooth', block: 'center'});
    match.classList.add('ring', 'ring-2', 'ring-accent-500');
}
