(() => {
  const steppers = document.querySelectorAll("[data-count-stepper]");
  if (!steppers.length) return;

  const clamp = (value, min, max) => {
    const n = Number.parseInt(String(value), 10);
    if (!Number.isFinite(n)) return min;
    return Math.min(max, Math.max(min, n));
  };

  steppers.forEach((root) => {
    const input = root.querySelector(".count-stepper-input");
    if (!(input instanceof HTMLInputElement)) return;

    const min = Number.parseInt(root.getAttribute("data-min") || input.min || "1", 10) || 1;
    const max = Number.parseInt(root.getAttribute("data-max") || input.max || "15", 10) || 15;

    const setValue = (next) => {
      input.value = String(clamp(next, min, max));
    };

    setValue(input.value);

    root.querySelectorAll("[data-count-step]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const delta = Number.parseInt(btn.getAttribute("data-count-step") || "0", 10) || 0;
        setValue((Number.parseInt(input.value, 10) || min) + delta);
        input.focus({ preventScroll: true });
      });
    });

    input.addEventListener("blur", () => setValue(input.value));
    input.addEventListener("change", () => setValue(input.value));
  });
})();
