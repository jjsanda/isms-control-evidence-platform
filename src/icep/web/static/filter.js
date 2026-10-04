// Live client-side text filter for any table whose input carries data-filter="#table-id".
// No dependencies; progressive enhancement (the full table renders server-side without JS).
(function () {
  "use strict";
  var inputs = document.querySelectorAll("input[data-filter]");
  inputs.forEach(function (input) {
    var table = document.querySelector(input.getAttribute("data-filter"));
    if (!table) return;
    var countEl = document.getElementById("filter-count");
    input.addEventListener("input", function () {
      var query = input.value.trim().toLowerCase();
      var shown = 0;
      table.querySelectorAll("tbody tr").forEach(function (row) {
        var match = row.textContent.toLowerCase().indexOf(query) !== -1;
        row.style.display = match ? "" : "none";
        if (match) shown += 1;
      });
      if (countEl) countEl.textContent = shown;
    });
  });
})();
