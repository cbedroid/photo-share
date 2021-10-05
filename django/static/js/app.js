$(document).ready(function () {
  const CLICK = "click";
  const SHADOW = "shadow-lg"; // Tailwind shadow class

  /* --------------------------------
    Bootstrap Message Alert
  ------------------------------------*/
  const message_alert = document.getElementById("alert_message");
  $(message_alert).delay(5000).fadeOut(1500);
  $(".close").on(CLICK, function () {
    $(message_alert).fadeOut(400);
  });

  /* --------------------------------
      Magnific Popup
  ------------------------------------*/
  $("#gallery-photo-collections .photo__card").each(function () {
    console.log("Gallery Photo", this);
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

  /* --------------------------------
      Dropdown Collapse and Expand
  ------------------------------------*/
  const togglers = $('[data-toggler="true"]');
  togglers.bind(CLICK, function () {
    const target = $(this).data("dropdown-target");
    $(`[data-target=${target}`).toggleClass("collapse collaspe--all-device");
  });

  /* --------------------------------
      Aside Sidebar
  ------------------------------------*/
  const toggleCheckBoxMenu = () => {
    const aside_menu_btn = $("#aside_menu_btn");
    $("#aside_checkbox").prop("checked")
      ? $(aside_menu_btn).removeClass("fa fa-bars").addClass(" fas fa-times")
      : $(aside_menu_btn).removeClass("fas fa-times").addClass(" fa fa-bars");
  };

  $(".preview").bind(CLICK, function () {
    const toggler = $(this).find(".preview__toggler").first();
    if (toggler !== "undefined") {
      $(toggler).toggleClass("fa-caret-down fa-caret-up");
    }
  });

  /* --------------------------------
     Register Checkbox Event
  ------------------------------------*/
  $("#aside_checkbox").on("change", function () {
    toggleCheckBoxMenu();
  });

  /**
   * CUSTOM IMAGE UPLOAD FORM SCRIPT
   **/
  (function () {
    const photo_form = $(".photoform__card");
    const form_inputs = $(photo_form).find("input[type=file]");

    if (photo_form) {
      const image_labels = $(".photoform__card").find("label");
      // Attach attr "for" to the custom input
      $(form_inputs).each((i, c) => {
        $(image_labels[i]).attr("for", $(c).attr("id"));
      });

      $(form_inputs).on("change", function () {
        // Set image preview and change label to filename name
        const image_file = this.files[0];

        // set preview image
        const filereader = new FileReader();
        const form_image = $(photo_form).find(".form-image");
        if (form_image && image_file) {
          filereader.readAsDataURL(image_file);
          // wait until image is loaded
          filereader.onloadend = (e) => {
            form_image[0].src = e.target.result;
          };
        }
        // Change form label name to the upload file name
        const custom_label = $(this).siblings("label").find(".image__label");
        $(custom_label)
          .addClass("font-semibold")
          .attr({
            title: image_file.name,
          })
          .text(image_file.name);
      });
    }
  })();
  /**
   * CUSTOM IMAGE UPLOAD FORM SCRIPT END
   **/

  /* --------------------------------
      Window and Main Events
  ------------------------------------*/
  $("#site-main,#main-overlay").on(CLICK, function () {
    // close aside menu
    $("#aside_checkbox").prop("checked", false);
    toggleCheckBoxMenu();
  });

  // Navigation Scroll Shadow
  $(window).scroll(function () {
    const mini_nav = $("#mini-nav");
    const main_nav_height = $("#main-nav").height() + 5; // add a little padding

    if ($(window).scrollTop() > main_nav_height) {
      $(mini_nav).addClass(SHADOW); // show navigation shadow
      $('[data-scroll-show="true"]').removeClass("invisible");
    } else {
      $(mini_nav).removeClass(SHADOW);
      $('[data-scroll-show="true"]').addClass("invisible");
    }
  });
}); //ready
