function fetch_api_data(callback, num) {
    var apiurl='/account/notifications/api/unread_list/'
    var full_url = apiurl + '?max=' + num
    $.getJSON(full_url, callback)
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

function reload_notifications() {
  var menu = $('.notify-menu')[0]

  // Add the loading icon
  var listelement = document.createElement('li')
  var centerdiv = document.createElement('div')
  var icon = document.createElement('i')
  centerdiv.className = 'text-center'
  icon.className = 'fa fa-refresh fa-spin'
  listelement.id = 'notify-loading'
  centerdiv.appendChild(icon)
  listelement.appendChild(centerdiv)
  menu.prepend(listelement)

  // Perform update
  fetch_api_data(fill_aristotle_notification_menu, 5) 

}

function mark_all_unread() {
    var r = new XMLHttpRequest();
    var mark_all_as_read_url = '/account/notifications/mark-all-as-read/'
    r.open("GET", notify_mark_all_unread_url, true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) {
            return;
        }
        var badge = document.getElementById(notify_badge_id);
        if (badge) {
            badge.innerHTML = 0;
        }
    }
    r.send();
}

$(document).ready(function() {
  // Perform initial notification loading
  fetch_api_data(update_notification_badge, 5) 

  // Set up reload on click
  $('#header_menu_button_notifications').click(reload_notifications)
})
