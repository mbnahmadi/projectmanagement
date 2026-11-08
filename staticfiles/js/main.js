function toggleSection(section) {
    const arrow = section.querySelector(".arrow");
    const content = section.nextElementSibling;

    arrow.classList.toggle("open");
    content.classList.toggle("show");
}

//  last logini
document.addEventListener("DOMContentLoaded", function () {
  fetch("/users/last-login/")
  .then(res => res.json())
  .then(data => {
    if (data.last_login) {
      const date = new Date(data.last_login);
      const options = { 
        year: "numeric", month: "short", day: "numeric", 
        hour: "2-digit", minute: "2-digit" 
      };
      document.querySelector(".last-login-box").textContent =
        "Last login: " + date.toLocaleString(undefined, options);
    }
  });
});