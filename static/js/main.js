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

function addComment(post_id) {
  const parentElement = document.querySelector("#commentsContainer");
  const commentText = document.getElementById("commentText");
  if (commentText.value == "") return;

  let commentsContain = document.createElement("div");
  commentsContain.className = "comments-contain";

  let commentImage = document.createElement("img");
  commentImage.className = "comment-image";

  let commentContent = document.createElement("div");
  commentContent.className = "comments-content";

  let commentHeader = document.createElement("div");
  commentHeader.className = "comment-header";

  let commentUsername = document.createElement("h3");
  let commentDate = document.createElement("h4");

  let commentBody = document.createElement("div");
  commentBody.className = "comment-body";

  let commentBodyContent = document.createElement("div");

  let anchor = document.createElement("a");

  let deleteImg = document.createElement("img");
  deleteImg.src = "/static/img/delete.png";

  fetch(`/post/${post_id}/addComment/${commentText.value}`, {
    method: "POST",
  })
    .then((res) => res.json())
    .then((data) => {
      anchor.href = `/post/${post_id}/comment/${data.comment_id}/delete`;
      // Appending childs to parent classes
      anchor.appendChild(deleteImg);
      commentBody.appendChild(commentBodyContent);
      commentBody.appendChild(anchor);
      commentContent.appendChild(commentHeader);
      commentContent.appendChild(commentBody);
      commentHeader.appendChild(commentUsername);
      commentHeader.appendChild(commentDate);
      commentsContain.appendChild(commentImage);
      commentsContain.appendChild(commentContent);

      // DOM manipulating to change inner contents of the html elements
      commentImage.src = `/static/img/${data.image}`;
      commentUsername.innerText = data.username;
      commentDate.innerText = data.date_created;
      commentBodyContent.innerText = data.content;
      parentElement.appendChild(commentsContain);
    });
}

function showMenu() {
  const expanded = document.querySelector(".expandable");
  expanded.style.display = "block";
}

function hideMenu() {
  const expanded = document.querySelector(".expandable");
  expanded.style.display = "none";
}
