function setuplogin() {
    // We set click handlers on the Login Form
    $("#sidebar").find(".login-button").click(function() {
        login();
    });
    $("#sidebar").find(".register-button").click(function() {
        loadreg();
    });
}

function loadlogin() {
    // We load the Login Form
    $.ajax("/q/logintemp", {
        type: "GET"
    }).done(function(html) {
        jQuery("#sidebar").fadeOut(1500, function() {
            var sidebar = jQuery("#sidebar");
            sidebar.html(html);
            sidebar.fadeIn(1500);
            setuplogin();
        });
    });
}

function login() {
    // Let's login
    $(".login-form").removeClass('error');
    $.ajax("/q/login", {
        type: "POST",
        data: {
            username: $("#username").find("input").val(),
            password: $.md5($("#password").find("input").val())
        }
    }).done(function() {
        location.reload();
    }).fail(function() {
        $(".login-form").addClass('error');
    });
}

function loadreg() {
    // We load the Registration Form
    $.ajax("/q/registertemp", {
        type: "GET"
    }).done(function(html) {
        jQuery("#sidebar").fadeOut(1500, function() {
            var sidebar = jQuery("#sidebar");
            sidebar.html(html);
            sidebar.fadeIn(1500);
            sidebar.find(".login-link").click(function() {
                loadlogin();
                return false;
            });
            sidebar.find(".button").click(function() {
                continuereg();
            });
        });
    });
}

function continuereg() {
    jQuery("#sidebar").find(".error").remove();
    $.ajax("/q/register", {
        type: "POST",
        data: {
            username: $("#username").find("input").val(),
            password: $.md5($("password").find("input").val())
        }
    }).done(function(html) {
        jQuery("#sidebar").fadeOut(1500, function() {
            var sidebar = jQuery("#sidebar");
            sidebar.html(html);
            sidebar.fadeIn(1500);
            sidebar.find(".login-link").click(function() {
               loadlogin();
            });
            sidebar.find("#finish").click(function() {
                $.ajax('/q/registerfin', {
                    type: "POST",
                    data: {
                        user: $("#user").val(),
                        name: $("#name").val(),
                        sesskey: $("#sesskey").val(),
                        cclass: $("#class").find(":selected").val()
                    }
                }).done(function() {
                    location.reload();
                });
            });
        });
    }).fail(function(xhr) {
        if (xhr.status == 403) {
            jQuery("#sidebar").find("#username").append('<small class="error">User already exists</small>');
        } else {
            jQuery("#sidebar").find("#username").append('<small class="error">Server error</small>');
        }
    });
}

function unhide() {
	jQuery("#logo").fadeIn(3000);
	jQuery("#sidebar").fadeIn(3000);
}

jQuery(document).ready(function () {
	// We use a framework called Tubular to show a YouTube video in the background
	// Let's show that video
	var options = { videoId: 'P99yh7DdFR4', mute: false };
	$('#wrapper').tubular(options);

	// Now we want the UI elements to unhide after 5 seconds. Go!
	setTimeout(function(){ unhide(); }, 5000);

    // We want to set click handlers on various elements
    setuplogin();
});