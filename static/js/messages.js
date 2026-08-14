(() => {
  const shell = document.querySelector(".chat-shell");
  const thread = document.getElementById("chat-thread");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-body");
  const status = document.getElementById("chat-status");
  if (!shell || !thread || !form || !input) return;

  const pollUrl = shell.getAttribute("data-poll-url");
  const sendUrl = shell.getAttribute("data-send-url");
  const empty = document.getElementById("chat-empty");
  let pending = false;

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
    status.hidden = !text;
    status.textContent = text || "";
    status.classList.toggle("is-error", Boolean(isError));
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
      (data.messages || []).forEach(addBubble);
      markRead(data.read_ids || []);
      if (typeof data.unread_messages === "number") setUnreadBadge(data.unread_messages);
      if (status && status.classList.contains("is-error")) setStatus("");
    } catch (error) {
      setStatus("Could not refresh messages. Trying again…", true);
    }
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = input.value.trim();
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
      const response = await fetch(sendUrl, {
        method: "POST",
        headers: { "X-Requested-With": "fetch", Accept: "application/json" },
        body: payload,
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error("send failed");
      input.value = "";
      if (temp) temp.remove();
      addBubble(data.message);
      setStatus("");
    } catch (error) {
      if (temp) {
        temp.classList.add("is-failed");
        temp.classList.remove("is-sending");
        const stamp = temp.querySelector(".chat-stamp");
        if (stamp) stamp.textContent = "Just now · Failed";
      }
      setStatus("Could not send. Check your connection and try again.", true);
    } finally {
      pending = false;
      if (submit) submit.disabled = false;
      input.focus();
    }
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  scrollToEnd();
  window.setInterval(poll, 4000);
})();
