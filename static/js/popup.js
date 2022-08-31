'use strict';
console.log("in");
const popover = document.querySelectorAll('.popover');
const openBtn = document.querySelectorAll('.mt-7');
const text = document.querySelectorAll('.modal-text');
// const closeBtn = document.querySelectorAll('.close');
function btnPressed(e) {
    const parent = e.target.parentNode;
    const sibling = parent.nextElementSibling;
    if (sibling.classList.contains('popover')) {
        // sibling.classList.toggle('hidden');
        const pText=sibling.lastElementChild.lastElementChild;
        alert(pText.innerHTML)
    }
}
//on click
openBtn.forEach(btn => {
    //console.log(btn)
    btn.addEventListener('click', function (e) {
        btnPressed(e)
    })
})