window.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("sidebar-toggle");
  const body = document.body;
  if (!toggle) return;
  const key = "bloom-pro-sidebar";
  if (localStorage.getItem(key) === "1") {
    body.classList.add("pro-sidebar-collapsed");
  }
  toggle.addEventListener("click", () => {
    body.classList.toggle("pro-sidebar-collapsed");
    localStorage.setItem(key, body.classList.contains("pro-sidebar-collapsed") ? "1" : "0");
  });
});
