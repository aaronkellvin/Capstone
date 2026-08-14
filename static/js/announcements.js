(() => {
  const detail = document.querySelector(".announce-detail.is-arrive");
  if (!detail) return;
  const url = new URL(window.location.href);
  if (url.searchParams.has("arrive")) {
    url.searchParams.delete("arrive");
    const next = `${url.pathname}${url.search}${url.hash}`;
    window.history.replaceState({}, "", next);
  }
  const clear = () => detail.classList.remove("is-arrive");
  detail.addEventListener("animationend", clear, { once: true });
  window.setTimeout(clear, 1600);
})();
