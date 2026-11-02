const API = "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);
let markdown = "";
function renderMarkdown(text) {
  return text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/^### (.*)$/gm,"<h3>$1</h3>").replace(/^## (.*)$/gm,"<h2>$1</h2>")
    .replace(/^# (.*)$/gm,"<h1>$1</h1>").replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>")
    .replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\n/g,"<br>");
}
$("analyze-form").addEventListener("submit", async (event) => {
  event.preventDefault(); $("status").textContent = "Analyzing repository…";
  try { const response = await fetch(`${API}/api/analyze`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({repository_url:$("repository-url").value})});
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Analysis failed.");
    markdown = data.readme.markdown; $("repo-name").textContent = data.repository.name; $("repo-description").textContent = data.repository.description || "No description provided.";
    $("repo-details").innerHTML = `<dt>Language</dt><dd>${data.repository.language || "Not detected"}</dd><dt>Stars</dt><dd>${data.repository.stars}</dd><dt>Files scanned</dt><dd>${data.analysis.files_scanned}</dd><dt>Project type</dt><dd>${data.repository.project_type}</dd><dt>Dependencies</dt><dd>${data.analysis.dependencies.join(", ") || "None detected"}</dd>`;
    $("preview").innerHTML = renderMarkdown(markdown); $("code").textContent = markdown; $("results").hidden = false; $("status").textContent = "README generated from repository evidence.";
  } catch (error) { $("status").textContent = error.message; }
});
document.querySelectorAll(".tab").forEach(tab => tab.addEventListener("click", () => { document.querySelectorAll(".tab").forEach(item => item.classList.remove("active")); tab.classList.add("active"); $("preview").hidden = tab.dataset.tab !== "preview"; $("code").hidden = tab.dataset.tab !== "code"; }));
$("copy").addEventListener("click", async () => { await navigator.clipboard.writeText(markdown); $("status").textContent = "Markdown copied."; });
$("download").addEventListener("click", () => { const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([markdown], {type:"text/markdown"})); link.download = "README.md"; link.click(); URL.revokeObjectURL(link.href); });
