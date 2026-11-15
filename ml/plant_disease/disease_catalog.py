"""
KrishiVision AI - Plant Disease Knowledge Base & Treatment Encyclopedia
========================================================================
Comprehensive agronomic data covering 27 PlantVillage disease classes across
6 major crop species: Tomato, Potato, Corn (Maize), Apple, Grape, and Bell Pepper.
"""

DISEASE_CATALOG = {
    # -------------------------------------------------------------------------
    # TOMATO (10 classes)
    # -------------------------------------------------------------------------
    "Tomato___Bacterial_spot": {
        "class_id": "Tomato___Bacterial_spot",
        "plant_name": "Tomato",
        "disease_name": "Bacterial Spot",
        "pathogen_type": "Bacterial (Xanthomonas spp.)",
        "severity": "Moderate to High",
        "is_healthy": False,
        "symptoms": (
            "Small, dark, water-soaked circular spots (<3mm) on leaves that later turn brown "
            "with yellow halos. Severely infected leaves turn yellow and drop prematurely. "
            "Raised scab-like blemishes may develop on green tomato fruit."
        ),
        "treatments": {
            "organic": "Apply copper octanoate (copper soap) or Bacillus subtilis bio-fungicide sprays at early onset.",
            "chemical": "Fixed copper bactericide (copper hydroxide) combined with Mancozeb spray every 7–10 days.",
            "cultural": "Avoid overhead watering; use drip irrigation. Rotate away from solanaceous crops for 2 years. Destroy infected crop residue."
        }
    },
    "Tomato___Early_blight": {
        "class_id": "Tomato___Early_blight",
        "plant_name": "Tomato",
        "disease_name": "Early Blight",
        "pathogen_type": "Fungal (Alternaria solani)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Concentric ring dark brown spots ('target board' appearance) on older lower leaves. "
            "Yellowing around the lesions, progressing to extensive foliar defoliation and stem collar rot."
        ),
        "treatments": {
            "organic": "Neem oil foliar spray (0.5%), copper sulfate, or Trichoderma viride soil application.",
            "chemical": "Chlorothalonil, Mancozeb 75% WP (2 g/L), or Azoxystrobin applied every 7–10 days during humid weather.",
            "cultural": "Mulch soil around plants to prevent fungal spore splashback. Prune bottom leaves 30 cm from ground."
        }
    },
    "Tomato___Late_blight": {
        "class_id": "Tomato___Late_blight",
        "plant_name": "Tomato",
        "disease_name": "Late Blight",
        "pathogen_type": "Oomycete / Water Mold (Phytophthora infestans)",
        "severity": "Critical / Severe",
        "is_healthy": False,
        "symptoms": (
            "Large, irregularly shaped greasy water-soaked gray-green lesions on leaves and stems. "
            "Under humid conditions, a delicate white fuzzy mold appears on the leaf underside. "
            "Can destroy entire crop within days in cool, wet weather."
        ),
        "treatments": {
            "organic": "Preventive copper-based sprays; bio-fungicides containing Bacillus amyloliquefaciens.",
            "chemical": "Systemic fungicides: Metalaxyl + Mancozeb (Ridomil MZ), Cymoxanil, or Dimethomorph.",
            "cultural": "Immediately rogue and bag infected plants; do not compost. Provide wide row spacing for air circulation."
        }
    },
    "Tomato___Leaf_Mold": {
        "class_id": "Tomato___Leaf_Mold",
        "plant_name": "Tomato",
        "disease_name": "Leaf Mold",
        "pathogen_type": "Fungal (Passalora fulva)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Pale greenish-yellow indistinct spots on upper leaf surfaces, with olive-green to grayish-purple "
            "velvety fungal growth on the corresponding undersides. Prevalent in greenhouse/high humidity conditions."
        ),
        "treatments": {
            "organic": "Potassium bicarbonate spray or sulfur-based organic dusts.",
            "chemical": "Chlorothalonil, Difenoconazole, or Mancozeb sprays.",
            "cultural": "Ventilate greenhouses; maintain relative humidity below 85%. Avoid wetting leaves."
        }
    },
    "Tomato___Septoria_leaf_spot": {
        "class_id": "Tomato___Septoria_leaf_spot",
        "plant_name": "Tomato",
        "disease_name": "Septoria Leaf Spot",
        "pathogen_type": "Fungal (Septoria lycopersici)",
        "severity": "Moderate to High",
        "is_healthy": False,
        "symptoms": (
            "Numerous small circular spots (1.5–3 mm) with dark brown margins and sunken grayish-white centers. "
            "Tiny black specks (pycnidia) visible inside older lesions under magnification."
        ),
        "treatments": {
            "organic": "Liquid copper fungicides and bio-stimulants that increase plant immunity.",
            "chemical": "Chlorothalonil, Mancozeb, or Azoxystrobin applications on a 7-day schedule.",
            "cultural": "Strip lower infected foliage; stake tomato vines; eliminate solanaceous weed hosts."
        }
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "class_id": "Tomato___Spider_mites Two-spotted_spider_mite",
        "plant_name": "Tomato",
        "disease_name": "Two-Spotted Spider Mites",
        "pathogen_type": "Pest / Arachnid (Tetranychus urticae)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Fine yellow stippling (pinpoint dots) on leaf surfaces, followed by bronzing and drying. "
            "Delicate fine webbing visible on leaf undersides and terminal leaf clusters in hot, dry conditions."
        ),
        "treatments": {
            "organic": "Release predatory mites (Phytoseiulus persimilis), spray insecticidal potassium soap or horticultural neem oil.",
            "chemical": "Acaricides/miticides such as Abamectin, Spiromesifen, or Propargite.",
            "cultural": "Maintain adequate soil moisture; overhead misting can temporarily discourage mite population explosion."
        }
    },
    "Tomato___Target_Spot": {
        "class_id": "Tomato___Target_Spot",
        "plant_name": "Tomato",
        "disease_name": "Target Spot",
        "pathogen_type": "Fungal (Corynespora cassiicola)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Brown lesions with light brown centers and darker concentric rings on foliage. "
            "Lesions expand rapidly under warm, humid conditions causing severe defoliation."
        ),
        "treatments": {
            "organic": "Preventive copper soap sprays and certified organic biological foliar sprays.",
            "chemical": "Azoxystrobin, Pyraclostrobin, or Boscalid fungicides.",
            "cultural": "Avoid dense canopies, prune suckers, and provide full sunlight and drip irrigation."
        }
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "class_id": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "plant_name": "Tomato",
        "disease_name": "Yellow Leaf Curl Virus (TYLCV)",
        "pathogen_type": "Viral (Begomovirus - Whitefly vectored)",
        "severity": "Critical / Severe",
        "is_healthy": False,
        "symptoms": (
            "Severe stunting of tomato plants, pronounced upward curling and cupping of leaflets, "
            "chlorotic yellow leaf margins, and drastic drop in fruit yield and blossoming."
        ),
        "treatments": {
            "organic": "Spray neem seed kernel extract (NSKE 5%) or mineral oils to suppress whitefly vectors.",
            "chemical": "Target vector whiteflies (Bemisia tabaci) with systemic insecticides: Imidacloprid, Acetamiprid, or Thiamethoxam.",
            "cultural": "Install yellow sticky traps (15–20 per acre), use 40-mesh insect netting in nurseries, rogue infected plants early."
        }
    },
    "Tomato___Tomato_mosaic_virus": {
        "class_id": "Tomato___Tomato_mosaic_virus",
        "plant_name": "Tomato",
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "pathogen_type": "Viral (Tobamovirus - Mechanically transmitted)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Mottled light and dark green mosaic patterns on leaves, distortion or 'fern-like' narrowing "
            "of leaf blades, internal brown browning of fruit tissue."
        ),
        "treatments": {
            "organic": "No curative chemical; treat seeds with 10% trisodium phosphate (TSP) solution.",
            "chemical": "No chemical control for plant viruses once established.",
            "cultural": "Wash tools and hands with 20% nonfat dry milk or detergent before handling plants. Avoid tobacco use near crops."
        }
    },
    "Tomato___healthy": {
        "class_id": "Tomato___healthy",
        "plant_name": "Tomato",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Leaf tissue is deep green, uniform, turgid, and completely free of spots, chlorosis, or necrotic margins.",
        "treatments": {
            "organic": "Continue balanced vermicompost and compost tea applications.",
            "chemical": "No fungicides or chemicals needed.",
            "cultural": "Maintain regular watering and scouting schedule to sustain optimum vigor."
        }
    },

    # -------------------------------------------------------------------------
    # POTATO (3 classes)
    # -------------------------------------------------------------------------
    "Potato___Early_blight": {
        "class_id": "Potato___Early_blight",
        "plant_name": "Potato",
        "disease_name": "Early Blight",
        "pathogen_type": "Fungal (Alternaria solani)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Dark brown to black lesions with concentric rings on older potato leaves. "
            "Surrounding tissue turns chlorotic; leaves dry up and droop along the stem."
        ),
        "treatments": {
            "organic": "Foliar application of copper oxychloride or bio-control agents (Trichoderma harzianum).",
            "chemical": "Mancozeb 75% WP (2.5 g/L) or Propineb or Difenoconazole sprays.",
            "cultural": "Ensure adequate nitrogen and potassium fertility; plant certified disease-free seed tubers."
        }
    },
    "Potato___Late_blight": {
        "class_id": "Potato___Late_blight",
        "plant_name": "Potato",
        "disease_name": "Late Blight",
        "pathogen_type": "Oomycete (Phytophthora infestans)",
        "severity": "Critical / Severe",
        "is_healthy": False,
        "symptoms": (
            "Water-soaked dark lesions at leaf tips and margins; lesions rapidly turn brown-black and rot. "
            "Faint white fungal mildew ring on leaf undersides in morning dew. Causes tuber dry rot."
        ),
        "treatments": {
            "organic": "Preventive copper hydroxide sprays; plant resistant potato cultivars (e.g., Kufri Girdhari, Kufri Himalini).",
            "chemical": "Curative spray of Metalaxyl + Mancozeb (2.5 g/L) or Cymoxanil + Mancozeb at first symptom sighting.",
            "cultural": "Proper earthing-up (hilling) to shield tubers from washing spores; destroy cull piles immediately."
        }
    },
    "Potato___healthy": {
        "class_id": "Potato___healthy",
        "plant_name": "Potato",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Healthy, vigorous green foliage with no discoloration, necrosis, or foliar distortion.",
        "treatments": {
            "organic": "Maintain organic soil matter and balanced potassium nutrition.",
            "chemical": "No chemical intervention needed.",
            "cultural": "Continue standard hilling-up and crop scouting."
        }
    },

    # -------------------------------------------------------------------------
    # CORN / MAIZE (4 classes)
    # -------------------------------------------------------------------------
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "class_id": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "plant_name": "Corn (Maize)",
        "disease_name": "Cercospora Gray Leaf Spot",
        "pathogen_type": "Fungal (Cercospora zeae-maydis)",
        "severity": "Moderate to High",
        "is_healthy": False,
        "symptoms": (
            "Distinct rectangular, tan-to-gray lesions running strictly parallel between leaf veins. "
            "Lesions coalesce to form extensive blighted areas during warm, overcast, humid periods."
        ),
        "treatments": {
            "organic": "Crop rotation and bio-fungicides; incorporation of crop residue post-harvest.",
            "chemical": "Pyraclostrobin + Fluxapyroxad, or Azoxystrobin + Propiconazole at tassel stage.",
            "cultural": "Rotate with soybeans or non-host legumes; plant hybrids with strong genetic tolerance."
        }
    },
    "Corn_(maize)___Common_rust_": {
        "class_id": "Corn_(maize)___Common_rust_",
        "plant_name": "Corn (Maize)",
        "disease_name": "Common Rust",
        "pathogen_type": "Fungal (Puccinia sorghi)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Oval to elongate cinnamon-brown powdery pustules (uredinia) scattered across both upper and lower "
            "leaf surfaces. Pustules rupture epidermal tissue, releasing golden-brown rust spores."
        ),
        "treatments": {
            "organic": "Sulfur-based fungicides; bio-control agents at vegetative stages.",
            "chemical": "Triazole or Strobilurin fungicides (e.g., Tebuconazole, Azoxystrobin).",
            "cultural": "Plant rust-resistant corn hybrids; early planting to avoid peak airborne spore loads."
        }
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "class_id": "Corn_(maize)___Northern_Leaf_Blight",
        "plant_name": "Corn (Maize)",
        "disease_name": "Northern Corn Leaf Blight (NCLB)",
        "pathogen_type": "Fungal (Exserohilum turcicum)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Large, elongated, elliptical or cigar-shaped grayish-green to tan lesions (2.5–15 cm long) "
            "appearing initially on lower leaves. In damp conditions, dark olivaceous fungal spores coat the lesions."
        ),
        "treatments": {
            "organic": "Ensure deep tillage to bury infected corn residue; apply bio-fungicide formulations.",
            "chemical": "Mancozeb or Propiconazole (Tilt) or Azoxystrobin sprays before tasseling.",
            "cultural": "Practice two-year crop rotation; plant certified resistant corn hybrids."
        }
    },
    "Corn_(maize)___healthy": {
        "class_id": "Corn_(maize)___healthy",
        "plant_name": "Corn (Maize)",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Uniform emerald-green broad leaf blades with intact parallel venation and no fungal pustules or lesions.",
        "treatments": {
            "organic": "Apply well-decomposed FYM (farmyard manure) and bio-fertilizers (Azotobacter, PSB).",
            "chemical": "No fungicide required.",
            "cultural": "Maintain optimum irrigation at critical tasseling and silking growth stages."
        }
    },

    # -------------------------------------------------------------------------
    # APPLE (4 classes)
    # -------------------------------------------------------------------------
    "Apple___Apple_scab": {
        "class_id": "Apple___Apple_scab",
        "plant_name": "Apple",
        "disease_name": "Apple Scab",
        "pathogen_type": "Fungal (Venturia inaequalis)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Olive-green to dull brown velvety spots on leaf surfaces and fruit. Leaf lesions develop "
            "radiating feathery margins; infected fruit becomes scabby, cracked, and deformed."
        ),
        "treatments": {
            "organic": "Sulfur or lime-sulfur sprays applied from green tip through petal fall.",
            "chemical": "Captan, Difenoconazole, or Myclobutanil fungicides.",
            "cultural": "Rake and shred fallen apple leaves in autumn or spray orchard floor with 5% urea to accelerate leaf decomposition."
        }
    },
    "Apple___Black_rot": {
        "class_id": "Apple___Black_rot",
        "plant_name": "Apple",
        "disease_name": "Black Rot (Frogeye Leaf Spot)",
        "pathogen_type": "Fungal (Botryosphaeria obtusa)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Frogeye leaf spots with purple margins and tan/brown centers. On fruit, a firm brown rotting circle "
            "develops, eventually turning jet black and producing mummified fruit on tree branches."
        ),
        "treatments": {
            "organic": "Copper-based dormant sprays and bio-fungicides.",
            "chemical": "Captan, Thiophanate-methyl, or Mancozeb sprays from pink bud through harvest.",
            "cultural": "Prune out dead wood, fire blight cankers, and remove all mummified apples from the orchard."
        }
    },
    "Apple___Cedar_apple_rust": {
        "class_id": "Apple___Cedar_apple_rust",
        "plant_name": "Apple",
        "disease_name": "Cedar Apple Rust",
        "pathogen_type": "Fungal (Gymnosporangium juniperi-virginianae)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Bright orange-yellow circular spots on upper apple leaf surfaces. Later in summer, small tube-like "
            "spore structures (aecia) project from the lower leaf surface, releasing orange powdery spores."
        ),
        "treatments": {
            "organic": "Sulfur sprays starting at bud break.",
            "chemical": "Myclobutanil or Propiconazole applied from tight cluster until 3 weeks after petal fall.",
            "cultural": "Remove nearby eastern red cedar / juniper trees within a 1-2 km radius if feasible."
        }
    },
    "Apple___healthy": {
        "class_id": "Apple___healthy",
        "plant_name": "Apple",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Crisp, fully expanded deep green leaves without scabs, rust spots, or necrotic margins.",
        "treatments": {
            "organic": "Continue balanced orchard floor mulching and organic micronutrient sprays.",
            "chemical": "No chemical treatment required.",
            "cultural": "Maintain annual canopy pruning for maximum sunlight penetration and ventilation."
        }
    },

    # -------------------------------------------------------------------------
    # GRAPE (4 classes)
    # -------------------------------------------------------------------------
    "Grape___Black_rot": {
        "class_id": "Grape___Black_rot",
        "plant_name": "Grape",
        "disease_name": "Black Rot",
        "pathogen_type": "Fungal (Guignardia bidwellii)",
        "severity": "High",
        "is_healthy": False,
        "symptoms": (
            "Small circular reddish-brown leaf spots with distinct dark margins containing tiny black pycnidia. "
            "Infected grape berries shrivel rapidly into hard, wrinkled, black mummies."
        ),
        "treatments": {
            "organic": "Lime-sulfur during dormancy and copper soap during active vegetative flush.",
            "chemical": "Myclobutanil, Mancozeb, or Kresoxim-methyl applied from 1-inch shoot growth through veraison.",
            "cultural": "Prune out and destroy mummified berries and dead canes during winter pruning."
        }
    },
    "Grape___Esca_(Black_Measles)": {
        "class_id": "Grape___Esca_(Black_Measles)",
        "plant_name": "Grape",
        "disease_name": "Esca (Black Measles / Trunk Disease)",
        "pathogen_type": "Fungal Complex (Phaeomoniella chlamydospora, Fomitiporia mediterranea)",
        "severity": "High to Severe",
        "is_healthy": False,
        "symptoms": (
            "'Tiger-stripe' chlorotic and necrotic patterns between leaf veins. Berries show tiny purple-brown "
            "flecking or spots resembling measles, followed by fruit cracking."
        ),
        "treatments": {
            "organic": "Treat pruning wounds with Trichoderma-based wound protectant pastes.",
            "chemical": "Paint fresh pruning cuts with wound sealants containing fungicides like Pyraclostrobin.",
            "cultural": "Delay pruning until late winter to reduce wound susceptibility; sanitize pruning shears between vines."
        }
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "class_id": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        "plant_name": "Grape",
        "disease_name": "Leaf Blight (Isariopsis Spot)",
        "pathogen_type": "Fungal (Pseudocercospora clavispora)",
        "severity": "Moderate",
        "is_healthy": False,
        "symptoms": (
            "Irregularly shaped, angular reddish-brown lesions bounded by smaller veins on older grape leaves. "
            "Lesions coalesce, causing scorched foliage, premature autumn defoliation, and reduced vine vigor."
        ),
        "treatments": {
            "organic": "Copper oxychloride (3 g/L) or Bordeaux mixture (1%) sprays.",
            "chemical": "Carbendazim (1 g/L) or Mancozeb (2 g/L) applied when spots first appear.",
            "cultural": "Ensure open vine trellising and manage canopy density to promote rapid leaf drying."
        }
    },
    "Grape___healthy": {
        "class_id": "Grape___healthy",
        "plant_name": "Grape",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Lush, palmately lobed green leaves with vibrant color and intact tissue throughout the canopy.",
        "treatments": {
            "organic": "Maintain regular foliar kelp extract and vermiwash applications.",
            "chemical": "No intervention required.",
            "cultural": "Continue trellis training and targeted drip irrigation."
        }
    },

    # -------------------------------------------------------------------------
    # BELL PEPPER (2 classes)
    # -------------------------------------------------------------------------
    "Pepper,_bell___Bacterial_spot": {
        "class_id": "Pepper,_bell___Bacterial_spot",
        "plant_name": "Bell Pepper",
        "disease_name": "Bacterial Spot",
        "pathogen_type": "Bacterial (Xanthomonas campestris pv. vesicatoria)",
        "severity": "Moderate to High",
        "is_healthy": False,
        "symptoms": (
            "Small, yellowish-green blister-like spots on leaves that turn dark brown with water-soaked halos. "
            "Infected leaves drop rapidly, exposing fruit to sunscald. Warty raised spots on peppers."
        ),
        "treatments": {
            "organic": "Copper soap (copper octanoate) sprays or Streptomyces bio-fungicide formulations.",
            "chemical": "Copper hydroxide mixed with Mancozeb (prevents copper-resistant bacterial strains).",
            "cultural": "Avoid handling plants when wet; use drip irrigation; buy certified disease-free hot-water-treated seed."
        }
    },
    "Pepper,_bell___healthy": {
        "class_id": "Pepper,_bell___healthy",
        "plant_name": "Bell Pepper",
        "disease_name": "Healthy Foliage",
        "pathogen_type": "None",
        "severity": "None",
        "is_healthy": True,
        "symptoms": "Glossy, uniform dark green leaf blades with smooth leaf margins and absence of foliar spotting.",
        "treatments": {
            "organic": "Provide balanced organic compost and calcium nutrition to prevent blossom end rot.",
            "chemical": "No spray needed.",
            "cultural": "Keep beds weed-free and maintain even soil moisture."
        }
    }
}


def get_all_classes():
    """Return summary list of all 27 supported plant disease classes."""
    return [
        {
            "class_id": k,
            "plant_name": v["plant_name"],
            "disease_name": v["disease_name"],
            "pathogen_type": v["pathogen_type"],
            "severity": v["severity"],
            "is_healthy": v["is_healthy"]
        }
        for k, v in sorted(DISEASE_CATALOG.items())
    ]


def get_disease_detail(class_id: str):
    """Retrieve full agronomic and treatment details for a given class ID."""
    return DISEASE_CATALOG.get(class_id)
