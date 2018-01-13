const path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
    entry: {
        teams: './static/teams/js/teams.js',
        'division-calendar': './static/calendar/js/division-calendar.js',
        'session-calendar': './static/calendar/js/session-calendar.js',
        'session-event-calendar': './static/calendar/js/session-event-calendar.js',
        'session-event': './static/substitutes/js/session-event.js',
        'session-event-select': './static/substitutes/js/session-event-select.js',
        'messaging': './static/messaging/js/messaging.js',
        'google': './static/socialauth/js/google.js',
        'facebook': './static/socialauth/js/facebook.js',
        'base': './static/js/base.js',
    },

    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, './static/bundles')
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }),
    ],

    module: {
       rules: [
            {test: /\.css$/, use: "style-loader!css-loader"},
            {test: require.resolve('jquery'), use: 'expose-loader?$!expose-loader?jQuery'},
            {test: require.resolve('moment'), use: 'expose-loader?moment'},
            {test: /\.handlebars$/, use: "handlebars-loader" }
        ],
    },

    resolve: {
        alias: {
            handlebars: 'handlebars/dist/handlebars.min.js',
            fullcalendar: 'fullcalendar/dist/fullcalendar',
            'jquery-ui': 'jquery-ui/jquery-ui.js'
        }
    }
};
