const legacyQuizData = {
  mod1: { label: "Módulo 1 • Nível Iniciante", questions: [
    ["Se A={1,2,3} e B={3,4}, qual é A ∩ B?", ["{1,2,4}", "{3}", "{1,2,3,4}"], 1],
    ["P ∨ ¬P é uma:", ["Contradição", "Contingência", "Tautologia"], 2],
    ["O símbolo ∀ significa:", ["Existe", "Para todo", "Pertence"], 1],
  ]},
  mod2: { label: "Módulo 2 • Nível Intermediário", questions: [
    ["Dois vetores formam uma base de R² quando são:", ["Iguais", "Linearmente independentes", "Nulos"], 1],
    ["O produto interno de (1,2) e (3,4) é:", ["7", "10", "11"], 2],
    ["A norma de (3,4) é:", ["5", "7", "25"], 0],
  ]},
  mod3: { label: "Módulo 3 • Nível Avançado", questions: [
    ["Uma matriz quadrada é inversível quando:", ["det=0", "det≠0", "Todos os elementos são 1"], 1],
    ["Uma transformação é injetora se o núcleo contém:", ["Só o vetor nulo", "Todo o domínio", "A imagem"], 0],
    ["Um isomorfismo é uma transformação linear:", ["Constante", "Bijetora", "Sem imagem"], 1],
  ]},
  mod4: { label: "Módulo 4 • Nível Master", questions: [
    ["Na P.A. a₁=2, r=3, qual é a₄?", ["8", "11", "14"], 1],
    ["Uma fila M/M/1 é estável quando:", ["λ<μ", "λ=μ", "λ>μ"], 0],
    ["Se λ=6 e μ=10, ρ vale:", ["0,4", "0,6", "1,6"], 1],
  ]},
};

let authMode = "login";
let activeQuizModule = "mod1";
let activeQuestion = 0;
let quizCorrect = 0;
let logicP = true;
let logicQ = false;

function openAuthModal() { document.getElementById("authModal").classList.remove("hidden"); }
function closeAuthModal() { document.getElementById("authModal").classList.add("hidden"); }
function closeAuthModalOutside(event) { if (event.target.id === "authModal") closeAuthModal(); }

function toggleAuthMode() {
  authMode = authMode === "login" ? "register" : "login";
  document.getElementById("nameFieldGroup").classList.toggle("hidden", authMode === "login");
  document.getElementById("authSubmitBtn").textContent = authMode === "login" ? "Entrar com Login e Senha" : "Criar conta gratuita";
  document.getElementById("authSwitchText").textContent = authMode === "login" ? "Ainda não possui conta?" : "Já possui conta?";
  document.getElementById("authSwitchBtn").textContent = authMode === "login" ? "Criar conta gratuita" : "Entrar";
}

async function handleCredentialLogin(event) {
  event.preventDefault();
  const email = document.getElementById("authLoginUser").value.trim();
  const password = document.getElementById("authPass").value;
  const payload = { email, password };
  if (authMode === "register") payload.name = document.getElementById("authName").value.trim();
  try {
    const data = await window.apiRequest(`/api/auth/${authMode}`, { method: "POST", body: JSON.stringify(payload) });
    window.location.href = "/painel";
  } catch (error) { window.showToast(error.message, "error"); }
}

function applyLoggedUser(user, stats = {}) {
  if (!user) return;
  const userText = document.getElementById("navUserText");
  const authButton = document.getElementById("authTriggerBtn");
  if (userText) userText.textContent = user.name.split(" ")[0];
  if (authButton) authButton.classList.add("logged-in");
  const xp = document.getElementById("xpPoints");
  const streak = document.getElementById("streakCount");
  if (xp) xp.textContent = stats.xp ?? 0;
  if (streak) streak.textContent = stats.streak ?? 0;
  const nameInput = document.getElementById("studentNameInput");
  if (nameInput) { nameInput.value = user.name; updateCertificate(); }
}

document.addEventListener("academy:session", (event) => { if (event.detail.user) applyLoggedUser(event.detail.user, event.detail.stats); });

function socialLogin() { window.showToast("Login social exige credenciais OAuth. Use e-mail e senha nesta versão.", "error"); }
function toggleElement(id) { document.getElementById(id)?.classList.toggle("hidden"); }

