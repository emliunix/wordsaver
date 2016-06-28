(function(global) {
    document.addEventListener("focus", (ev) => {
        if(ev.target.classList.contains("text-input")) {
            ev.target.classList.add("text-input-focused")
        }
    }, {
        "capture": true,
        "passive": true
    })

    document.addEventListener("blur", (ev) => {
        if(ev.target.classList.contains("text-input")) {
            ev.target.classList.remove("text-input-focused")
        }
    }, {
        "capture": true,
        "passive": true
    })
})(this);
