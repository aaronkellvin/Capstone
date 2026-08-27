(() => {
  const cards = Array.from(document.querySelectorAll(".take-card"));
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const submitBtn = document.getElementById("submit-btn");
  const progressText = document.getElementById("progress-text");
  const progressBar = document.getElementById("progress-bar");
  const form = document.getElementById("practice-take-form");
  if (!cards.length || !form) return;

  let index = 0;
  let dirty = false;
  const draftKey =
    form.getAttribute("data-draft-key") ||
    `bloom-take:${form.getAttribute("action") || location.pathname}`;

  const overlay = (message) => {
    let node = document.getElementById("qol-overlay");
    if (!node) {
      node = document.createElement("div");
      node.id = "qol-overlay";
      node.className = "qol-overlay";
      node.innerHTML = `<div class="qol-overlay-card" role="status" aria-live="assertive"><span class="qol-spinner" aria-hidden="true"></span><p></p></div>`;
      document.body.appendChild(node);
    }
    node.querySelector("p").textContent = message;
    node.hidden = false;
  };

  const answered = (card) => {
    const checked = card.querySelector("input[type=radio]:checked");
    const textarea = card.querySelector("textarea");
    if (card.querySelector("input[type=radio]")) return Boolean(checked);
    if (textarea) return textarea.value.trim().length > 0;
    return true;
  };

  const unansweredCount = () => cards.filter((card) => !answered(card)).length;

  const collectDraft = () => {
    const values = {};
    form.querySelectorAll("input[type=radio]:checked, textarea").forEach((field) => {
      if (!field.name) return;
      values[field.name] = field.value;
    });
    return values;
  };

  const saveDraft = () => {
    try {
      localStorage.setItem(draftKey, JSON.stringify({ savedAt: Date.now(), values: collectDraft() }));
    } catch (_error) {
      /* ignore quota / private mode */
    }
  };

  const restoreDraft = () => {
    try {
      const raw = localStorage.getItem(draftKey);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      const values = parsed?.values || {};
      Object.entries(values).forEach(([name, value]) => {
        const radios = form.querySelectorAll(`input[type=radio][name="${CSS.escape(name)}"]`);
        if (radios.length) {
          radios.forEach((radio) => {
            radio.checked = radio.value === value;
          });
          return;
        }
        const area = form.querySelector(`textarea[name="${CSS.escape(name)}"]`);
        if (area) area.value = value;
      });
    } catch (_error) {
      /* ignore */
    }
  };

  const clearDraft = () => {
    try {
      localStorage.removeItem(draftKey);
    } catch (_error) {
      /* ignore */
    }
  };

  const progressTrack = document.querySelector(".take-progress");

  const show = (nextIndex) => {
    cards[index].hidden = true;
    cards[index].classList.remove("is-active");
    index = nextIndex;
    cards[index].hidden = false;
    cards[index].classList.add("is-active");

    progressText.textContent = String(index + 1);
    progressBar.style.width = `${((index + 1) / cards.length) * 100}%`;
    if (progressTrack) progressTrack.setAttribute("aria-valuenow", String(index + 1));

    prevBtn.disabled = index === 0;
    const last = index === cards.length - 1;
    nextBtn.hidden = last;
    submitBtn.hidden = !last;
  };

  restoreDraft();

  form.addEventListener("input", () => {
    dirty = true;
    saveDraft();
  });
  form.addEventListener("change", () => {
    dirty = true;
    saveDraft();
  });

  window.addEventListener("beforeunload", (event) => {
    if (dirty) event.preventDefault();
  });

  prevBtn.addEventListener("click", () => {
    if (index > 0) show(index - 1);
  });

  nextBtn.addEventListener("click", () => {
    if (!answered(cards[index])) {
      const skip = window.confirm("This question is still empty. Skip it for now?");
      if (!skip) return;
    }
    if (index < cards.length - 1) show(index + 1);
  });

  form.addEventListener("submit", (event) => {
    const missing = unansweredCount();
    if (missing) {
      const go = window.confirm(
        missing === 1
          ? "1 question is still empty. Submit anyway?"
          : `${missing} questions are still empty. Submit anyway?`
      );
      if (!go) {
        event.preventDefault();
        event.stopImmediatePropagation();
        return;
      }
    }
    const warning = form.getAttribute("data-confirm-submit");
    if (warning && !window.confirm(warning)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }
    dirty = false;
    clearDraft();
    submitBtn.disabled = true;
    overlay(form.getAttribute("data-loading") || "Submitting…");
  });
})();
