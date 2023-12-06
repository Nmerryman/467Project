
function toggle_children(order_id) {
    const element = document.getElementById(order_id);
    for (const child of element.children) {
        if (child.classList.contains("order_items")) {
            if (child.style.display === "none") {
                child.style.display = "";
            } else {
                child.style.display = "none";
            }
        }
    }
    console.log("Folded: " + order_id);
}

function update_order_status(id, status) {
    let xhttp = new XMLHttpRequest();
    let url = "api/update_order/" + id + "/" + status;
    xhttp.open("GET", url);
    xhttp.onload = () => {
        console.log("loaded response");
        location.reload();
    };
    xhttp.send();
    console.log("Sent: " + status + " to " + id);
}
