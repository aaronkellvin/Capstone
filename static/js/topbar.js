(() => {
  const toggle = document.getElementById("notify-toggle");
  const panel = document.getElementById("notify-panel");
  if (!toggle || !panel) return;

  const close = () => {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
  };

  const open = () => {
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
  };

  toggle.addEventListener("click", (event) => {
    event.stopPropagation();
    if (panel.hidden) open();
    else close();
  });

  document.addEventListener("click", (event) => {
    if (!panel.hidden && !panel.contains(event.target) && event.target !== toggle) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });
})();
