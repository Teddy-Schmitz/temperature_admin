$(function () {
    $('#users').addClass('active');

    $('#deleteModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var user = button.data('user'); // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var modal = $(this);
        modal.find('.modal-title').text('Delete ' + user);

        modal.find('#deleteButton').click(function (e) {
            modal.modal('toggle');
            $.get('/users/delete/'+user, function(e){
                location.reload(true);
            }).fail(function(e){
                failureAlert("Something went wrong :(");
            });
        });
    });

    $('#modifyModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var user = button.data('user');// Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var modal = $(this);
        if (user) {
            modal.find('#username').val(user).prop('disabled', true);
            modal.find('.modal-title').text('Modify User');
            modal.find('#submitButton').click(function (e) {
                var o = {password: modal.find('#password').val()};
                var url = "/users/".concat(user);
                modal.modal('toggle');
                $.post(
                    url,
                    o,
                    function (e) {
                        successAlert("User modified");
                    }
                ).fail(function (e) {
                        failureAlert("Something went wrong :(");
                    });
            });
        }
        else {
            modal.find('#submitButton').click(function (e) {
                var d = {username: modal.find('#username').val(),
                    password: modal.find('#password').val()};
                modal.modal('toggle');
                $.post('/users/create', d, function(e){
                    location.reload(true);
                }).fail(function(e){
                    failureAlert("Something went wrong :(");
                });
            });
        }
    });

    $('#modifyModal').on('hide.bs.modal', function (event) {
        var modal = $(this);
        modal.find('#username').val('').prop('disabled', false);
        modal.find('.modal-title').text('Add New User');
        modal.find('#submitButton').off()
    });

    function successAlert(message) {
        $('#alert-placeholder').html(
            '<div id="alert" class="alert alert-success alert-dismissable"> <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button> <h4 id="alertHeader"><i class="icon fa fa-check"></i> Success!</h4> <span>' + message + '</span>');
    }
    function failureAlert(message) {
        $('#alert-placeholder').html('<div id="alert" class="alert alert-danger alert-dismissable"> <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button> <h4 id="alertHeader"><i class="icon fa fa-ban"></i> Failure!</h4> <span id="alertText">' + message + '</span>');
    }
});
