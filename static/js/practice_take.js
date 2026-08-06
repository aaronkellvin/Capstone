(() => {
  const cards = Array.from(document.querySelectorAll(".take-card"));
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const submitBtn = document.getElementById("submit-btn");
  const progressText = document.getElementById("progress-text");
  const progressBar = document.getElementById("progress-bar");
  if (!cards.length) return;

  let index = 0;

  const show = (nextIndex) => {
    cards[index].hidden = true;
    cards[index].classList.remove("is-active");
    index = nextIndex;
    cards[index].hidden = false;
    cards[index].classList.add("is-active");

    progressText.textContent = String(index + 1);
    progressBar.style.width = `${((index + 1) / cards.length) * 100}%`;

    prevBtn.disabled = index === 0;
    const last = index === cards.length - 1;
    nextBtn.hidden = last;
    submitBtn.hidden = !last;
  };

  prevBtn.addEventListener("click", () => {
    if (index > 0) show(index - 1);
  });

  nextBtn.addEventListener("click", () => {
    if (index < cards.length - 1) show(index + 1);
  });
})();
