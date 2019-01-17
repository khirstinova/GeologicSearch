$(document).ready(
    function() {
        $('button[data-next]').click(
            function (e)
            {
                e.preventDefault();
                let n = $(this).attr('data-next');
                let classname = '.search_' + n;
                $(classname).show();
            }
        );
    }
);