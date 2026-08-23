document.addEventListener("DOMContentLoaded", function () {
    const deactivateButtons = document.querySelectorAll(".deactivate-btn");

    deactivateButtons.forEach(btn => {
        btn.addEventListener("click", function () {

            const form = btn.closest(".deactivate-form");
            if (!form) return;

            const reasonInput = form.querySelector(".deactivate_donate_reason");

            const modal = document.createElement("div");
            modal.className = "deactivate-modal-backdrop";
            modal.innerHTML = `
                <div class="deactivate-modal-window">
                    <div class="deactivate-modal-header">
                        <span class="deactivate-modal-title">Укажите причину</span>
                        <span class="deactivate-modal-close" id="modalCloseBtn">&times;</span>
                    </div>

                    <div class="deactivate-modal-body">
                        <label>
                          Причина деактивации:
                          <input id="deactivateReasonInput"
                                 type="text"
                                 placeholder="Введите причину..."
                                 class="input-reason">
                        </label>
                    </div>

                    <div class="deactivate-modal-actions">
                        <button id="cancelModalBtn" class="btn btn-outline-dark">Отмена</button>
                        <button id="continueModalBtn" class="btn-red">Подтвердить</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            const close = () => { document.body.removeChild(modal); };

            modal.querySelector("#modalCloseBtn").onclick = close;
            modal.querySelector("#cancelModalBtn").onclick = close;
            modal.addEventListener("mousedown", (e) => {
                if (e.target === modal) close();
            });
            window.addEventListener("keydown", function escFunc(e){
                if (e.key === "Escape") {
                    close();
                    window.removeEventListener("keydown", escFunc);
                }
            });

            modal.querySelector("#continueModalBtn").onclick = () => {
                const reason = document.getElementById("deactivateReasonInput").value.trim();
                reasonInput.value = reason === "" ? "No reason" : reason;

                close();
                form.submit();
            };
        });
    });
});