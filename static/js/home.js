document.addEventListener("DOMContentLoaded", function() {
    const closeButtons = document.querySelectorAll(".close-button");
    
    closeButtons.forEach(function(button) {
      button.addEventListener("click", function() {
        const messageId = this.parentElement.dataset.id;
        const messageDiv = document.querySelector(`[data-id="${messageId}"]`);
        messageDiv.style.display = "none";
      });
    });
  });