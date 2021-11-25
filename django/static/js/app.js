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
    const dropdown_elem = $(this).data("dropdown-target");
    const target = $(`[data-target=${dropdown_elem}`)[0];
    $(target).toggleClass("collapse collapse--all-device");
    const is_expanded = $(target).attr("data-expanded") == "true";
    $(target).attr("data-expanded", !is_expanded);
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
