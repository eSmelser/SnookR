/**
 * Created by bobby on 12/27/17.
 */
const genericUserPanelDOM = function (user, actionDOMString) {
    return $(genericUserPanelDOMString(user, actionDOMString));
};


const genericUserPanelDOMString = function (user, actionDOMString) {
    //This layout is inspired by the snippet found here: https://bootsnipp.com/snippets/56ExR
    return (`<div class="panel panel-default">
                <div class="panel-body">
                      <div class="pull-left">
                            <a href="${user.url}">
                                <img class="img-circle" width="50px" height="50px"
                                     style="margin-right:8px; margin-top:-5px;"
                                     src="${user.thumbnail_url}"
                                >
                            </a>
                        </div>
                        <h4 class="pull-left"><a href="${user.url}"
                                                 style="text-decoration:none;"><strong>${user.username}</strong></a>
                        </h4>
                        ${actionDOMString ? actionDOMString : '<span></span>'}
                </div>  
            </div>`)
};