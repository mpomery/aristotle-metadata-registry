// This script tracks changes on a status change to help a user know
// how visible an item will be after an item is registered.

// These are defined in "templates/aristotle_mdr/actions/changeStatus.html"
/* global select_state_to_see */
/* global status_matrix */
/* global visibility_translations */
/* global same_visibility_text */
/* global diff_visibility_text */
/* global current_visibility */

$(document).ready(function() {
    $("#changeStatus input").change(function() {
        var state = $('#changeStatus input[name$=state]:checked').val();
        console.log(state);
        var selected_ras = $("#changeStatus input[name$=registrationAuthorities]:checked");
        if (selected_ras.length == 0) {
           // Diffent name on review create form
           var selected_ras = $("#changeStatus input[name=registration_authority]:checked")
        }
        if ((typeof state === "undefined") || (selected_ras.length == 0)){
            $('#potential').html(select_state_to_see);
        } else {
            $('#potential').html(this.name);
            var new_visibility = "hidden";
            selected_ras.each(function( index ) {
                var ra = $(this).val();
                console.log(
                    status_matrix[ra].states[state]
                );
                var potential_vis = status_matrix[ra].states[state];
                if (potential_vis == "public") {
                    new_visibility = potential_vis;
                } else if (new_visibility == "public") {
                    // Do nothing, if one thinks its public, its public
                } else if (potential_vis == "locked") {
                    new_visibility = potential_vis;
                }
            });
            var msg = "";
            var vis_trans = visibility_translations[new_visibility];
            if (new_visibility == current_visibility) {
                msg = same_visibility_text;
            } else {
                msg = diff_visibility_text;
            }
            msg = msg.replace('VISIBILITY_STATUS',vis_trans);

            $('#potential').html(msg);
        }
    });
});
