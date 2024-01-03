// verifie si il veut les colonnes ou pas pour nous afficher ou non les éléments. 

// verifie si on affiche ou non le dépot d'un fichier liste_lot : 
let file_lot = document.getElementById("file_lot")

let Oui_lot = document.getElementById("Oui_lot")
Oui_lot.addEventListener("change", () => {
    file_lot.classList.remove("file_lot");
    file_lot.classList.add("file_lot.active");
})

let Non_lot = document.getElementById("Non_lot")
Non_lot.addEventListener("change", () => {
    file_lot.classList.remove("file_lot.active");
    file_lot.classList.add("file_lot");
})
