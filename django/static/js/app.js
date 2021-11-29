$(document).ready(function () {
  /*
   * Alert Message
    */
  (function handleAlertMessage() {
    const message_alert = document.getElementById("alert_message");
    $(message_alert).delay(5000).fadeOut(1500);
    $(".close").bind('click', function () {
      $(this).parent().remove();
    });
  })();

  /**
   * Magnific Popup
   *
   */
  (function handleMagnificPopup() {
    $("#gallery-photo-collections .photo__card").each(function () {
      $(this)
        .find(".share_popup")
        .magnificPopup({
          items: [
            {
              src: $(this).find(".social-share").first(),
              type: "inline",
            },
          ],
          closeOnContentClick: true,
          closeBtnInside: false,
        });
    });
  })();

  /**
   * Aside CheckBox Events
   */
  (function handleSideBar() {
    $("#aside_checkbox").bind("change", function () {
      // swap aside toggler from bars to times and vice-versa.
      $('svg.toggler').toggleClass('hidden');

    });
  })();

}); //ready
