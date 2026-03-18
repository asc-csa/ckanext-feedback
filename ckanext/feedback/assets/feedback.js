document.addEventListener("DOMContentLoaded", function () {
  // Star rating handler
  var widget = document.querySelector(".feedback-rating-widget");
  if (widget) {
    var packageId = widget.getAttribute("data-package-id");
    var rateUrl = widget.getAttribute("data-rate-url");
    var stars = widget.querySelectorAll(".feedback-star");
    var avgEl = widget.querySelector(".feedback-avg");
    var countEl = widget.querySelector(".feedback-count");

    stars.forEach(function (star) {
      star.addEventListener("mouseenter", function () {
        var val = parseInt(this.getAttribute("data-value"));
        stars.forEach(function (s) {
          s.style.color =
            parseInt(s.getAttribute("data-value")) <= val
              ? "#f0ad4e"
              : "#ccc";
        });
      });

      star.addEventListener("mouseleave", function () {
        // Restore to current user rating or none
        var current = widget.getAttribute("data-user-rating") || "0";
        var cur = parseInt(current);
        stars.forEach(function (s) {
          s.style.color =
            parseInt(s.getAttribute("data-value")) <= cur
              ? "#f0ad4e"
              : "#ccc";
        });
      });

      star.addEventListener("click", function () {
        var val = parseInt(this.getAttribute("data-value"));
        var csrfInput = document.querySelector(
          'input[name="csrf_token"], input[name="_csrf_token"]'
        );
        var csrfToken = csrfInput ? csrfInput.value : "";

        var formData = new FormData();
        formData.append("rating", val);
        if (csrfToken) {
          formData.append("csrf_token", csrfToken);
          formData.append("_csrf_token", csrfToken);
        }

        fetch(rateUrl, {
          method: "POST",
          credentials: "same-origin",
          body: formData,
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (data.error) return;
            avgEl.textContent = data.average;
            countEl.textContent = data.count;
            widget.setAttribute("data-user-rating", data.user_rating);
            stars.forEach(function (s) {
              s.style.color =
                parseInt(s.getAttribute("data-value")) <= data.user_rating
                  ? "#f0ad4e"
                  : "#ccc";
            });
          });
      });
    });

    // Set initial user rating data attribute
    var initialRating = 0;
    stars.forEach(function (s) {
      if (s.style.color === "rgb(240, 173, 78)") {
        var v = parseInt(s.getAttribute("data-value"));
        if (v > initialRating) initialRating = v;
      }
    });
    widget.setAttribute("data-user-rating", initialRating);
  }

  // reCAPTCHA loader
  var form = document.querySelector(
    ".feedback-submission-form[data-recaptcha-sitekey]"
  );
  if (form) {
    var sitekey = form.getAttribute("data-recaptcha-sitekey");
    var container = document.getElementById("feedback-recaptcha");
    if (sitekey && container) {
      var script = document.createElement("script");
      script.src = "https://www.google.com/recaptcha/api.js?onload=feedbackRecaptchaReady&render=explicit";
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);

      window.feedbackRecaptchaReady = function () {
        grecaptcha.render("feedback-recaptcha", { sitekey: sitekey });
      };
    }
  }
});
