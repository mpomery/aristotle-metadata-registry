$(document).ready(function() {

  // Remove href attributes if javascript enabled
  // This will not be needed if using bootstrap 4.0
  $('.delete-button').each(function() {
      $(this).removeAttr('href');
  })

  $('#delete-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var item_id = button.data('item-id') // Extract info from data-* attributes
    var csrftoken = $("[name=csrfmiddlewaretoken]").val(); // Can do this since a token is already on the page
    var modal = $(this);

    // Set element name
    var element_name = button.closest('tr').find('.itemLink').text();
    modal.find('#element-name').html($.trim(element_name));

    submit_button = modal.find('#delete-submit-button');
    submit_url = submit_button.attr('submit-url');
    message_p = modal.find('#modal-message')

    submit_button.on("click", function() {
        $.ajax({
          method: "POST",
          url: submit_url,
          data: {item: item_id, csrfmiddlewaretoken: csrftoken},
          datatype: "json",
          success: function(data) {
              if (data.completed) {
                // Remove item's row
                button.closest('tr').remove();
                modal.modal('hide');
              } else if (data.message) {
                message_p.html(data.message);
              }
          },
          error: function() {
              message_p.html("The item could not be deleted");
          }
        })
    })
  })

  $('#delete-modal').on('hide.bs.modal', function(event) {
    var modal = $(this);
    submit_button = modal.find('#delete-submit-button');
    submit_button.off("click") //Unbind the on click event
  })
})
