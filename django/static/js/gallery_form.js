$(document).ready(() => {
  /**
   * CUSTOM IMAGE UPLOAD FORM SCRIPT
   **/
  (function handleImageUpload() {
    const photo_form = $("#photoset-field .card");
    const form_inputs = $(photo_form).find("input[type=file]");

    if (photo_form) {
      const image_labels = $(photo_form).find(".image-label label");
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
});
