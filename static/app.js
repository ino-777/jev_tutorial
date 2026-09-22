const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const deadlineInput = document.getElementById("todo-deadline");
const list = document.getElementById("todo-list");
const errorBox = document.getElementById("error");

const PRIORITY_LABELS = ["低", "中", "高"];

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.hidden = true;
}

async function fetchTodos() {
  const res = await fetch("/api/todos");
  if (!res.ok) throw new Error("failed to load todos");
  return res.json();
}

function renderTodo(todo) {
  const li = document.createElement("li");
  li.className = "todo-item" + (todo.done ? " done" : "");

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = todo.done;
  checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

  const text = document.createElement("span");
  text.className = "todo-text";
  text.textContent = todo.text;

  const meta = document.createElement("span");
  meta.className = "todo-meta";

  if (todo.category) {
    const categoryBadge = document.createElement("span");
    categoryBadge.className = "badge";
    categoryBadge.textContent = todo.category;
    meta.appendChild(categoryBadge);
  }

  if (todo.deadline) {
    const deadlineBadge = document.createElement("span");
    deadlineBadge.className = "badge deadline";
    deadlineBadge.textContent = `締切: ${todo.deadline.replace("T", " ")}`;
    meta.appendChild(deadlineBadge);
  }

  if (todo.priority !== null && todo.priority !== undefined) {
    const priorityBadge = document.createElement("span");
    priorityBadge.className = `badge priority-${todo.priority}`;
    priorityBadge.textContent = `優先度: ${PRIORITY_LABELS[todo.priority] ?? todo.priority}`;
    meta.appendChild(priorityBadge);
  }

  if (todo.is_urgent) {
    const urgentBadge = document.createElement("span");
    urgentBadge.className = "badge urgent";
    urgentBadge.textContent = "緊急";
    meta.appendChild(urgentBadge);
  }

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "delete-btn";
  deleteBtn.textContent = "✕";
  deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

  li.append(checkbox, text, meta, deleteBtn);
  return li;
}

async function refresh() {
  const todos = await fetchTodos();
  list.innerHTML = "";
  for (const todo of todos) {
    list.appendChild(renderTodo(todo));
  }
}

async function toggleTodo(id, done) {
  clearError();
  try {
    const res = await fetch(`/api/todos/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ done }),
    });
    if (!res.ok) throw new Error("update failed");
    await refresh();
  } catch (err) {
    showError("更新に失敗しました: " + err.message);
  }
}

async function deleteTodo(id) {
  clearError();
  try {
    const res = await fetch(`/api/todos/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("delete failed");
    await refresh();
  } catch (err) {
    showError("削除に失敗しました: " + err.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  const deadline = deadlineInput.value || null;

  clearError();
  const submitBtn = form.querySelector("button");
  submitBtn.disabled = true;
  submitBtn.textContent = "jev が分析中…";

  try {
    const res = await fetch("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, deadline }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "追加に失敗しました");
    }
    input.value = "";
    deadlineInput.value = "";
    await refresh();
  } catch (err) {
    showError(err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "追加";
  }
});

refresh().catch((err) => showError("読み込みに失敗しました: " + err.message));
