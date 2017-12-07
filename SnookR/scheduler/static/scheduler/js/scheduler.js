const createSessionPanel = function (sessionData) {
    let subs = sessionData['subs']
        .map(elem =>
            `<li>
                <a href=\"${api.baseURL + elem.user.url}\">${elem.user.username}</a>
            </li>`)
        .reduce((a, b) => a + b, ``);

    $content = $('<div>').html(`
        <div>
            <h2>${sessionData['name']}</h2>
            <h3>Available Subs</h3>
            <ul>
                ${subs}
            </ul>
        </div>
    `);

    $column = $('<div>').attr('class', 'col-md-12').append($content);
    $row = $('<div>').attr('class', 'row').append($column);
    return $row;
};

$(document).ready(function () {

    // Filter the Session data set on the Division.slug field of the Division foreign key.
    let division = $('#id_division').val();
    let data = division ? {division__slug: division} : {};

    api.getSessionList(data).done(function (data) {
        let sessionList = [];
        for (elem in data) {
            if (data.hasOwnProperty(elem)) {
                sessionList.push(data[elem])
            }
        }

        let eventList = sessionList.map(elem => {
            return {title: elem.name, start: elem.start_date, end: elem.end_date}
        });


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
                console.log('eventClick', calEvent);

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