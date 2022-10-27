const menu = document.querySelector('#mobile-menu')
const menuLinks = document.querySelector('.navbar__menu')

//Display mobile menu
const mobileMenu = () => {
    //toggle means active or inactive
    menu.classList.toggle('is-active')
    menuLinks.classList.toggle('active')
}

//event listener to toggle the above elements
menu.addEventListener('click', mobileMenu)

function popupFunctionExp1() {
    var popup = document.getElementById("popupExp1");
    popup.classList.toggle("show");
  }
function popupFunctionExp2() {
    var popup = document.getElementById("popupExp2");
    popup.classList.toggle("show");
    }
function popupFunctionExp3() {
    var popup = document.getElementById("popupExp3");
    popup.classList.toggle("show");
    }
function popupFunctionExp4() {
    var popup = document.getElementById("popupExp4");
    popup.classList.toggle("show");
    }