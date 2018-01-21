let api = require('../../api/js/api.js');
let Sub = require('./simple-sub.js')
require('fullcalendar');

$(document).ready(function() {
  $('#invite-all-button').click(function() {
    $('#hidden-invite-form').empty();
    $('.invite-status').each(function(i, obj) {
        let id = $(this).attr('data-sub-id');
        let invited = $(this).attr('data-status');
        if (invited === 'true') {
          let $input = $('<input>', {type: 'hidden', value: id})
          $('#hidden-invite-form').append($input)
        }
    });
  });
});

$(document).ready(function () {
    let times = context.sessionEvents.map(event => new Date(event.date + 'T' + event.start_time).getTime());
    let minTime = new Date(Math.min(...times)).getHours() - 2 + ':00:00';
    let maxTime = new Date(Math.min(...times)).getHours() + 2 + ':00:00';

    event = context.sessionEvents[0];
    let $subsDiv = $('.substitutes-div');
    let $sessionName = $('.session-name');
    let $sessionDate = $('.session-date');


    const render = function() {
        $subsDiv.empty();
        if(event.subs.length === 0) {
            $subsDiv.append('<h3>No Substitutes available!</h3>')
        } else {
            $sessionName.empty().append(event.session.name);
            $sessionDate.empty().append(event.date);
            console.log('sub', event.subs);
            event.subs.map( sub => new Sub(sub) )
                      .map( sub => $subsDiv.append(sub.$dom) );
        }
    };

    render();

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month'
        },
        defaultDate: new Date().toISOString(),
        minTime: minTime,
        maxTime: maxTime,
        navLinks: true, // can click day/week names to navigate views
        editable: false,
        eventLimit: true, // allow "more" link when too many events
        eventClick: function (calEvent, jsEvent, view) {
            event = calEvent.sessionEvent;
            render();
        },
        events: context.sessionEvents.map(sessionEvent => {
            return {
                title: sessionEvent.session.name,
                start: sessionEvent.date + 'T' + sessionEvent.start_time,
                sessionEvent: sessionEvent
            }
        }),
    });
});
