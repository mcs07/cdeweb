$(function() {

    function getResults() {
        if ($('.progress').length > 0) {
            $.get('/api/job/' + jobId, function(data) {
                console.log(data);
                if (data.status == 'SUCCESS') {
                    window.location.reload();
                } else {
                    setTimeout(function () {
                        getResults();
                    }, 1000);
                }
            });
        }
    }

    // Poll to check if job has completed
    getResults();

});
