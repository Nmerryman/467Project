
function handleSearch(event) {
  var query = event.target.value;

  // Featch search results and update the page
  fetcher('search','container', [query], function() {
     // This callback function will be called after the page is updated
     console.log('Page updated with search results for query:', query);
  });
  // TODO: Use the query to search your data and update the page
  console.log('Search query:', query);
}