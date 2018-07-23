$(document).ready(function() {

    var processing = false; // If button task processing
    var polling = true; // If polling for status updates

    // Add click event to each task button
    $('.task-btn').each(function() {
        var url = $(this).attr('ajaxurl');
        var button = $(this);
        button.click(function() {
            $.get(url, function(data) {
                button.attr('task_name', button.text());
                button.html('Processing...');
                button.prop('disabled', true);
                button.attr('task_id', data);
                processing = true;
                if (!polling) {
                    status_update()
                }
            })
        })
    })

    var task_table = $('#tasks');
    var url = task_table.attr('ajaxurl');
    var task_status_list = task_table.find('tbody');
    if (url) {
      status_update();
    }

    function status_update() {
      $.ajax({
        url: url,
        dataType: "json",
        global: false,
        success: function(data) {
            console.log(data);
            task_status_list.html("");
            polling = processing
            for (index in data.results) {
              item = data.results[index];
              check_button(item.id, item.status)
              row = $('#task_header').clone()

              if (item.status == 'STARTED') {
                  // If any tasks marked started keep polling
                  polling = true;
              }

              var task_data = "<tr>";
              task_data += "<td>" + item.name + "</td>";
              task_data += "<td>" + item.status + "</td>";
              task_data += "<td>" + item.date_started + "</td>";
              task_data += "<td>" + item.date_done + "</td>";
              task_data += "<td>" + item.user + "</td>";
              task_data += "<td>" + item.result + "</td>";
              task_data += "</tr>";

              task_status_list.append(task_data);
            }
        },
        complete: function(data) {
            // on complete ajax request schedule another in 5 seconds
            if (polling) {
              setTimeout(status_update, 5000);
            }
        }
      })
    }

    function check_button(id, status) {
        if (status != "STARTED") {
            $('.task-btn').each(function() {
                var button = $(this);
                task_id = button.attr('task_id');
                if (task_id == id) {
                    var task_name = button.attr('task_name');
                    button.text(task_name);
                    button.prop('disabled', false);
                    check_if_button_processing();
                }
            })
        }
    }

    function check_if_button_processing() {
        // Check if any buttons are processing
        processing = false;
        $('.taskbtn').each(function() {
            if (button.prop('disabled')) {
                processing = true;
            }
        })
    }

})
