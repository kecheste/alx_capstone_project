const open = document.querySelector(".open-close");
const form = document.querySelector(".edit-profile-form");
const editButton = document.querySelector(".edit-profile");

open.addEventListener("click", function (e) {
  e.preventDefault();
  form.classList.remove("show");
});

editButton.addEventListener("click", function (e) {
  e.preventDefault();
  form.classList.add("show");
});
