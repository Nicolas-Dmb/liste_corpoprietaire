//vérifier la validité du mot de passe et que la confirmation MP est similaire 
let MP = document.getElementById("password")
let MPconf = document.getElementById("password2")
let form = document.querySelector(".newAccount")


    //verif MP 
MP.addEventListener("input", () => {

    //on vérifie que le mot de passe respecte les critères 
    verifMP(MP)

    //lancement de same 
    sameMP(MP, MPconf)
});

    //verif que se sont les mm MP 
MPconf.addEventListener("input", () => {

        //on vérifie que le mot de passe respecte les critères 
        sameMP(MP, MPconf)
});

    //On vérifie avant de valider le formulaire 
form.addEventListener("submit", (event)=> {
    // On empêche le comportement par défaut
    event.preventDefault();

    let verif = verifMP(MP)
    let same = sameMP(MP, MPconf)

    if (verif===true){
        if (same === true){
            form.submit(); 
        }else{
            alert("le mot de passe de confirmation n'est pas bon")
        }
    }else{
        alert("le mot de passe ne respect pas les critères de sécurité")
    }
})

function verifMP(MP){
let valeurMP = MP.value;
let caractere = document.querySelector(".caractere")
let lettre = document.querySelector(".lettre")
let chiffre = document.querySelector(".chiffre")
let taille = document.querySelector(".taille")
let A = 0;
    if(valeurMP.length >= 8){
        taille.classList.add("ok")
        A+=1;
    }else{
        if (taille.classList.contains("ok")){
            taille.classList.remove("ok")
        }
    }
    if(/[0-9]{1}/.test(valeurMP)){
        chiffre.classList.add("ok")
        A+=1;
    }else{
        if (chiffre.classList.contains("ok")){
            chiffre.classList.remove("ok")
        }
    }
    if(/[a-zA-Z]{1}/.test(valeurMP)){
        lettre.classList.add("ok")
        A+=1;
    }else{
        if (lettre.classList.contains("ok")){
            lettre.classList.remove("ok")
        }
    }
    if(/[^A-Za-z0-9]{1}/.test(valeurMP)){
        caractere.classList.add("ok")
        A+=1;
    }else{
        if (caractere.classList.contains("ok")){
            caractere.classList.remove("ok")
        }
    }
    if (A===4){
        return true; 
    }else{
        return false;
    }
}

function sameMP(MP, MPconf){
    let valeurMP = MP.value;
    let valeurMPconf = MPconf.value
    let same = document.querySelector(".same")
    console.log(valeurMP)
    console.log(valeurMPconf)
    if(valeurMP === valeurMPconf){
        same.classList.add("ok")
        return true; 
    }else{
        if (same.classList.contains("ok")){
            same.classList.remove("ok")
        }
        return false;
    }
}