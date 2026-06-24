const selectRegion = document.getElementById("region");

// Supprimer l'option dont le texte est "FRANCE"
for (const option of selectRegion.options) {
    if (option.textContent.trim().toUpperCase() === "FRANCE") {
        option.remove();
        break;
    }
}

document.getElementById("region").addEventListener("change", async (e) => {
    const regionId = e.target.value;
    const selectDept = document.getElementById("departement");

    // Vider la liste
    selectDept.innerHTML = '<option value="">Choisir</option>';

    if (!regionId) return;

    // Appel AJAX (window.APP_BASE = préfixe de l'app en prod, vide en local)
    const response = await fetch(`${window.APP_BASE || ""}/api/departements/${regionId}`);
    const depts = await response.json();

    // Remplir la liste
    for (const dept of depts) {
        const opt = document.createElement("option");
        opt.value = dept.id;
        opt.textContent = `${dept.code} – ${dept.libelle}`;
        selectDept.appendChild(opt);
    }
});