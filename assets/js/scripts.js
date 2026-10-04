// <!-- Script pour faire disparaître les messages après 4 secondes -->

document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.getElementById("flash-messages");
  if (flashMessages) {
    setTimeout(function () {
      flashMessages.style.opacity = "0";
      setTimeout(function () {
        flashMessages.remove();
      }, 1000);
    }, 4000);
  }
});
