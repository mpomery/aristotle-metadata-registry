function fetch_api_data(callback, num) {
    var apiurl='/account/notifications/api/unread_list/'
    var full_url = apiurl + '?max=' + num
    $.getJSON(full_url, callback)
}
