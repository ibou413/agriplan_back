from parcelle.models import Culture, Variete, EtapeCulture, ProduitPhytosanitaire, Fertilisation, TraitementPhytosanitaire

# --- 1. Culture Patate douce ---
patate_douce = Culture.objects.create(
    nom="Patate douce",
    description="Plante vivace cultivée annuellement pour ses tubercules et ses feuilles comestibles. Très répandue à Madagascar, elle joue un rôle clé dans la sécurité alimentaire.",
    cycle_min=90,
    cycle_max=180,
    rendement_min_t_ha=4,
    rendement_max_t_ha=35,
    type_culture="conventionnelle",
    saisonnalite="Novembre à Mai selon les régions"
)

# --- 2. Variétés de Patate douce ---
Variete.objects.bulk_create([
    Variete(culture=patate_douce, nom="Mahafaly"),
    Variete(culture=patate_douce, nom="Naveto"),
    Variete(culture=patate_douce, nom="Mahasoa"),
    Variete(culture=patate_douce, nom="Ravo"),
    Variete(culture=patate_douce, nom="Mafotra"),
    Variete(culture=patate_douce, nom="Mavo"),
    Variete(culture=patate_douce, nom="Riba"),
    Variete(culture=patate_douce, nom="Mendrika"),
    Variete(culture=patate_douce, nom="Bôra"),
    Variete(culture=patate_douce, nom="Mevakely"),
])

# --- 3. Étapes culturales ---
EtapeCulture.objects.bulk_create([
    EtapeCulture(
        culture=patate_douce,
        nom="Préparation du sol",
        description="Labour à 20-25 cm, ameublissement, drainage sur rizière, fosses ou billons selon le type de sol.",
        frequence="Avant plantation",
        delai_apres_plantation=0
    ),
    EtapeCulture(
        culture=patate_douce,
        nom="Plantation",
        description="Boutures de 25-30 cm, 3-4 nœuds, densité de 47 330 à 70 000 boutures/ha selon mode de plantation.",
        frequence="Unique",
        delai_apres_plantation=0
    ),
    EtapeCulture(
        culture=patate_douce,
        nom="Entretien",
        description="Sarclage, buttage à 45 jours, lutte biologique contre insectes (neem, pyrèthre, voandelaka).",
        frequence="Périodique",
        delai_apres_plantation=45
    ),
    EtapeCulture(
        culture=patate_douce,
        nom="Récolte",
        description="Récolte manuelle entre 3 à 6 mois selon variété et altitude. Tubercules récoltés à maturité.",
        frequence="Unique",
        delai_apres_plantation=90
    ),
])

# --- 4. Produits phytosanitaires ---
ProduitPhytosanitaire.objects.bulk_create([
    ProduitPhytosanitaire(nom_commercial="Neem", matiere_active="Extrait de neem", type_produit="insecticide biologique"),
    ProduitPhytosanitaire(nom_commercial="Pyrèthre", matiere_active="Extrait de fleurs de pyrèthre", type_produit="insecticide biologique"),
    ProduitPhytosanitaire(nom_commercial="Voandelaka", matiere_active="Melia azedarach", type_produit="insecticide biologique"),
])

# --- 5. Fertilisation ---
variete_patate = Variete.objects.get(nom="Mahafaly")
Fertilisation.objects.create(
    variete=variete_patate,
    jour=0,
    type_engrais="Fumier de ferme",
    dose_ha="10 à 20 T/ha",
    mode_application="Épandage localisé ou à la volée lors de la plantation"
)

# --- 6. Traitement phytosanitaire ---
TraitementPhytosanitaire.objects.bulk_create([
    TraitementPhytosanitaire(
        variete=variete_patate,
        jour=30,
        type_traitement="Préventif",
        cible="Charançons, apions, chenilles, cassides",
        produit=ProduitPhytosanitaire.objects.get(nom_commercial="Neem"),
        matiere_active="Extrait de neem"
    ),
    TraitementPhytosanitaire(
        variete=variete_patate,
        jour=45,
        type_traitement="Curatif",
        cible="Alternariose, flétrissement fusarien",
        produit=ProduitPhytosanitaire.objects.get(nom_commercial="Pyrèthre"),
        matiere_active="Extrait de fleurs de pyrèthre"
    ),
])
