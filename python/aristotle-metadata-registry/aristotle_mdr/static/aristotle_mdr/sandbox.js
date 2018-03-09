$(document).ready(function() {
  $('#delete-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var itemid = button.data('item-id') // Extract info from data-* attributes
    console.log(itemid);
    var modal = $(this);
    button = modal.find('#delete_submit_button');
    console.log(button);
  })
})
