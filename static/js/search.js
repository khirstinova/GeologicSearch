$(document).ready(
    function() {
        $('button[data-next]').click(
            function (e)
            {
                e.preventDefault();
                let n = $(this).attr('data-next');
                let classname = '.search_' + n;
                $(classname).show();
                $(this).prop("disabled", true);
                $(this).siblings('.close').hide();
            }
        );

        $('#search-btn').click
        (
            function(e) {
                e.preventDefault();
                $('.search-results-list-journals').hide();
                $('.search-results-list-articles').hide();
                $('.search-wait').show();
                $('.search-results-container').show();
                setTimeout(function () {
                    $('.search-wait').hide();
                    $('.search-results-list-journals').show();
                }, 5000);
            }
        );

        $('.close').click(function() {
            let p = $(this).parent();
            $(this).siblings('input').val('');
            let number = p.attr('class').replace("search_", "");
            $('button[data-next=' + number + ']').prop("disabled", false);
            $('.search_' + (number - 1)).find('.close').show();
            p.hide();
        });

        $('.search-results-item-journal a').click(function() {
            $('.search-results-list-journals').hide();
            $('.search-results-list-articles').show();
        });
    }
);