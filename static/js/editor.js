// Initialize Quill rich text editors
document.addEventListener("DOMContentLoaded", function () {
  // Configuration for Quill toolbar
  const toolbarOptions = [
    [{ header: [1, 2, 3, false] }],
    ["bold", "italic", "underline"],
    [{ list: "ordered" }, { list: "bullet" }],
    ["code-block", "link"],
    ["clean"],
  ];

  // Initialize description editor
  const descriptionEditor = document.getElementById("description-editor");
  if (descriptionEditor) {
    const quillDescription = new Quill("#description-editor", {
      theme: "snow",
      modules: {
        toolbar: toolbarOptions,
      },
      placeholder: "Explanation, flags, or usage notes",
    });

    // Sync Quill content to hidden input before form submission
    const descriptionInput = document.getElementById("description-input");
    if (descriptionInput) {
      // Set initial content if editing (wait a bit for Quill to be ready)
      setTimeout(() => {
        if (descriptionInput.value) {
          quillDescription.root.innerHTML = descriptionInput.value;
        }
      }, 100);

      // Update hidden input on text change
      quillDescription.on("text-change", function () {
        descriptionInput.value = quillDescription.root.innerHTML;
      });

      // Also update on form submit
      const form = descriptionInput.closest("form");
      if (form) {
        form.addEventListener("submit", function (e) {
          descriptionInput.value = quillDescription.root.innerHTML;
        });
      }
    }
  }

  // Initialize example editor
  const exampleEditor = document.getElementById("example-editor");
  if (exampleEditor) {
    const quillExample = new Quill("#example-editor", {
      theme: "snow",
      modules: {
        toolbar: toolbarOptions,
      },
      placeholder: "Example usage (optional)",
    });

    // Sync Quill content to hidden input before form submission
    const exampleInput = document.getElementById("example-input");
    if (exampleInput) {
      // Set initial content if editing (wait a bit for Quill to be ready)
      setTimeout(() => {
        if (exampleInput.value) {
          quillExample.root.innerHTML = exampleInput.value;
        }
      }, 100);

      // Update hidden input on text change
      quillExample.on("text-change", function () {
        exampleInput.value = quillExample.root.innerHTML;
      });

      // Also update on form submit
      const form = exampleInput.closest("form");
      if (form) {
        form.addEventListener("submit", function (e) {
          exampleInput.value = quillExample.root.innerHTML;
        });
      }
    }
  }
});