function setActiveTab(containerId, filter) {
  document.querySelectorAll(`#${containerId} [data-filter]`).forEach((tab) => tab.classList.toggle("active", tab.dataset.filter === filter));
}
function filterVideos(filter, button) {
  document.querySelectorAll("#videoGridContainer [data-module]").forEach((card) => { card.style.display = filter === "all" || card.dataset.module === filter ? "flex" : "none"; });
  setActiveTab("videoFilterTabs", filter);
  if (button) button.classList.add("active");
}
function filterExercises(filter, button) {
  document.querySelectorAll("#exercisesListContainer [data-module]").forEach((card) => { card.style.display = filter === "all" || card.dataset.module === filter ? "flex" : "none"; });
  setActiveTab("exFilterTabs", filter);
  if (button) button.classList.add("active");
}
function jumpToSectionWithFilter(section, filter) {
  if (document.body.dataset.authenticated !== "true") { window.location.href = "/entrar"; return; }
  const moduleNumber = Number(filter.replace("mod", ""));
  if (moduleNumber > Number(document.body.dataset.unlockedCount)) {
    window.location.href = "/painel?locked=" + filter;
    return;
  }
  document.getElementById(section).scrollIntoView({ behavior: "smooth" });
  if (section === "videos") filterVideos(filter); else filterExercises(filter);
}
function jumpToQuizModule(module) {
  if (document.body.dataset.authenticated !== "true") { window.location.href = "/entrar"; return; }
  const slugs = { mod1: "conjuntos-logica", mod2: "espacos-euclidianos", mod3: "transformacoes-lineares", mod4: "sequencias-filas" };
  window.location.href = `/quiz/${slugs[module] || ""}`;
}

function parseSet(id) { return new Set(document.getElementById(id).value.split(",").map((item) => item.trim()).filter(Boolean)); }
function formatSet(values) { return `{ ${[...values].join(", ")} }`; }
function calculateSets() {
  const a = parseSet("setA"); const b = parseSet("setB");
  document.getElementById("resUnion").textContent = formatSet(new Set([...a, ...b]));
  document.getElementById("resIntersection").textContent = formatSet(new Set([...a].filter((value) => b.has(value))));
  document.getElementById("resDiffAB").textContent = formatSet(new Set([...a].filter((value) => !b.has(value))));
}
function toggleVal(name) {
  if (name === "P") logicP = !logicP; else logicQ = !logicQ;
  const value = name === "P" ? logicP : logicQ;
  const button = document.getElementById(`toggle${name}`);
  button.textContent = value ? "V (Verdadeiro)" : "F (Falso)";
  button.className = `btn-toggle ${value ? "true-val" : "false-val"}`;
  document.getElementById("logicQuickRes").innerHTML = `<div class="result-row"><strong>P ∧ Q:</strong> <span>${logicP && logicQ ? "V" : "F"}</span></div><div class="result-row"><strong>P ∨ Q:</strong> <span>${logicP || logicQ ? "V" : "F"}</span></div>`;
}
function vector(id) { return document.getElementById(id).value.split(",").map(Number); }
function calculateEuclidean() {
  const [x1, y1] = vector("vecU"); const [x2, y2] = vector("vecV"); const det = x1 * y2 - y1 * x2;
  document.getElementById("resDot").textContent = x1 * x2 + y1 * y2;
  document.getElementById("resNormU").textContent = Math.hypot(x1, y1).toFixed(2);
  document.getElementById("resLILD").textContent = Math.abs(det) < 1e-9 ? "LD (Linearmente Dependentes)" : "LI (Linearmente Independentes)";
  document.getElementById("resIsBasis").textContent = Math.abs(det) < 1e-9 ? "Não (dimensão gerada < 2)" : "Sim, formam base de R²";
}
function calculateLinearTransform() {
  const a = +document.getElementById("matA").value, b = +document.getElementById("matB").value, c = +document.getElementById("matC").value, d = +document.getElementById("matD").value;
  const det = a * d - b * c; const invertible = Math.abs(det) > 1e-9;
  document.getElementById("resDet").textContent = det;
  document.getElementById("resKernel").textContent = invertible ? "{ (0, 0) } (dim = 0)" : "Núcleo não trivial (dim ≥ 1)";
  document.getElementById("resIso").textContent = invertible ? "Bijetora → É um isomorfismo" : "Não é bijetora → Não é isomorfismo";
}
function calculateSequencesAndQueue() {
  const a1 = +document.getElementById("seqA1").value, r = +document.getElementById("seqR").value, n = +document.getElementById("seqN").value;
  const paN = a1 + (n - 1) * r, paSum = n * (a1 + paN) / 2, pgN = a1 * r ** (n - 1), pgSum = r === 1 ? a1 * n : a1 * (r ** n - 1) / (r - 1);
  document.getElementById("resPA").textContent = `a${n} = ${paN} | S${n} = ${paSum}`;
  document.getElementById("resPG").textContent = `a${n} = ${pgN} | S${n} = ${pgSum}`;
  const lambda = +document.getElementById("queueLambda").value, mu = +document.getElementById("queueMu").value, stable = lambda < mu;
  document.getElementById("resQueueRho").textContent = `${(lambda / mu * 100).toFixed(1)}% (${stable ? "Sistema estável" : "Sistema instável"})`;
  document.getElementById("resQueueL").textContent = stable ? `${(lambda / (mu - lambda)).toFixed(2)} clientes` : "Tende ao infinito";
}

