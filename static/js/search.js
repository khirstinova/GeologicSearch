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
                let t1 = $('#search_1').val(), t2 = $('#search_2').val(), t3 = $('#search_3').val(),
                    st = parseInt($('#proximity').val()) + 1, exp = false;
                let valid = (t1 !== '');
                if (valid)
                {
                    $('#search_1').parent().removeClass("form-input-error");
                    search.performJournalSearch(t1, t2, t3, st, exp);
                }
                else
                    $('#search_1').parent().addClass("form-input-error");
            }
        );

        $('#search_1').blur
        (
            function() {
                if ($(this).val() !== '')
                    $(this).parent().removeClass("form-input-error");
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
    }
);

var search = {

    searchUrlFormatArticle: "/search/search-ajax-article?term1=R1&term2=R2&term3=R3&st=R4&exp=R5&journal=R6",
    searchUrlFormatJournal: "/search/search-ajax-journal?term1=R1&term2=R2&term3=R3&st=R4&exp=R5",

    performJournalSearch: function(term1, term2, term3, st, expand) {
        $('.search-results-list-journals').hide();
        $('.search-results-list-articles').hide();
        $('.search-wait').show();
        $('.search-results-container').show();

        let journal_search_url =
            this.searchUrlFormatJournal
                .replace("R1", encodeURIComponent(term1))
                .replace("R2", encodeURIComponent(term2))
                .replace("R3", encodeURIComponent(term3))
                .replace("R4", encodeURIComponent(st))
                .replace("R5", encodeURIComponent(expand));

        $.ajax({
            cache: false,
            method: 'GET',
            url: journal_search_url,
            success: function(data) {
                console.log(data);
                $('#search-ajax-container').html(data);

                $('.search-results-item-journal a').click(
                    function(e) {
                        e.preventDefault();
                        search.performArticleSearchLink(this);
                    }
                );
            },
            complete: function() {
                $('.search-wait').hide();
                $('.search-results-list-journals').show();
            }
        });
    },

    performArticleSearchLink: function(a) {
        let link = $(a);
        let term1 = link.attr("data-term1"), term2 = link.attr("data-term2"),
            term3 = link.attr("data-term3"), st = link.attr("data-st"), journal = link.attr("data-journal");

        search.performArticleSearch(term1, term2, term3, st, false, journal);
    },

    performJournalSearchLink: function(a) {
        let link = $(a);
        let term1 = link.attr("data-term1"), term2 = link.attr("data-term2"),
            term3 = link.attr("data-term3"), st = link.attr("data-st");

        search.performJournalSearch(term1, term2, term3, st, false);
    },

    performArticleSearch: function(term1, term2, term3, st, expand, journal) {
        $('.search-results-list-journals').hide();
        $('.search-wait').show();

        let article_search_url =
            this.searchUrlFormatArticle
                .replace("R1", encodeURIComponent(term1))
                .replace("R2", encodeURIComponent(term2))
                .replace("R3", encodeURIComponent(term3))
                .replace("R4", encodeURIComponent(st))
                .replace("R5", encodeURIComponent(expand))
                .replace("R6", encodeURIComponent(journal));

        $.ajax({
            cache: false,
            method: 'GET',
            url: article_search_url,
            success: function(data) {
                console.log(data);
                $('#search-ajax-container').html(data);
            },
            complete: function() {
                $('.search-wait').hide();
                $('.search-results-list-articles').show();

                $('.search-back a').click(
                    function(e) {
                        e.preventDefault();
                        search.performJournalSearchLink(this);
                    }
                );
            }
        });
    }
}