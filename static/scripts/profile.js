document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab-btn").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn")
        .forEach((item) => item.classList.remove("active"));

      document.querySelectorAll(".tab-content")
        .forEach((item) => item.classList.remove("active"));

      button.classList.add("active");

      const target = document.getElementById(button.dataset.tab);
      if (target) target.classList.add("active");
    });
  });

  document.querySelectorAll(".open-modal").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      const form = button.closest("form");
      if (!form) return;

      const modal = document.createElement("div");
      modal.className = "deactivate-modal-backdrop";

      modal.innerHTML = `
        <div class="deactivate-modal-window">
          <div class="deactivate-modal-header">
            <span class="deactivate-modal-title" style="color:#1f0000">Внимание!</span>
            <button type="button" class="deactivate-modal-close btn-close"></button>
          </div>
          <div class="deactivate-modal-body" style="color:#1f0000">
            После деактивации <b style="color:#b10000">донат нельзя будет вернуть</b>.<br>
            Ты точно хочешь продолжить?
          </div>
          <div class="deactivate-modal-actions mt-3 d-flex gap-2">
            <button type="button" class="btn btn-outline-dark cancel-btn">Отмена</button>
            <button type="button" class="btn btn-danger confirm-btn">Продолжить</button>
          </div>
        </div>
      `;

      document.body.appendChild(modal);

      const close = () => {
        modal.remove();
        window.removeEventListener("keydown", onKeyDown);
      };

      const onKeyDown = (e) => {
        if (e.key === "Escape") close();
      };

      modal.querySelector(".deactivate-modal-close").addEventListener("click", close);
      modal.querySelector(".cancel-btn").addEventListener("click", close);

      modal.querySelector(".confirm-btn").addEventListener("click", () => {
        form.submit();
        close();
      });

      modal.addEventListener("mousedown", (e) => {
        if (e.target === modal) close();
      });

      window.addEventListener("keydown", onKeyDown);
    });
  });
});
