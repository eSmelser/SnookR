$(document).ready(function() {
    // Change text fields to reflect selected toggle option
    $('.toggle-option').on('click', function(event) {
        const optionDescriptionText = $(this).text();
        const optionId = $(this).attr('id');
        $caret = $('<span>').attr('class', 'caret');

        let optionText;
        switch (optionId) {
            case 'id_option_substitute':
                optionText = 'substitute';
                break;
            case 'id_option_session':
                optionText = 'session';
                break;
            default:
                optionText = 'substitute';
                break;
        }

        $('#id_dropdown_toggle').text(optionDescriptionText).append($caret);
        $('#id_search_field').attr('placeholder', optionDescriptionText);
        $('#id_selected_option').val(optionText);
    });

    $('#id_submit_button').on('click', function(event) {
        event.preventDefault();
        const option = $('#id_selected_option').val();
        const searchTerm = $('#id_search_field').val();
        const baseURL = window.location.origin;
        const requestURL = baseURL + '/search/' + option + '?query=';

        if (searchTerm) {
            window.location.href = requestURL + searchTerm.replace(/ /g, '+');
        }
    });
});