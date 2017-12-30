const path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
    // context: path.resolve(__dirname, 'static'),
    entry: {
        teams: './static/teams/js/teams.js',
        'division-calendar': './static/calendar/js/division-calendar.js',
        'session-calendar': './static/calendar/js/session-calendar.js',
        'session-event-calendar': './static/calendar/js/session-event-calendar.js',
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
        loaders: [
            {test: /\.css$/, loader: "style-loader!css-loader"},
            {test: require.resolve('jquery'), loader: 'expose-loader?$!expose-loader?jQuery'},
            {test: require.resolve('moment'), loader: 'expose-loader?moment'}
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
