(() => {
  const filterRow = document.querySelector("[data-practice-filters]");
  const grid = document.querySelector("[data-practice-grid]");
  if (!filterRow || !grid) return;

  const pills = [...filterRow.querySelectorAll("[data-subject-filter]")];
  const cards = [...grid.querySelectorAll("[data-subject]")];

  const applyFilter = (slug) => {
    pills.forEach((pill) => {
      pill.classList.toggle("active", pill.getAttribute("data-subject-filter") === slug);
      pill.classList.toggle("is-active", pill.getAttribute("data-subject-filter") === slug);
    });
    cards.forEach((card) => {
      const match = slug === "all" || card.getAttribute("data-subject") === slug;
      card.hidden = !match;
    });
  };

  filterRow.addEventListener("click", (event) => {
    const pill = event.target.closest("[data-subject-filter]");
    if (!pill || !filterRow.contains(pill)) return;
    applyFilter(pill.getAttribute("data-subject-filter") || "all");
  });
})();
