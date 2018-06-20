// Set (then unset) this to supress the ajax loading animation
var suppressLoadingBlock = false;

$(document).ready(function() {
    // Scrap modals if they lose focus so they can be loaded with new content
    $('.modal').on('hidden.bs.modal', function(e)
    {
        if (!$(this).hasClass('exclude-scrap')) {
          $(this).removeData();
          x = $(this).find('.modal-content > *');
          //console.log(x)
          x.remove()
        }
    });

    $('.modal').on('loaded.bs.modal', function() {
        // Need to do this on modal show for newly added popovers
        $('.aristotle-popover').popover()
    });

    // Initialize popovers
    $('.aristotle-popover').popover()

    // Perform initial notification loading
    fetch_api_data(fill_aristotle_notification_menu, 5) 

    // Set up reload on click
    $('#header_menu_button_notifications').click(reload_notifications)
});

// getCookie function taken from django docs
// Used to get csrf_token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ajaxSend(function(event, request, settings) {
    if (!suppressLoadingBlock) {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    }
});

$(document).ajaxComplete(function(event, request, settings) {
    $('#loading_indicator').hide().removeClass('loading');
});

// Callback for notify menu
function fill_aristotle_notification_menu(data) {
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
