
$(document).ready(() => {
  const menu_toggler = $('#gallery-sidebar .menu-toggler');
  $(menu_toggler).bind('click', function () {

    // rclose all menus and rotate all menus icon caret down (close)
    $(menu_toggler).each((_, btn) => {
      const menu = $(btn).siblings('div').first();
      const menu_icon = $(btn).find('svg');
      $(menu_icon).removeClass('rotate-180')
      // close menu
      $(menu).addClass('hidden');
    })

    // open active menu
    const menu = $(this).siblings('div').first();
    $(menu).removeClass('hidden');

    // toggle active menu caret sign up (open)
    const menu_icon = $(this).find('svg');
    $(menu_icon).toggleClass('rotate-180')

  });

});
