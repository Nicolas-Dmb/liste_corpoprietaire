//verifie si on affiche ou non le questions sur les adresses en fonction de la demande de l'user 
let adresses_copro = document.getElementById("adresses_copro")


let oui_copro = document.getElementById("Oui_RP")
oui_copro.addEventListener("change", () => {
    adresses_copro.classList.remove("adresses_copro");
    adresses_copro.classList.add("adresses_copro.active");
    console.log("on active")
})

let non_copro = document.getElementById("Non_RP")
non_copro.addEventListener("change", () => {
    adresses_copro.classList.remove("adresses_copro.active");
    adresses_copro.classList.add("adresses_copro");
    console.log("on desactive")
})