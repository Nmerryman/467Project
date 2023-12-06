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


function add_bracket() {
    const desc = document.getElementById('name').value;
    const min_weight = document.getElementById('min_weight').value;
    const max_weight = document.getElementById('max_weight').value;
    const weight_m = document.getElementById('weight_m').value;
    const weight_b = document.getElementById('weight_b').value;

    fetcher('api/add_bracket', 'dummy', [desc, min_weight, max_weight, weight_m, weight_b], () => {
        console.log('Bracket added');
        load_brackets();
    });
}