function askCamilePreset(message) { document.getElementById("camileUserInput").value = message; handleCamileSubmit(new Event("submit")); }
function handleCamileSubmit(event) {
  event.preventDefault(); const input = document.getElementById("camileUserInput"); const message = input.value.trim(); if (!message) return;
  const box = document.getElementById("camileChatMessages");
  box.insertAdjacentHTML("beforeend", `<div class="msg-bubble msg-user"></div>`); box.lastElementChild.textContent = message;
  const lower = message.toLowerCase(); let answer = "Comece identificando as variáveis, os parâmetros e as hipóteses. Depois formule a relação matemática e valide o resultado com um caso simples.";
  if (lower.includes("p.g") || lower.includes("pg")) answer = "Em uma P.G., use aₙ = a₁·qⁿ⁻¹. Para somar, Sₙ = a₁(qⁿ−1)/(q−1), quando q≠1.";
  else if (lower.includes("núcleo")) answer = "Para achar o núcleo, resolva T(v)=0. Se o único resultado for o vetor nulo, a transformação é injetora.";
  else if (lower.includes("fila")) answer = "Na fila M/M/1, primeiro verifique λ<μ. Depois calcule ρ=λ/μ e L=λ/(μ−λ).";
  box.insertAdjacentHTML("beforeend", `<div class="msg-bubble msg-tutor"></div>`); box.lastElementChild.textContent = answer;
  input.value = ""; box.scrollTop = box.scrollHeight;
}
function clearCamileChat() { document.getElementById("camileChatMessages").innerHTML = '<div class="msg-bubble msg-tutor">Olá! Sou Camile Dias. Como posso ajudar no seu estudo hoje?</div>'; }

function selectQuizModule(module, button) {
  activeQuizModule = module; activeQuestion = 0; quizCorrect = 0;
  document.querySelectorAll(".quiz-mod-btn[data-qmod]").forEach((item) => item.classList.toggle("active", item.dataset.qmod === module));
  if (button) button.classList.add("active");
  document.getElementById("quizFinished").classList.add("hidden");
  document.getElementById("quizModuleBadge").textContent = legacyQuizData[module].label;
  renderLegacyQuestion();
}
function renderLegacyQuestion() {
  const quiz = legacyQuizData[activeQuizModule]; const [question, options] = quiz.questions[activeQuestion];
  document.getElementById("quizProgText").textContent = `Questão ${activeQuestion + 1} de ${quiz.questions.length}`;
  document.getElementById("quizContainer").innerHTML = `<div class="quiz-question-block"><h3>${question}</h3><div class="quiz-options">${options.map((option, index) => `<button type="button" class="quiz-option" onclick="answerLegacyQuiz(${index}, this)">${option}</button>`).join("")}</div><p id="inlineQuizFeedback" class="quiz-feedback"></p></div>`;
}
function answerLegacyQuiz(answer, button) {
  const correct = legacyQuizData[activeQuizModule].questions[activeQuestion][2];
  document.querySelectorAll(".quiz-option").forEach((item) => { item.disabled = true; });
  button.classList.add(answer === correct ? "correct" : "wrong");
  if (answer !== correct) document.querySelectorAll(".quiz-option")[correct].classList.add("correct"); else quizCorrect++;
  document.getElementById("inlineQuizFeedback").textContent = answer === correct ? "Correto! +25 XP" : "Revise a explicação do módulo e tente novamente.";
  setTimeout(() => { activeQuestion++; if (activeQuestion < legacyQuizData[activeQuizModule].questions.length) renderLegacyQuestion(); else finishLegacyQuiz(); }, 850);
}
function finishLegacyQuiz() {
  document.getElementById("quizContainer").innerHTML = ""; document.getElementById("quizFinished").classList.remove("hidden");
  document.getElementById("quizDoneTitle").textContent = `${quizCorrect} de 3 respostas corretas`;
  document.getElementById("quizFinalMsg").textContent = quizCorrect >= 2 ? "Muito bem! Você concluiu este nível." : "Revise o módulo e refaça o desafio.";
  const xp = 300 + quizCorrect * 25; document.getElementById("xpPoints").textContent = xp; document.getElementById("scoreText").textContent = `Experiência: ${xp} XP`;
}
function restartCurrentModuleQuiz() { selectQuizModule(activeQuizModule); }
function unlockCertificate() { window.showToast("Certificado liberado para personalização."); }
function updateCertificate() { const value = document.getElementById("studentNameInput").value.trim(); if (value) document.getElementById("certNameDisplay").textContent = value; }

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("setA")) calculateSets();
  if (document.getElementById("toggleQ")) { toggleVal("Q"); toggleVal("Q"); }
});
