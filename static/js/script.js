document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('button[data-bs-target="#editExpenseModal"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = this.getAttribute("data-id")
      var card = document.querySelector('.expense-card[data-id="' + id + '"]')

      document.getElementById("editExpenseForm").action = "/edit/" + id + "/"
      document.getElementById("editExpenseId").value = id
      document.getElementById("editExpenseTitle").value =
        card.querySelector(".expense-title").textContent

      var price = card.querySelector(".expense-price").textContent
      document.getElementById("editExpensePrice").value = price.replace("$", "").trim()

      var catName = card.querySelector(".expense-category").textContent
      var select = document.getElementById("editExpenseCategory")
      for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].textContent === catName) {
          select.options[i].selected = true
          break
        }
      }
    })
  })

  document.querySelectorAll('button[data-bs-target="#deleteExpenseModal"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = this.getAttribute("data-id")
      var card = document.querySelector('.expense-card[data-id="' + id + '"]')

      document.getElementById("deleteExpenseForm").action = "/delete/" + id + "/"
      document.getElementById("deleteExpenseTitle").textContent =
        card.querySelector(".expense-title").textContent
    })
  })

  document.querySelectorAll('button[data-bs-target="#editCategoryModal"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = this.getAttribute("data-id")

      var category = document.querySelector('.category-row[data-id="' + id + '"]')

      console.log(category)

      document.getElementById("editCategoryName").value = category.getAttribute("data-name")

      document.getElementById("editCategoryForm").action = "/edit-category/" + id + "/"
    })
  })

  document.querySelectorAll('button[data-bs-target="#deleteCategoryModal"]')
    .forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = this.getAttribute("data-id")

        var category = document.querySelector('.category-row[data-id="' + id + '"]')

        document.getElementById("deleteCategoryName").textContent =
          category.getAttribute("data-name")

        document.getElementById("deleteCategoryForm").action = "/delete-category/" + id + "/"
      })
    })
})

const hideMessage = (message) => {
    if (message.classList.contains('is-hiding')) return;

    message.classList.add('is-hiding');

    setTimeout(() => {
        message.remove();
    }, 300);
};

document.querySelectorAll('.pet-message').forEach(message => {
    const closeButton = message.querySelector('.btn-close');

    closeButton?.addEventListener('click', () => {
        hideMessage(message);
    });

    if (message.classList.contains('success')) {
        setTimeout(() => {
            hideMessage(message);
        }, 4000);
    }
});