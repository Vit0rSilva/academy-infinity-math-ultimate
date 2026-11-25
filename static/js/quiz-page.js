(async function () {
  const page = document.querySelector(".quiz-page");
  if (!page) return;
  const slug = page.dataset.quizSlug;
  const loading = document.getElementById("quizLoading");
  const container = document.getElementById("quizQuestions");
  const form = document.getElementById("dedicatedQuizForm");
  const submit = document.getElementById("submitQuizBtn");
  const resultPanel = document.getElementById("quizResult");
  const progressBar = document.getElementById("quizProgressBar");
  let questions = [];

  try {
    const data = await window.apiRequest(`/api/quizzes/${slug}`);
    questions = data.questions;
    loading.remove();
    container.innerHTML = questions.map((question, index) => `
      <fieldset class="question-card" data-question="${index}">
        <legend><span>${String(index + 1).padStart(2, "0")}</span>${question.question}</legend>
        <div class="answer-grid">
          ${question.options.map((option, optionIndex) => `
            <label class="answer-option">
              <input type="radio" name="question-${index}" value="${optionIndex}">
              <span class="option-letter">${String.fromCharCode(65 + optionIndex)}</span>
              <span>${option}</span>
            </label>`).join("")}
        </div>
        <div class="answer-feedback" hidden></div>
      </fieldset>`).join("");
    submit.hidden = false;
    form.addEventListener("change", updateProgress);
  } catch (error) {
    loading.textContent = error.message;
  }

  function updateProgress() {
    const answered = questions.filter((_, index) => form.querySelector(`input[name="question-${index}"]:checked`)).length;
    progressBar.style.width = `${answered * 100 / questions.length}%`;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const answers = questions.map((_, index) => {
      const checked = form.querySelector(`input[name="question-${index}"]:checked`);
      return checked ? Number(checked.value) : null;
    });
    if (answers.some((answer) => answer === null)) {
      window.showToast("Responda todas as questões antes de corrigir.", "error");
      return;
    }

    submit.disabled = true;
    submit.textContent = "Corrigindo…";
    try {
      const data = await window.apiRequest(`/api/quizzes/${slug}/submit`, { method: "POST", body: JSON.stringify({ answers }) });
      data.results.forEach((item, index) => {
        const card = container.querySelector(`[data-question="${index}"]`);
        card.classList.add(item.correct ? "is-correct" : "is-wrong");
        const feedback = card.querySelector(".answer-feedback");
        feedback.hidden = false;
        feedback.innerHTML = `<strong>${item.correct ? "Resposta correta" : `Resposta correta: ${questions[index].options[item.correct_answer]}`}</strong><p>${item.explanation}</p>`;
        card.querySelectorAll("input").forEach((input) => { input.disabled = true; });
      });
      progressBar.style.width = "100%";
      resultPanel.classList.remove("hidden");
      resultPanel.classList.toggle("passed", data.passed);
      document.querySelectorAll('[data-stat="xp"]').forEach((element) => { element.textContent = data.stats.xp; });
      document.querySelectorAll('[data-stat="streak"]').forEach((element) => { element.textContent = data.stats.streak; });
      resultPanel.innerHTML = `
        <div class="result-score">${data.percentage}%</div>
        <div><span class="eyebrow">${data.passed ? "Módulo concluído" : "Continue praticando"}</span>
        <h3>${data.score} de ${data.total} respostas corretas</h3>
        <p>Resultado salvo. ${data.xp_earned > 0 ? `Você ganhou ${data.xp_earned} XP.` : "Seu melhor resultado não mudou, então não houve XP adicional."}</p></div>
        <a class="btn btn-primary" href="/painel">Ver meu progresso</a>`;
      resultPanel.scrollIntoView({ behavior: "smooth", block: "center" });
      submit.hidden = true;
    } catch (error) {
      window.showToast(error.message, "error");
      submit.disabled = false;
      submit.textContent = "Corrigir respostas";
    }
  });
})();
