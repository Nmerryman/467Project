
function load_brackets() {
    fetcher('api/load_brackets', 'container', [], () => {
        console.log('Page updated with brackets');
    });
}


function remove_bracket(bracket_id) {
    fetcher('api/remove_bracket/' + bracket_id, 'dummy', [], () => {
        console.log('Bracket removed');
        load_brackets();
    });
}

