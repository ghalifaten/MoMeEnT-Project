const inputs  = document.getElementsByTagName("input")
console.log(inputs[0])
console.log(inputs[1])
for (let i = 0; i < inputs.length - 1; i++) {
    inputs[i].required = true;
}


