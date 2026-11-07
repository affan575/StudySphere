document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".edit-toggle").forEach(button => {
    button.addEventListener("click", () => {
      const form = button.closest(".record").querySelector(".edit-form");
      form.classList.toggle("hidden");
      button.textContent = form.classList.contains("hidden") ? "✎" : "×";
    });
  });

  const search = document.getElementById("assignmentSearch");
  if (search) {
    search.addEventListener("input", () => {
      const term = search.value.trim().toLowerCase();
      document.querySelectorAll(".record").forEach(record => {
        record.style.display = record.dataset.search.includes(term) ? "" : "none";
      });
    });
  }

  document.querySelectorAll('input[type="date"]').forEach(input => {
    input.addEventListener("keydown", event => event.preventDefault());
  });
});
