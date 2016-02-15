function executeElementStatus( element, status ) {
    if (status) {
        $(element).fadeIn(250);
    } else {
        $(element).fadeOut(250);
    }
}

function executeResponses( responses ) {
    var action = $("#action-select");
    if (action.length) {
        var select = action[0].selectize;
        for (var objkey in select.options) {
            var obj = select.options[objkey];
            if (obj.optgroup == 'responses') {
                select.removeOption(objkey);
            }
        }
        select.removeOptionGroup('responses');
        if (Object.keys(responses).length > 0) {
            select.addOptionGroup('responses', {id: "action-responses", label: "Responses"});
            for (var resp in responses) {
                select.addOption({value: 'r-' + resp, icon: 'comment', text: responses[resp], optgroup: 'responses'});
            }
        }
    }
}

function executeLocaleAct() {
    $.ajax("/q/localeact").done(function( data ) {
        console.log(data);
        var action = $("#action-select");
        if (action.length) {
            var select = action[0].selectize;
            select.clearOptionGroups();
            select.clearOptions();
            console.log(data["actions"]);
            var groups = [];
            for (var objkey in data["actions"]) {
                var obj = data["actions"][objkey];
                console.log(obj);
                if (!(obj["optgroup"] in groups)) {
                    select.addOptionGroup(obj["optgroup"], {id: "action-" + obj["optgroup"], label: obj["optlabel"]});
                    groups.push(obj["optgroup"]);
                }
                select.addOption({value: obj["value"], icon: obj["icon"], text: obj["text"], optgroup: obj["optgroup"]});
            }
            if ("responses" in data) {
                executeResponses(data["responses"]);
            }
        }
    });
}

function executeLocaleTravel() {
    $.ajax("/q/localetravel").done(function( data ) {
        console.log(data);
        var action = $("#travel-select");
        if (action.length) {
            var select = action[0].selectize;
            select.clearOptions();
            console.log(data["linked"]);
            var valueset = false;
            for (var objkey in data["linked"]) {
                var obj = data["linked"][objkey];
                console.log(obj);
                select.addOption({value: obj["value"], text: obj["name"]});
                if (!valueset) {
                    valueset = true;
                    select.setValue(obj["value"], true);
                }
            }
        }
    });
}

function executeActStatus( status ) {
    var action = $("#action-select");
    if (action.length) {
        var select = action[0].selectize;
        if (status) {
            select.unlock();
        } else {
            select.lock();
        }
    }
}

function executeMsg( sender, msg, eclass ) {
    if ($("#central.messages").length) {
        var html = '<div class="message ' + eclass + '">';
        if (sender) {
            html += '<span class="sender">' + sender + ':</span> ';
        }
        html += msg + '</div>';
        $("#central.messages").append(html).animate({ scrollTop: $('#central.messages').prop("scrollHeight")}, 'fast');
    }
}

function executeCommands(commands, index) {
    if (commands.length > index) {
        var command = commands[index];
        console.log(command);
        if (command["type"] == "central") {

        } else if (command["type"] == "status") {
            executeElementStatus(command["element"], command["status"]);
        } else if (command["type"] == "responses") {
            executeResponses(command["responses"]);
        } else if (command["type"] == "msg") {
            if ("eclass" in command) {
                executeMsg(command["sender"], command["msg"], command["eclass"]);
            } else {
                executeMsg(command["sender"], command["msg"], "");
            }
        } else if (command["type"] == "localeact") {
            executeLocaleAct();
        } else if (command["type"] == "localetravel") {
            executeLocaleTravel();
        } else if (command["type"] == "location") {
            $("#travelModalRevealer").find("span").text(command["name"]);
        } else if (command["type"] == "actbarstatus") {
            executeActStatus(command["status"]);
        }

        if ("time" in command && command["time"] > 0) {
            console.log(command["time"]);
            setTimeout(function() {
                executeCommands(commands, index+1)
            }, command["time"]);
        } else {
            console.log(0);
            executeCommands(commands, index+1);
        }
    }
}

function setupPage() {
    var action = $("#action-select");
    if (action.length) {
        action.selectize({
            render: {
                option: function(data, escape) {
                    return '<div class="option">' +
                            '<span class="icon"><i class="fa fa-' + escape(data.icon) + '" /> </span>' +
                            '<span class="title">' + escape(data.text) + '</span>' +
                        '</div>';
                }
            },
            onChange: function( value ) {
                if ( value ) {
                    $.ajax("/q/act", {
                        type: 'POST',
                        data: {
                            value: value
                        }
                    }).done(function( data ) {
                        executeCommands(data["commands"], 0);
                    });
                }
            }
        });
    }
    $(".player-unequip").click(function() {
        $.ajax("/q/punequip", {
            type: 'POST',
            data: {
                skill: $(this).attr("id")
            }
        }).done(function() {
            Tipped.init();
            $("#character").trigger('click');
        });
    });
    $(".player-equip").click(function() {
        $.ajax("/q/pequip", {
            type: 'POST',
            data: {
                skill: $(this).attr("id")
            }
        }).done(function() {
            Tipped.init();
            $("#character").trigger('click');
        });
    });
    Tipped.create('.inventory-item-filled', function(element) {
      return {
        title: $(element).find(".tipped-title").html(),
        content: $(element).find(".tipped-content").html()
      };
    }, {
      skin: 'light',
      //close: true,
      //hideOn: false,
    });
    Tipped.create('.skill-filled', function(element) {
      return {
        title: $(element).find(".tipped-title").html(),
        content: $(element).find(".tipped-content").html()
      };
    }, {
      skin: 'light',
      //close: true,
      //hideOn: false,
    });
}

jQuery(document).ready(function () {
    setInterval('updateClock()', 1000);

    setupPage();
    $("#central.messages").scrollTop($('#central.messages').prop("scrollHeight"));

    $("#menu").find("a").click(function () {
        var id = $(this).attr("id");
        $.ajax("/q/menu", {
            type: "GET",
            data: {
                menu: id
            }
        }).done(function (html) {
            $("#content").fadeOut(400, function () {
                $("#menu").find("a.active").each(function () {
                    $(this).removeClass("active");
                });
                $("#" + id).addClass("active");
                $("#content").html(html).fadeIn(400, function() {
                    $("#central.messages").scrollTop($('#central.messages').prop("scrollHeight"));
                });
                setupPage();
                executeLocaleAct();
            });
        });
    });

    $("#travelModalRevealer").click(function() {
        $("#travelModal").foundation('reveal', 'open');
    });
    var travel = $("#travel-select").selectize();
    $(".shoeprints").find('a').click(function() {
        $.ajax("/q/travel", {
            type: "GET",
            data: {
                key: travel[0].selectize.getValue()
            }
        }).done(function( data ) {
            $("#travelModal").foundation('reveal', 'close');
            if (data) {
                executeCommands(data["commands"], 0);
            }
        });
    });

    $.ajax("/q/start").done(function( data ) {
        if (data) {
            executeCommands(data["commands"], 0);
        }
    });
});