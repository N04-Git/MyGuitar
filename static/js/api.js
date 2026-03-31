// API Requests
function call_api(endpoint, parameters={}) {
    return fetch('/api'+endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(parameters)
    })
    .then(response => {
        if (response.ok) { return response.json() }
        else { alert('API Error :', response) }
    })
    .then(data => { return data })
    .catch( error => { alert('API Error : ', error) })
}