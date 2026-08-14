(() => {
  const popovers = [
    ["notify-toggle", "notify-panel"],
    ["profile-toggle", "profile-panel"],
    ["settings-toggle", "settings-panel"],
  ]
    .map(([toggleId, panelId]) => ({
      toggle: document.getElementById(toggleId),
      panel: document.getElementById(panelId),
    }))
    .filter((item) => item.toggle && item.panel);

  const closePopover = (item) => {
    item.panel.hidden = true;
    item.toggle.setAttribute("aria-expanded", "false");
  };

  const closeAll = () => popovers.forEach(closePopover);

  const openPopover = (item) => {
    closeAll();
    item.panel.hidden = false;
    item.toggle.setAttribute("aria-expanded", "true");
  };

  popovers.forEach((item) => {
    item.toggle.addEventListener("click", (event) => {
      event.stopPropagation();
      if (item.panel.hidden) openPopover(item);
      else closePopover(item);
    });
  });

  const applyAnnouncementRead = (id, unread) => {
    document.querySelectorAll(`[data-mark-announcement="${id}"]`).forEach((node) => {
      node.classList.remove("is-unread", "is-unread-card");
      const subject = node.querySelector(".notify-subject");
      if (subject) subject.textContent = subject.textContent.replace(/\s·\sNew$/, "");
      const kicker = node.querySelector(".hub-card-kicker");
      if (kicker) kicker.textContent = kicker.textContent.replace(/\s·\sUnread$/, "");
    });
    const toggle = document.getElementById("notify-toggle");
    const countEl = document.querySelector("#notify-panel .notify-count");
    if (!toggle) return;
    let dot = toggle.querySelector(".bell-dot");
    if (unread > 0) {
      if (!dot) {
        dot = document.createElement("span");
        dot.className = "bell-dot";
        toggle.appendChild(dot);
      }
      dot.textContent = String(unread);
      if (countEl) {
        countEl.classList.remove("notify-count-quiet");
        countEl.textContent = `${unread} unread`;
      }
    } else {
      if (dot) dot.remove();
      if (countEl) {
        countEl.classList.add("notify-count-quiet");
        countEl.textContent = "All caught up";
      }
    }
  };

  document.querySelectorAll("[data-mark-announcement]").forEach((link) => {
    link.addEventListener("click", async (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      const unread = link.classList.contains("is-unread") || link.classList.contains("is-unread-card");
      if (!unread && link.classList.contains("hub-card")) {
        event.preventDefault();
        return;
      }
      if (!unread) return;
      event.preventDefault();
      const id = link.getAttribute("data-mark-announcement");
      try {
        const response = await fetch(`/announcements/${id}/read`, {
          method: "POST",
          headers: { Accept: "application/json", "X-Requested-With": "fetch" },
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) throw new Error(data.error || "mark failed");
        applyAnnouncementRead(id, data.unread_announcements);
        if (link.classList.contains("hub-card")) return;
        window.location.href = link.getAttribute("href");
      } catch (error) {
        window.alert("Unable to update notification status. Please try again.");
      }
    });
  });

  const highlighted = document.querySelector(".hub-card.is-highlight");
  if (highlighted) highlighted.scrollIntoView({ block: "nearest" });

  document.addEventListener("click", (event) => {
    popovers.forEach((item) => {
      if (item.panel.hidden) return;
      if (!item.panel.contains(event.target) && !item.toggle.contains(event.target)) {
        closePopover(item);
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAll();
  });

  const prefKey = (name) => `bloom-pref-${name}`;
  const applyPref = (name, on) => {
    const root = document.documentElement;
    if (name === "large-type") root.classList.toggle("pref-large-type", on);
    if (name === "reduce-motion") root.classList.toggle("pref-reduce-motion", on);
    if (name === "notify-badge") root.classList.toggle("pref-hide-badge", !on);
  };

  document.querySelectorAll("[data-pref]").forEach((input) => {
    const name = input.getAttribute("data-pref");
    const stored = localStorage.getItem(prefKey(name));
    const on = name === "notify-badge" ? stored !== "0" : stored === "1";
    input.checked = on;
    applyPref(name, on);
    input.addEventListener("change", () => {
      localStorage.setItem(prefKey(name), input.checked ? "1" : "0");
      applyPref(name, input.checked);
    });
  });

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
    if (form.id === "practice-take-form" || form.id === "chat-form") return;
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
