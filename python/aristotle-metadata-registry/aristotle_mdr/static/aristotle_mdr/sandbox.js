$(document).ready(function() {

  // Remove href attributes if javascript enabled
  // This will not be needed if using bootstrap 4.0
  $('.delete-button').each(function() {
      $(this).removeAttr('href');
  })

  $('.delete-button').on('click', function() {
    var button = $(this);
    var item_id = button.data('item-id') // Extract info from data-* attributes
    var csrftoken = $("[name=csrfmiddlewaretoken]").val(); // Can do this since a token is already on the page
    var element_name = button.closest('tr').find('.itemLink').text();
    submit_url = delete_submit_url; //submit_button.attr('submit-url');

    bootbox.alert({ 
      size: "small",
      title: "Delete",
      message: "Are you sure you want to delete <span id=\"element-name\">"+element_name+"</span>", 
      callback: function() {
        var modal=$(this);
        var message_p = $(this).find('#modal-message');
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
      }
    })

  })

})
