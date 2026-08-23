document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("payment-form");
  const amountInput = document.getElementById("payment-amount");
  const submitButton = document.getElementById("payment-submit");
  const redirectInput = document.getElementById("redirect_to");

  if (!form || !amountInput || !submitButton) return;

  form.addEventListener("submit", (event) => {
    const amount = Number(amountInput.value);
    const selectedMethod = form.querySelector(
      'input[name="payment_method"]:checked'
    );

    if (redirectInput) {
      redirectInput.value =
        new URLSearchParams(window.location.search).get("redirect_to") ?? "";
    }

    if (!Number.isInteger(amount) || amount < 1) {
      event.preventDefault();
      amountInput.focus();
      return;
    }

    if (!selectedMethod) {
      event.preventDefault();
      form.querySelector('input[name="payment_method"]')?.focus();
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Создание платежа...";
  });
});
