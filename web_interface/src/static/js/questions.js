const inputs  = document.getElementsByTagName("input")
console.log(inputs[0])
for (let i = 0; i < inputs.length - 1; i++) {
    console.log(i, inputs[i].name)
    inputs[i].required = true;
    //inputs[i].setCustomValidity("Bitte wählen Sie eine der folgenden Optionen");
}
