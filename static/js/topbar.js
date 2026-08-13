(() => {
  const toggle = document.getElementById("notify-toggle");
  const panel = document.getElementById("notify-panel");
  if (toggle && panel) {
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
  }

  const overlay = (message) => {
    let node = document.getElementById("qol-overlay");
    if (!node) {
      node = document.createElement("div");
      node.id = "qol-overlay";
      node.className = "qol-overlay";
      node.innerHTML = `<div class="qol-overlay-card"><span class="qol-spinner" aria-hidden="true"></span><p></p></div>`;
      document.body.appendChild(node);
    }
    node.querySelector("p").textContent = message;
    node.hidden = false;
  };

  document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.closest(".password-wrap")) return;
    const wrap = document.createElement("div");
    wrap.className = "password-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "password-toggle";
    button.setAttribute("aria-label", "Show password");
    button.textContent = "Show";
    wrap.appendChild(button);
    button.addEventListener("click", () => {
      const hidden = input.type === "password";
      input.type = hidden ? "text" : "password";
      button.textContent = hidden ? "Hide" : "Show";
      button.setAttribute("aria-label", hidden ? "Hide password" : "Show password");
    });
  });

  document.querySelectorAll('input[type="file"]').forEach((input) => {
    const hint = document.createElement("p");
    hint.className = "file-chosen";
    input.insertAdjacentElement("afterend", hint);
    const update = () => {
      hint.textContent = input.files && input.files[0] ? input.files[0].name : "";
    };
    input.addEventListener("change", update);
    update();
  });

  document.querySelectorAll("[data-fill-login]").forEach((button) => {
    button.addEventListener("click", () => {
      const [email, password] = (button.getAttribute("data-fill-login") || "").split("|");
      const emailInput = document.getElementById("email");
      const passwordInput = document.getElementById("password");
      if (emailInput) emailInput.value = email || "";
      if (passwordInput) passwordInput.value = password || "";
      emailInput?.focus();
    });
  });

  document.querySelectorAll("[data-fill-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.getAttribute("data-fill-target"));
      if (target) target.value = button.getAttribute("data-fill-value") || "";
    });
  });

  const emailInput = document.getElementById("email");
  if (emailInput && emailInput.form && emailInput.form.getAttribute("action")?.includes("login")) {
    const saved = localStorage.getItem("bloom-email");
    if (saved && !emailInput.value) emailInput.value = saved;
    emailInput.form.addEventListener("submit", () => {
      localStorage.setItem("bloom-email", emailInput.value.trim());
    });
  }

  document.querySelectorAll("form").forEach((form) => {
    if (form.id === "practice-take-form") return;
    form.addEventListener("submit", (event) => {
      if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
        event.preventDefault();
        return;
      }
      const types = form.querySelectorAll('input[name="types"]');
      if (types.length && ![...types].some((box) => box.checked)) {
        event.preventDefault();
        window.alert("Choose at least one question type.");
        return;
      }
      const submit = form.querySelector('button[type="submit"]:not([hidden])');
      if (submit) submit.disabled = true;
      if (form.dataset.loading) overlay(form.dataset.loading);
    });
  });
})();
