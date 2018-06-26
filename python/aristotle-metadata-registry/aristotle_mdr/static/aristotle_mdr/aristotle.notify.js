var loading_notifications = false

function fetch_api_data(callback, num) {

    if (!loading_notifications) {
      loading_notifications = true;
      suppressLoadingBlock = true
      var apiurl='/account/notifications/api/unread_list/'
      var full_url = apiurl + '?max=' + num

      setTimeout(function() {
        $.ajax({
          url: full_url, 
          dataType: "json",
          success: callback,
          complete: function() {
            loading_notifications = false
            suppressLoadingBlock = false
          },
          error: function() {
            display_notify_error()
          }
        })
      }, 500)
    }

}

// Callback for notify menu
function fill_aristotle_notification_menu(data) {
    update_notification_badge(data)
    var menu = $('.notify-menu')[0]
    var notify_unread_url = '/account/notifications'
    if (menu) {
        menu.innerHTML = "";
        if (data.unread_list.length > 0) {
            for (var i=0; i < data.unread_list.length; i++) {
                var item = data.unread_list[i];
                if (item.target_object_id) {
                    menu.innerHTML = menu.innerHTML + "<li><a href='/notifyredirect/"+ item.target_content_type+ "/" + item.target_object_id + "'>"+item.verb+" - "+item.actor+"</a></li>";
                } else {
                    menu.innerHTML = menu.innerHTML + "<li><a>" + item.verb + " - " + item.actor+"</a></li>";
                }
            }
            menu.innerHTML = menu.innerHTML + '<li role="presentation" class="divider"></li>';
            menu.innerHTML = menu.innerHTML + "<li><a href='#' onclick='mark_all_unread();return false'><i class='fa fa-envelope-o fa-fw'></i> Mark all as read</a></li>";
            menu.innerHTML = menu.innerHTML + "<li><a href='"+notify_unread_url+"'><i class='fa fa-inbox fa-fw'></i> View all unread notifications...</a></li>";
        } else {
            menu.innerHTML = "<li><a href='"+notify_unread_url+"'><i class='fa fa-inbox fa-fw'></i> No unread notifications...</a></li>";
        }
    }
}

function update_notification_badge(data) {
  var num_notifications = data.unread_count
  $('.notify-badge').each(function() {
    this.innerHTML = num_notifications
  })
}

function make_dropdown_item(text) {
    var textelement = document.createElement('li')
    var linkelement = document.createElement('a')
    var text = document.createTextNode(text)
    linkelement.href = "#"
    linkelement.appendChild(text)
    textelement.appendChild(linkelement)

    return textelement
}

function reload_notifications() {
  if (!loading_notifications) {
    var menu = $('.notify-menu')[0]

    menu.innerHTML = ""

    // Make loading icon li element
    var listelement = document.createElement('li')
    var centerdiv = document.createElement('div')
    var icon = document.createElement('i')
    centerdiv.className = 'text-center'
    icon.className = 'fa fa-refresh fa-spin'
    centerdiv.appendChild(icon)
    listelement.appendChild(centerdiv)

    // Make text element
    textelement = make_dropdown_item('Fetching Notifications...')

    menu.append(listelement)
    menu.append(textelement)

    // Perform update
    fetch_api_data(fill_aristotle_notification_menu, 5)
  }

}

function display_notify_error() {
    var menu = $('.notify-menu')[0]
    menu.innerHTML = ""

    // Add text
    list_element = make_dropdown_item('Notifications could not be retrieved')

    menu.append(list_element)
}

function mark_all_unread() {
  var notify_mark_all_unread_url = '/account/notifications/api/mark-all-as-read/'

  $.getJSON(notify_mark_all_unread_url, function (data) {
    if (data.status == 'success') {
      reload_notifications()
    }
  })

}

$(document).ready(function() {
  // Set up reload on click
  $('#header_menu_button_notifications').click(reload_notifications)
})
