$(document).ready(function() {
    function fetchAndDisplayGrades() {
        $.ajax({
            url: "/get_grades",  // Replace with your actual endpoint
            type: 'GET',
            success: function(response) {
                var grades = response.data;
                var groupedGrades = groupGradesBySemester(grades);
                displayGroupedGrades(groupedGrades);
            },
            error: function(xhr, status, error) {
                console.error('An error occurred while fetching grades:', error);
                showFlashMessage('error', 'Failed to fetch grades. Please try again.');
            }
        });
    }

    function fetchAndDisplayNotifications() {
        $.ajax({
            url: "/get_notifications",  // Replace with your actual endpoint
            type: 'GET',
            success: function(response) {
                displayLatestNotification(response.notification);
            },
            error: function(xhr, status, error) {
                console.error('An error occurred while fetching notifications:', error);
                showFlashMessage('error', 'Failed to fetch notifications. Please try again.');
            }
        });
    }

    function groupGradesBySemester(grades) {
        var grouped = {};
        grades.forEach(function(grade) {
            if (!grouped[grade.semester]) {
                grouped[grade.semester] = [];
            }
            grouped[grade.semester].push(grade);
        });
        return grouped;
    }

    function displayGroupedGrades(groupedGrades) {
        var container = $('#grades-container');
        container.empty();

        Object.keys(groupedGrades).sort().reverse().forEach(function(semester) {
            var button = $('<button class="semester-button"><i class="bx bx-calendar"></i> ' + semester + '</button>');
            button.data('semester', semester);
            container.append(button);
        });
    }

    function displayLatestNotification(notification) {
        var content = $('#latestNotification');
        content.empty();
        
        if (notification) {
            content.html('<div class="notification" data-id="' + notification.id + '">' + notification.message + '</div>');
        } else {
            content.html('<div class="notification">No new notifications</div>');
        }
    }

    $('#grades-container').on('click', '.semester-button', function() {
        var semester = $(this).data('semester');
        window.location.href = "/semester_grades?semester=" + encodeURIComponent(semester);
    });

    $('#darkModeToggle').click(function() {
        $('body').toggleClass('dark-mode');
        if ($('body').hasClass('dark-mode')) {
            $(this).html('<i class="bx bx-sun"></i>');
        } else {
            $(this).html('<i class="bx bx-moon"></i>');
        }
    });

    $('#notificationToggle').click(function() {
        $('#notificationPanel').toggle();
        if ($('#notificationPanel').is(':visible')) {
            fetchAndDisplayNotifications();
        }
    });

    $('#latestNotification').on('click', '.notification', function() {
        var notificationId = $(this).data('id');
        $.ajax({
            url: "/mark_grade_notified",  // Replace with your actual endpoint
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({grade_id: notificationId}),
            success: function(response) {
                if (response.success) {
                    fetchAndDisplayNotifications();
                }
            },
            error: function(xhr, status, error) {
                console.error('Error marking notification as read:', error);
                showFlashMessage('error', 'Failed to mark notification as read. Please try again.');
            }
        });
    });

    $('#calculatorForm').submit(function(e) {
        e.preventDefault();
        var currentGrade = parseFloat($('#currentGrade').val());
        var desiredGrade = parseFloat($('#desiredGrade').val());
        var remainingWeight = parseFloat($('#remainingWeight').val()) / 100;

        if (isNaN(currentGrade) || isNaN(desiredGrade) || isNaN(remainingWeight)) {
            $('#calculationResult').text('Please enter valid numbers');
            return;
        }

        var requiredGrade = (desiredGrade - currentGrade * (1 - remainingWeight)) / remainingWeight;
        $('#calculationResult').text('You need to score ' + requiredGrade.toFixed(2) + '% on the remaining assessments to achieve your desired grade.');
    });

    function showFlashMessage(type, message) {
        var alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        var flashMessage = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                             message +
                             '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                             '<span aria-hidden="true">&times;</span></button></div>');
        $('.container').prepend(flashMessage);
        setTimeout(function() {
            flashMessage.alert('close');
        }, 5000);
    }

    fetchAndDisplayGrades();

    // Periodically check for new notifications only when the panel is visible
    setInterval(function() {
        if ($('#notificationPanel').is(':visible')) {
            fetchAndDisplayNotifications();
        }
    }, 60000); // Check every minute
});