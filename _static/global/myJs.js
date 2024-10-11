function show_text(id) {
    id.style.transition = "opacity 1.6s";
    id.style.display= 'block';
};

function hide(elemid) {
    var div = document.getElementById(elemid);
    div.style.display = 'none';
};

function button_click(buttonid, paragraphid) {
    console.log(buttonid)
    hide(buttonid.id);
    show_text(paragraphid);
};


function buttonAppear() {
    { $('#next').show(); }
};

