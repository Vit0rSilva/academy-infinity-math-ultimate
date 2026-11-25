(function () {
  const card = document.querySelector(".auth-card");
  const form = document.getElementById("pageAuthForm");
  if (!card || !form) return;
  const tabs = document.querySelectorAll(".auth-tab");
  const nameField = document.getElementById("pageNameField");
  const title = document.getElementById("authPageTitle");
  const subtitle = document.getElementById("authPageSubtitle");
  const submit = document.getElementById("pageAuthSubmit");
  const errorBox = document.getElementById("pageAuthError");
  let mode = "login";

  function setMode(nextMode) {
    mode = nextMode;
    tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.mode === mode));
    nameField.classList.toggle("hidden", mode === "login");
    document.getElementById("pageAuthName").required = mode === "register";
    document.getElementById("pageAuthPassword").autocomplete = mode === "login" ? "current-password" : "new-password";
    title.textContent = mode === "login" ? "Boas-vindas de volta" : "Crie sua conta gratuita";
    subtitle.textContent = mode === "login" ? "Entre para continuar exatamente de onde parou." : "Você começa com 0 XP e o primeiro módulo liberado.";
    submit.textContent = mode === "login" ? "Entrar na minha conta" : "Criar conta e começar";
    errorBox.classList.add("hidden");
  }

  tabs.forEach((tab) => tab.addEventListener("click", () => setMode(tab.dataset.mode)));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.classList.add("hidden");
    submit.disabled = true;
    submit.textContent = mode === "login" ? "Entrando…" : "Criando conta…";
    const payload = {
      email: document.getElementById("pageAuthEmail").value.trim(),
      password: document.getElementById("pageAuthPassword").value,
    };
    if (mode === "register") payload.name = document.getElementById("pageAuthName").value.trim();
    try {
      await window.apiRequest(`/api/auth/${mode}`, { method: "POST", body: JSON.stringify(payload) });
      const destination = card.dataset.nextUrl.startsWith("/") ? card.dataset.nextUrl : "/painel";
      window.location.href = destination;
    } catch (error) {
      submit.disabled = false;
      setMode(mode);
      errorBox.textContent = error.message;
      errorBox.classList.remove("hidden");
    }
  });
})();
