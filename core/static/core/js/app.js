$(document).ready(function () {
  const message_alert = document.getElementById("alert_message");
  $(message_alert).delay(5000).fadeOut(1500);
  $(".close").on("touch click", function () {
    $(message_alert).fadeOut(400);
  });
}); //ready
