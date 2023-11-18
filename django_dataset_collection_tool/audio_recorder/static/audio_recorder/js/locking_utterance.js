function releaseLock() {
    $.ajax({
        url: "{% url 'release_lock' %}",
        method: "POST",
        data: {
            utterance_id: "{{ object.id }}",
            csrfmiddlewaretoken: "{{ csrf_token }}"
        }
    });
}

$(window).on('beforeunload', function() {
    releaseLock();
});

TimeMe.initialize({
    currentPageName: "{% url 'utterance-detail' pk=object.pk %}", // replace 'your_view_name' with your Django view name and 'object' with your context object
    idleTimeoutInSeconds: 30 // time before user considered idle
});