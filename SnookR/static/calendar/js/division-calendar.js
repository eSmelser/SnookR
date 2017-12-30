let api = require('../../api/js/api');
let fullcalendar = require('fullcalendar');
let templates = require('../../core/js/templates');

$(document).ready(function () {
    api.getSessionList(data).done(function (data) {
        $('#calendar').fullCalendar({
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay,listWeek'
            },
            defaultDate: new Date().toISOString(),
            navLinks: true, // can click day/week names to navigate views
            editable: false,
            eventLimit: true, // allow "more" link when too many events
            eventClick: function (calEvent, jsEvent, view) {
                let session = data.find( elem => elem.name === calEvent.title );

                // Fill the event content element with event data
                $('#id_event_content').empty().append(createSessionPanel(session));

                // change the border color just for fun
                $(this).css('border-color', 'red');
            },
            events: eventList,
        });
    });
});