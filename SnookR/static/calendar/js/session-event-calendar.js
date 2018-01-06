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
            let event = calEvent.sessionEvent;
            let $div = $('.substitutes-div').empty();
            event.subs.map( sub => new Sub(sub) )
                      .map( sub => $div.append(sub.$dom) );
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
