document.getElementById("editExpenseModal").addEventListener("show.bs.modal", (event) => {
  const expense = event.relatedTarget.closest(".expense-card").dataset
  const form = document.getElementById("editExpenseForm")

  form.action = expense.editUrl
  form.elements.namedItem("title").value = expense.title
  form.elements.namedItem("price").value = expense.price
  form.elements.namedItem("category").value = expense.category
  form.elements.namedItem("date").value = expense.date
  form.elements.namedItem("description").value = expense.description
})

document.getElementById("deleteExpenseModal").addEventListener("show.bs.modal", (event) => {
  const expense = event.relatedTarget.closest(".expense-card").dataset

  document.getElementById("deleteExpenseForm").action = expense.deleteUrl
  document.getElementById("deleteExpenseTitle").textContent = expense.title
})
