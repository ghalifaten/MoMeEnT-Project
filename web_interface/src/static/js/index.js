window.localStorage.clear()
const qualtrics_data = JSON.parse(document.getElementById("qualtrics_data").innerHTML)
window.localStorage.setItem("qualtrics_data", JSON.stringify(qualtrics_data));