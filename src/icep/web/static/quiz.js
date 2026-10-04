// Client-side scoring for the awareness quiz. The server stays read-only; the correct answers are
// data attributes (this is illustrative training, not an exam).
(function () {
  "use strict";
  var form = document.getElementById("quiz");
  var submit = document.getElementById("quiz-submit");
  if (!form || !submit) return;

  submit.addEventListener("click", function () {
    var questions = form.querySelectorAll(".qz");
    var correct = 0;
    questions.forEach(function (q) {
      var want = parseInt(q.getAttribute("data-correct"), 10);
      var chosen = q.querySelector("input[type=radio]:checked");
      var feedback = q.querySelector(".qz-feedback");
      var explain = q.getAttribute("data-explain") || "";
      if (chosen && parseInt(chosen.value, 10) === want) {
        correct += 1;
        feedback.textContent = "Correct. " + explain;
        feedback.className = "qz-feedback status-pass";
      } else {
        feedback.textContent = "Not quite. " + explain;
        feedback.className = "qz-feedback status-fail";
      }
      feedback.hidden = false;
    });

    var total = questions.length;
    var score = total ? correct / total : 0;
    var threshold = parseFloat(form.getAttribute("data-threshold") || "0.8");
    var passed = score >= threshold;
    var result = document.getElementById("quiz-result");
    result.textContent =
      "Score: " + correct + "/" + total + " (" + Math.round(score * 100) + "%) — " +
      (passed ? "PASS" : "below the pass mark, review and retry");
    result.style.color = passed ? "#059669" : "#b91c1c";
    result.hidden = false;
  });
})();
