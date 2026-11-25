(function () {
  const toast = document.getElementById("toastNotification");

  window.showToast = function (message, kind = "success") {
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${kind}`;
    window.clearTimeout(window.__toastTimer);
    window.__toastTimer = window.setTimeout(() => toast.classList.add("hidden"), 3200);
  };

  window.apiRequest = async function (url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Não foi possível concluir a operação.");
    return data;
  };

  async function hydrateSession() {
    try {
      const data = await window.apiRequest("/api/auth/me");
      window.currentAcademyUser = data.user;
      const sessionLabel = document.getElementById("sessionLabel");
      if (sessionLabel && data.user) sessionLabel.textContent = data.user.name.split(" ")[0];
      document.querySelectorAll('[data-stat="xp"]').forEach((element) => { element.textContent = data.stats?.xp ?? 0; });
      document.querySelectorAll('[data-stat="streak"]').forEach((element) => { element.textContent = data.stats?.streak ?? 0; });
      document.dispatchEvent(new CustomEvent("academy:session", { detail: data }));
    } catch (_) {
      window.currentAcademyUser = null;
    }
  }

  hydrateSession();

  document.addEventListener("click", async (event) => {
    const logout = event.target.closest("#logoutButton");
    if (!logout) return;
    logout.disabled = true;
    try {
      await window.apiRequest("/api/auth/logout", { method: "POST" });
      window.location.href = "/";
    } catch (error) {
      logout.disabled = false;
      window.showToast(error.message, "error");
    }
  });
})();
