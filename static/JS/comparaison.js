function retirerOptionFrance(selectRegion) {
    for (const option of Array.from(selectRegion.options)) {
        if (option.textContent.trim().toUpperCase() === "FRANCE") {
            option.remove();
            break;
        }
    }
}

async function chargerDepartements(selectRegion) {
    const regionId = selectRegion.value;
    const selectDept = document.getElementById(selectRegion.dataset.departementSelect);

    selectDept.innerHTML = '<option value="">Choisir</option>';

    if (!regionId) return;

    const response = await fetch(`${window.APP_BASE || ""}/api/departements/${regionId}`);
    const departements = await response.json();

    for (const dept of departements) {
        const option = document.createElement("option");
        option.value = dept.id;
        option.textContent = `${dept.code} – ${dept.libelle}`;
        selectDept.appendChild(option);
    }
}

for (const selectRegion of document.querySelectorAll("[data-departement-select]")) {
    retirerOptionFrance(selectRegion);
    selectRegion.addEventListener("change", () => chargerDepartements(selectRegion));
}

if (typeof Chart !== "undefined" && typeof comparaisonEvolution !== "undefined") {
    const canvasComparaison = document.getElementById("graphique-comparaison");
    const annees = Array.from(new Set([
        ...comparaisonEvolution.dept1.donnees.map((ligne) => ligne.annee),
        ...comparaisonEvolution.dept2.donnees.map((ligne) => ligne.annee),
    ])).sort((a, b) => a - b);

    function valeursParAnnee(donnees) {
        return annees.map((annee) => {
            const ligne = donnees.find((item) => item.annee === annee);
            return ligne ? ligne.effectif : null;
        });
    }

    new Chart(canvasComparaison, {
        type: "line",
        data: {
            labels: annees,
            datasets: [
                {
                    label: comparaisonEvolution.dept1.nom,
                    data: valeursParAnnee(comparaisonEvolution.dept1.donnees),
                    borderColor: "#0474ba",
                    backgroundColor: "rgba(4, 116, 186, 0.12)",
                    tension: 0.2,
                },
                {
                    label: comparaisonEvolution.dept2.nom,
                    data: valeursParAnnee(comparaisonEvolution.dept2.donnees),
                    borderColor: "#f17720",
                    backgroundColor: "rgba(241, 119, 32, 0.12)",
                    tension: 0.2,
                },
            ],
        },
    });
}
