(() => {
  const shell = document.querySelector(".chat-shell");
  const thread = document.getElementById("chat-thread");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-body");
  const status = document.getElementById("chat-status");
  if (!shell || !thread || !form || !input) return;

  const pollUrl = shell.getAttribute("data-poll-url");
  const sendUrl = shell.getAttribute("data-send-url");
  const readUrl = shell.getAttribute("data-read-url");
  const empty = document.getElementById("chat-empty");
  let pending = false;

  const csrfToken = () => document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";

  const markThreadRead = async () => {
    if (!readUrl) return;
    try {
      const payload = new FormData();
      const token = csrfToken();
      if (token) payload.set("csrf_token", token);
      await fetch(readUrl, {
        method: "POST",
        headers: {
          "X-Requested-With": "fetch",
          Accept: "application/json",
          ...(token ? { "X-CSRF-Token": token } : {}),
        },
        body: payload,
      });
    } catch (_error) {
      /* ignore — poll continues */
    }
  };

  const lastId = () => {
    const bubbles = thread.querySelectorAll(".chat-bubble[data-id]");
    if (!bubbles.length) return 0;
    return Number(bubbles[bubbles.length - 1].getAttribute("data-id") || 0);
  };

  const scrollToEnd = () => {
    thread.scrollTop = thread.scrollHeight;
  };

  const stampFor = (item) => {
    if (!item.mine) return item.created_label || "";
    const label = item.status === "read" ? "Read" : item.status === "sending" ? "Sending" : item.status === "failed" ? "Failed" : "Sent";
    return `${item.created_label || "Just now"} · ${label}`;
  };

  const addBubble = (item) => {
    if (item.id && thread.querySelector(`[data-id="${item.id}"]`)) return;
    if (empty) empty.remove();
    const article = document.createElement("article");
    article.className = `chat-bubble ${item.mine ? "is-mine" : "is-theirs"}`;
    if (item.status === "sending") article.classList.add("is-sending");
    if (item.status === "failed") article.classList.add("is-failed");
    // After initial stagger freezes, give polled/sent bubbles a single fade-in
    // instead of reusing nth-child list stagger.
    if (thread.classList.contains("is-stagger-done")) {
      article.classList.add("pro-toast-in");
    }
    if (item.id) article.dataset.id = String(item.id);
    if (item.tempId) article.dataset.tempId = item.tempId;
    article.innerHTML = `<p class="chat-text"></p><p class="chat-stamp"></p>`;
    article.querySelector(".chat-text").textContent = item.body;
    article.querySelector(".chat-stamp").textContent = stampFor(item);
    thread.appendChild(article);
    scrollToEnd();
    return article;
  };

  const setStatus = (text, isError) => {
    if (!status) return;
    const wasHidden = status.hidden;
    status.hidden = !text;
    status.textContent = text || "";
    status.classList.toggle("is-error", Boolean(isError));
    if (text && wasHidden) {
      status.classList.remove("pro-toast-in");
      void status.offsetWidth;
      status.classList.add("pro-toast-in");
    }
  };

  const addRetry = (bubble, body) => {
    if (!bubble) return;
    let retry = bubble.querySelector(".chat-retry");
    if (!retry) {
      retry = document.createElement("button");
      retry.type = "button";
      retry.className = "chat-retry";
      retry.textContent = "Retry";
      retry.addEventListener("click", () => {
        if (pending) return;
        bubble.remove();
        sendMessage(body);
      });
      bubble.appendChild(retry);
    }
  };

  const setUnreadBadge = (count) => {
    const link = document.querySelector('a[aria-label="Messages"]');
    if (!link) return;
    let dot = link.querySelector(".bell-dot");
    if (count > 0) {
      if (!dot) {
        dot = document.createElement("span");
        dot.className = "bell-dot";
        link.appendChild(dot);
      }
      dot.textContent = String(count);
    } else if (dot) {
      dot.remove();
    }
  };

  const markRead = (ids) => {
    (ids || []).forEach((id) => {
      const bubble = thread.querySelector(`.chat-bubble.is-mine[data-id="${id}"] .chat-stamp`);
      if (bubble && bubble.textContent.includes("Sent")) {
        bubble.textContent = bubble.textContent.replace("Sent", "Read");
      }
    });
  };

  const poll = async () => {
    try {
      const response = await fetch(`${pollUrl}?after=${lastId()}`, { headers: { Accept: "application/json" } });
      if (!response.ok) return;
      const data = await response.json();
      const incoming = (data.messages || []).filter((item) => !item.mine);
      (data.messages || []).forEach(addBubble);
      markRead(data.read_ids || []);
      if (incoming.length) markThreadRead();
      if (typeof data.unread_messages === "number") setUnreadBadge(data.unread_messages);
      if (status && status.classList.contains("is-error")) setStatus("");
    } catch (error) {
      setStatus("Could not refresh messages. Trying again…", true);
    }
  };

  const updateCharCount = () => {
    const count = document.getElementById("chat-char-count");
    if (!count || !input) return;
    const length = input.value.length;
    count.textContent = `${length} / 2000`;
    count.classList.toggle("is-near-limit", length >= 1800);
  };

  const sendMessage = async (body) => {
    if (!body || pending) return;
    const submit = form.querySelector("button[type=submit]");
    pending = true;
    if (submit) submit.disabled = true;
    const tempId = `temp-${Date.now()}`;
    const temp = addBubble({
      tempId,
      body,
      mine: true,
      status: "sending",
      created_label: "Just now",
    });
    setStatus("Sending…");
    try {
      const payload = new FormData();
      payload.set("body", body);
      const token = csrfToken();
      if (token) payload.set("csrf_token", token);
      const response = await fetch(sendUrl, {
        method: "POST",
        headers: {
          "X-Requested-With": "fetch",
          Accept: "application/json",
          ...(token ? { "X-CSRF-Token": token } : {}),
        },
        body: payload,
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error("send failed");
      if (input.value.trim() === body) input.value = "";
      updateCharCount();
      if (temp) temp.remove();
      addBubble(data.message);
      setStatus("");
    } catch (error) {
      if (temp) {
        temp.classList.add("is-failed");
        temp.classList.remove("is-sending");
        const stamp = temp.querySelector(".chat-stamp");
        if (stamp) stamp.textContent = "Just now · Failed";
        addRetry(temp, body);
      }
      setStatus("Could not send. Use Retry on the message when you’re ready.", true);
    } finally {
      pending = false;
      if (submit) submit.disabled = false;
      input.focus();
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(input.value.trim());
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  input.addEventListener("input", updateCharCount);
  updateCharCount();

  scrollToEnd();
  markThreadRead();
  // Freeze thread stagger after first paint so poll/send appends do not
  // pick up nth-child stagger delays on the whole list.
  window.setTimeout(() => {
    thread.classList.add("is-stagger-done");
  }, 650);
  window.setInterval(poll, 4000);
})();
