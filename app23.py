# ============================================================
# TRINEXIS — INTELLIGENT VISION PLATFORM
# ============================================================
#
# Flask + YOLO-World + Webcam + Face Recognition + TTS
#
# Camera index and backend are configurable with TRINEXIS_CAMERA_INDEX and
# TRINEXIS_CAMERA_BACKEND. See README.md and .env.example.
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import cv2
import time
import threading
import queue
import platform
import random
import json
import os
import io
import uuid

import numpy as np

from flask import (
    Flask,
    render_template,
    Response,
    jsonify,
    request,
    send_file,
    session,
)

from ultralytics import YOLO
from datetime import datetime
from gtts import gTTS
from collections import defaultdict
from trinexis_core import (
    ALLOWED_MODELS,
    camera_config,
    normalize_model_name,
    rate_per_second,
    relative_distance_index,
    select_speech_objects,
    single_client_check,
    time_decay_factor,
    validate_control_request,
)


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get(
    "TRINEXIS_SECRET_KEY",
    os.urandom(24).hex()
)

API_TOKEN = os.environ.get("TRINEXIS_API_TOKEN", "").strip()
SINGLE_CLIENT_MODE = os.environ.get("TRINEXIS_SINGLE_CLIENT", "1") == "1"
SINGLE_CLIENT_TIMEOUT_S = float(os.environ.get("TRINEXIS_CLIENT_TIMEOUT_S", "60"))
ACTIVE_CLIENT_ID = None
ACTIVE_CLIENT_LAST_SEEN = 0.0
client_lock = threading.Lock()


@app.before_request
def enforce_control_policy():
    """Apply optional token auth and single-client control arbitration."""
    global ACTIVE_CLIENT_ID
    global ACTIVE_CLIENT_LAST_SEEN

    if request.method == "GET" or request.path.startswith("/static/"):
        return None

    if not validate_control_request(API_TOKEN, request.headers):
        return jsonify({
            "status": "error",
            "message": "Invalid or missing API token"
        }), 401

    if SINGLE_CLIENT_MODE:
        client_id = session.get("client_id")
        if not client_id:
            client_id = uuid.uuid4().hex
            session["client_id"] = client_id
        now = time.time()
        with client_lock:
            allowed, active, seen = single_client_check(
                ACTIVE_CLIENT_ID,
                client_id,
                ACTIVE_CLIENT_LAST_SEEN,
                now,
                SINGLE_CLIENT_TIMEOUT_S,
            )
            ACTIVE_CLIENT_ID = active
            ACTIVE_CLIENT_LAST_SEEN = seen
        if not allowed:
            return jsonify({
                "status": "error",
                "message": "Another client currently controls this single-client session"
            }), 409
    return None


# ============================================================
# CAMERA CONFIGURATION
# ============================================================

# Camera index, backend, and resolution are configurable through environment
# variables so the same source works on Windows, Linux, and macOS.
CAMERA_CONFIG = camera_config(os.environ)
WEBCAM_INDEX = CAMERA_CONFIG["index"]
CAMERA_WIDTH = int(os.environ.get("TRINEXIS_CAMERA_WIDTH", "1280"))
CAMERA_HEIGHT = int(os.environ.get("TRINEXIS_CAMERA_HEIGHT", "720"))
CAMERA_BACKEND_NAME = CAMERA_CONFIG["backend"]

_BACKEND_CONSTANTS = {
    "AUTO": cv2.CAP_ANY,
    "DSHOW": getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY),
    "MSMF": getattr(cv2, "CAP_MSMF", cv2.CAP_ANY),
    "V4L2": getattr(cv2, "CAP_V4L2", cv2.CAP_ANY),
}
CAMERA_BACKEND = _BACKEND_CONSTANTS.get(CAMERA_BACKEND_NAME, cv2.CAP_ANY)


# ============================================================
# YOLO WORLD MODEL
# ============================================================

MODEL_NAME = "yolov8s-worldv2.pt"

print(
    f"[TRINEXIS] Loading model: {MODEL_NAME}"
)

try:

    model = YOLO(MODEL_NAME)

    print(
        "[TRINEXIS] Model loaded successfully."
    )

except Exception as e:

    print(
        f"[TRINEXIS] MODEL ERROR: {e}"
    )

    raise


# ============================================================
# FACE RECOGNITION
# ============================================================

try:

    from modules.faces import FaceRecognizer

    face_recognizer = FaceRecognizer()

    FACE_REC_ENABLED = True

    print(
        "[TRINEXIS] Face recognition loaded."
    )

except Exception as e:

    face_recognizer = None

    FACE_REC_ENABLED = False

    print(
        f"[TRINEXIS] Face recognition disabled: {e}"
    )


# ============================================================
# VOCABULARY
# ============================================================

VOCABULARY = [

    # PEOPLE
    "person",
    "man",
    "woman",
    "child",
    "baby",
    "face",
    "hand",
    "eye",
    "head",
    "arm",
    "leg",
    "foot",
    "finger",
    "hair",
    "smile",

    # CLOTHING
    "shirt",
    "t-shirt",
    "pants",
    "jeans",
    "dress",
    "skirt",
    "jacket",
    "coat",
    "hoodie",
    "sweater",
    "hat",
    "cap",
    "helmet",
    "glasses",
    "sunglasses",
    "shoe",
    "sneaker",
    "boot",
    "sandal",
    "sock",
    "glove",
    "scarf",
    "tie",
    "belt",
    "watch",
    "ring",
    "necklace",
    "earring",
    "bracelet",
    "backpack",
    "handbag",
    "purse",
    "wallet",
    "suitcase",
    "bag",
    "umbrella",

    # VEHICLES
    "car",
    "truck",
    "bus",
    "motorcycle",
    "bicycle",
    "scooter",
    "train",
    "airplane",
    "helicopter",
    "boat",
    "ship",
    "van",
    "taxi",
    "ambulance",
    "fire truck",
    "police car",
    "tractor",
    "forklift",
    "wheel",
    "tire",
    "engine",

    # FURNITURE
    "chair",
    "table",
    "desk",
    "couch",
    "sofa",
    "bed",
    "pillow",
    "blanket",
    "mattress",
    "shelf",
    "bookshelf",
    "cabinet",
    "wardrobe",
    "drawer",
    "door",
    "window",
    "curtain",
    "lamp",
    "chandelier",
    "mirror",
    "clock",
    "picture frame",
    "painting",
    "poster",
    "rug",
    "carpet",
    "vase",
    "candle",
    "flower pot",
    "plant",

    # BATHROOM / CLEANING
    "toilet",
    "sink",
    "bathtub",
    "shower",
    "faucet",
    "towel",
    "trash can",
    "broom",
    "mop",
    "bucket",

    # ELECTRONICS
    "cell phone",
    "smartphone",
    "laptop",
    "computer",
    "monitor",
    "keyboard",
    "mouse",
    "tablet",
    "ipad",
    "television",
    "tv",
    "remote control",
    "speaker",
    "headphones",
    "earbuds",
    "microphone",
    "camera",
    "webcam",
    "printer",
    "scanner",
    "router",
    "charger",
    "cable",
    "usb",
    "battery",
    "power bank",
    "smartwatch",
    "drone",
    "robot",
    "game controller",
    "console",

    # KITCHEN
    "bottle",
    "cup",
    "glass",
    "mug",
    "plate",
    "bowl",
    "fork",
    "knife",
    "spoon",
    "chopsticks",
    "pot",
    "pan",
    "wok",
    "kettle",
    "teapot",
    "blender",
    "microwave",
    "oven",
    "stove",
    "refrigerator",
    "freezer",
    "toaster",
    "coffee maker",

    # FOOD
    "apple",
    "banana",
    "orange",
    "grape",
    "strawberry",
    "watermelon",
    "lemon",
    "lime",
    "mango",
    "pineapple",
    "tomato",
    "potato",
    "onion",
    "carrot",
    "broccoli",
    "corn",
    "pepper",
    "mushroom",
    "bread",
    "cake",
    "pizza",
    "burger",
    "sandwich",
    "hot dog",
    "donut",
    "cookie",
    "candy",
    "chocolate",
    "ice cream",
    "egg",
    "cheese",
    "butter",
    "milk",
    "juice",
    "water bottle",
    "coffee",
    "tea",

    # OFFICE
    "pen",
    "pencil",
    "marker",
    "highlighter",
    "eraser",
    "ruler",
    "scissors",
    "stapler",
    "tape",
    "glue",
    "notebook",
    "notepad",
    "paper",
    "document",
    "folder",
    "binder",
    "envelope",
    "stamp",
    "calculator",
    "whiteboard",
    "blackboard",
    "projector",

    # SPORTS
    "ball",
    "football",
    "soccer ball",
    "basketball",
    "tennis ball",
    "baseball",
    "volleyball",
    "golf ball",
    "cricket bat",
    "tennis racket",
    "badminton racket",
    "skateboard",
    "surfboard",
    "snowboard",
    "ski",
    "bicycle helmet",
    "dumbbell",
    "weight",
    "yoga mat",
    "jump rope",
    "frisbee",
    "kite",
    "fishing rod",

    # ANIMALS
    "dog",
    "cat",
    "bird",
    "fish",
    "horse",
    "cow",
    "pig",
    "sheep",
    "goat",
    "chicken",
    "duck",
    "rabbit",
    "hamster",
    "mouse",
    "snake",
    "lizard",
    "frog",
    "turtle",
    "butterfly",
    "bee",
    "ant",
    "spider",
    "elephant",
    "lion",
    "tiger",
    "bear",
    "monkey",
    "giraffe",
    "zebra",
    "deer",
    "fox",
    "wolf",
    "eagle",
    "owl",
    "parrot",
    "penguin",
    "shark",
    "dolphin",
    "whale",
    "octopus",
    "crab",
    "lobster",
    "snail",

    # ENVIRONMENT
    "tree",
    "flower",
    "grass",
    "bush",
    "leaf",
    "branch",
    "log",
    "rock",
    "stone",
    "mountain",
    "hill",
    "river",
    "lake",
    "ocean",
    "wave",
    "cloud",
    "sun",
    "moon",
    "star",
    "rain",
    "snow",
    "rainbow",
    "fire",
    "smoke",
    "sand",
    "beach",
    "path",
    "road",
    "bridge",
    "fence",
    "gate",
    "wall",
    "building",
    "house",
    "skyscraper",
    "tower",
    "tent",
    "flag",
    "sign",
    "traffic light",
    "street light",
    "bench",
    "mailbox",
    "fire hydrant",
    "parking meter",

    # TOOLS
    "hammer",
    "screwdriver",
    "wrench",
    "pliers",
    "drill",
    "saw",
    "nail",
    "screw",
    "bolt",
    "nut",
    "wire",
    "pipe",
    "ladder",
    "toolbox",
    "tape measure",
    "level",
    "axe",
    "shovel",
    "rake",

    # MEDICAL / SAFETY
    "mask",
    "syringe",
    "bandage",
    "pill",
    "medicine",
    "thermometer",
    "stethoscope",
    "wheelchair",
    "crutch",
    "first aid kit",
    "fire extinguisher",
    "life jacket",
    "cone",
    "barrier",

    # TOYS / MUSIC / OTHER
    "teddy bear",
    "doll",
    "toy car",
    "lego",
    "puzzle",
    "balloon",
    "stuffed animal",
    "action figure",
    "board game",
    "dice",
    "playing card",
    "guitar",
    "piano",
    "drum",
    "violin",
    "flute",
    "trumpet",
    "book",
    "magazine",
    "newspaper",
    "comic",

    # PERSONAL ITEMS
    "toothbrush",
    "toothpaste",
    "soap",
    "shampoo",
    "comb",
    "brush",
    "razor",
    "hair dryer",
    "tissue",
    "toilet paper",
    "perfume",
    "lotion",
    "sunscreen",
    "lipstick",
    "makeup",
    "key",
    "lock",
    "coin",
    "money",
    "credit card",
    "id card",
    "passport",
    "ticket",
    "receipt",
    "label",
    "tag",
    "sticker",
    "button",
    "zipper",
    "hook",
    "hanger",
    "basket",
    "box",
    "crate",
    "barrel",
    "jar",
    "can",
    "tin",
    "container",
    "lid",
    "cap",
    "straw",
    "napkin",
    "tablecloth",
    "apron",
    "suit",
    "uniform",
    "costume",
    "crown",
    "medal",
    "trophy",
    "gift",
    "ribbon",
    "wreath",
    "lantern",
    "torch",
    "lighter",
    "match",
    "ashtray",
    "telescope",
    "binoculars",
    "compass",
    "map",
    "globe",
    "hourglass",
    "magnet",
    "sponge",
]


# Remove duplicates while keeping order.
VOCABULARY = list(
    dict.fromkeys(VOCABULARY)
)


# ============================================================
# SET YOLO WORLD CLASSES
# ============================================================

try:

    model.set_classes(
        VOCABULARY
    )

    print(
        f"[TRINEXIS] {len(VOCABULARY)} classes loaded."
    )

except Exception as e:

    print(
        f"[TRINEXIS] Class configuration warning: {e}"
    )


# ============================================================
# GLOBAL STATE
# ============================================================

# Heuristic constants for a non-metric relative distance index.
FOCAL_LENGTH = 360

KNOWN_WIDTH = 60

INTERVAL = 1.5

prev = 0

running = False

confidence_threshold = 0.15

language = "English"

detection_log = []

IMG_SIZE = 640

current_frame = None

frame_lock = threading.Lock()

heatmap_accumulator = None

last_heatmap_update = None

HEATMAP_HALF_LIFE_S = float(
    os.environ.get("TRINEXIS_HEATMAP_HALF_LIFE_S", "60")
)

recent_inference_times = []

alert_objects = set()


# ============================================================
# STATISTICS
# ============================================================

stats = {

    "total_detections": 0,

    "unique_objects": set(),

    "session_start": None,

    "fps": 0,

    "capture_fps": 0,

    "inference_fps": 0.0,

    "model_name": MODEL_NAME,

    "frames_processed": 0,

    "avg_confidence": 0,

    "last_detection_time": None,

    "object_frequency": defaultdict(int),

    "confidence_history": [],

    "detection_timeline": [],

    "uptime_start": time.time(),

}


# ============================================================
# LANGUAGES
# ============================================================

language_code_map = {

    # ----------------------------
    # INDIAN
    # ----------------------------

    "Hindi": "hi",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Odia": "or",
    "Assamese": "as",
    "Urdu": "ur",
    "Sindhi": "sd",
    "Konkani": "gom",
    "Maithili": "mai",
    "Dogri": "doi",
    "Bodo": "brx",
    "Santali": "sat",
    "Kashmiri": "ks",
    "Nepali": "ne",
    "Manipuri": "mni-Mtei",
    "Sanskrit": "sa",

    # ----------------------------
    # INTERNATIONAL
    # ----------------------------

    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh-CN",
    "Korean": "ko",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
    "Dutch": "nl",
    "Turkish": "tr",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Swahili": "sw",
    "Polish": "pl",
    "Ukrainian": "uk",
    "Romanian": "ro",
    "Greek": "el",
    "Czech": "cs",
    "Swedish": "sv",
    "Finnish": "fi",
    "Hungarian": "hu",
    "Norwegian": "no",
    "Danish": "da",
    "Hebrew": "iw",
    "Filipino": "tl",
    "Malay": "ms",
    "Burmese": "my",
    "Sinhala": "si",
    "Afrikaans": "af",
    "Amharic": "am",
    "Catalan": "ca",
    "Croatian": "hr",
    "Serbian": "sr",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Estonian": "et",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Georgian": "ka",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Kazakh": "kk",
    "Uzbek": "uz",
    "Mongolian": "mn",
    "Khmer": "km",
    "Lao": "lo",

}


# ============================================================
# SPEECH
# ============================================================

speech_queue = queue.Queue(
    maxsize=1
)

speech_enabled = True

last_spoken_time = 0

last_face_greetings = {}

FACE_GREETING_COOLDOWN = 15.0

# Increased so speech doesn't become annoying.
SPEECH_COOLDOWN = 4.5

# IMPORTANT:
# Keep this LOW to keep speech short.
MAX_OBJECTS_TO_SPEAK = 2


# ============================================================
# SHORT SPEECH PREFIXES
# ============================================================

speech_prefixes = {

    "Hindi":
        "दृश्य में {count} वस्तुएं। {objects}। सबसे पास {nearest}।",

    "Gujarati":
        "દૃશ્યમાં {count} વસ્તુઓ. {objects}. સૌથી નજીક {nearest}.",

    "Bengali":
        "দৃশ্যে {count}টি বস্তু। {objects}। সবচেয়ে কাছে {nearest}।",

    "Tamil":
        "காட்சியில் {count} பொருட்கள். {objects}. அருகில் {nearest}.",

    "Telugu":
        "దృశ్యంలో {count} వస్తువులు. {objects}. దగ్గరగా {nearest}.",

    "Kannada":
        "ದೃಶ್ಯದಲ್ಲಿ {count} ವಸ್ತುಗಳು. {objects}. ಹತ್ತಿರದಲ್ಲಿ {nearest}.",

    "Malayalam":
        "ദൃശ്യത്തിൽ {count} വസ്തുക്കൾ. {objects}. അടുത്തത് {nearest}.",

    "Marathi":
        "दृश्यात {count} वस्तू. {objects}. जवळ {nearest}.",

    "Punjabi":
        "ਦ੍ਰਿਸ਼ ਵਿੱਚ {count} ਵਸਤੂਆਂ। {objects}। ਨੇੜੇ {nearest}।",

    "Odia":
        "ଦୃଶ୍ୟରେ {count}ଟି ବସ୍ତୁ। {objects}। ନିକଟରେ {nearest}।",

    "Assamese":
        "দৃশ্যত {count}টা বস্তু। {objects}। ওচৰত {nearest}।",

    "Urdu":
        "منظر میں {count} چیزیں۔ {objects}۔ قریب {nearest}۔",

    "Nepali":
        "दृश्यमा {count} वस्तु। {objects}। नजिक {nearest}।",

    "Sanskrit":
        "दृश्ये {count} वस्तूनि। {objects}। समीपे {nearest}।",

    "English":
        "{count} objects. {objects}. Nearest {nearest}.",

    "Spanish":
        "{count} objetos. {objects}. Más cerca {nearest}.",

    "French":
        "{count} objets. {objects}. Plus proche {nearest}.",

    "German":
        "{count} Objekte. {objects}. Am nächsten {nearest}.",

    "Japanese":
        "{count}個の物体。{objects}。最も近いのは{nearest}。",

    "Chinese":
        "检测到{count}个物体。{objects}。最近的是{nearest}。",

    "Korean":
        "{count}개의 물체. {objects}. 가장 가까운 것은 {nearest}.",

    "Arabic":
        "تم اكتشاف {count} كائنات. {objects}. الأقرب {nearest}.",

    "Portuguese":
        "{count} objetos. {objects}. Mais próximo {nearest}.",

    "Russian":
        "{count} объектов. {objects}. Ближе всего {nearest}.",

    "Italian":
        "{count} oggetti. {objects}. Più vicino {nearest}.",

    "Dutch":
        "{count} objecten. {objects}. Dichtstbij {nearest}.",

    "Turkish":
        "{count} nesne. {objects}. En yakın {nearest}.",

    "Thai":
        "พบ {count} วัตถุ {objects} ใกล้ที่สุดคือ {nearest}",

    "Vietnamese":
        "{count} đối tượng. {objects}. Gần nhất {nearest}.",

    "Indonesian":
        "{count} objek. {objects}. Terdekat {nearest}.",

    "Polish":
        "{count} obiektów. {objects}. Najbliżej {nearest}.",

    "Ukrainian":
        "{count} об'єктів. {objects}. Найближче {nearest}.",

    "Romanian":
        "{count} obiecte. {objects}. Cel mai aproape {nearest}.",

    "Greek":
        "{count} αντικείμενα. {objects}. Πιο κοντά {nearest}.",

    "Czech":
        "{count} objektů. {objects}. Nejblíže {nearest}.",

    "Swedish":
        "{count} objekt. {objects}. Närmast {nearest}.",

    "Finnish":
        "{count} kohdetta. {objects}. Lähimpänä {nearest}.",

    "Hungarian":
        "{count} objektum. {objects}. Legközelebb {nearest}.",

    "Norwegian":
        "{count} objekter. {objects}. Nærmest {nearest}.",

    "Danish":
        "{count} objekter. {objects}. Tættest på {nearest}.",

    "Hebrew":
        "{count} אובייקטים. {objects}. הקרוב ביותר {nearest}.",

    "Filipino":
        "{count} bagay. {objects}. Pinakamalapit {nearest}.",

    "Malay":
        "{count} objek. {objects}. Paling dekat {nearest}.",

    "Burmese":
        "အရာဝတ္ထု {count} ခု။ {objects}။ အနီးဆုံး {nearest}။",

    "Sinhala":
        "වස්තූන් {count}ක්. {objects}. ආසන්නම {nearest}.",

    "Afrikaans":
        "{count} voorwerpe. {objects}. Naaste {nearest}.",

    "Catalan":
        "{count} objectes. {objects}. Més proper {nearest}.",

    "Croatian":
        "{count} objekata. {objects}. Najbliži {nearest}.",

    "Serbian":
        "{count} објеката. {objects}. Најближе {nearest}.",

    "Slovak":
        "{count} objektov. {objects}. Najbližšie {nearest}.",

    "Slovenian":
        "{count} predmetov. {objects}. Najbližje {nearest}.",

    "Estonian":
        "{count} objekti. {objects}. Lähim {nearest}.",

    "Latvian":
        "{count} objekti. {objects}. Tuvākais {nearest}.",

    "Lithuanian":
        "{count} objektų. {objects}. Arčiausiai {nearest}.",

    "Georgian":
        "{count} ობიექტი. {objects}. უახლოესი {nearest}.",

    "Armenian":
        "{count} օբյեկտ. {objects}. Ամենամոտը {nearest}.",

    "Azerbaijani":
        "{count} obyekt. {objects}. Ən yaxın {nearest}.",

    "Kazakh":
        "{count} нысан. {objects}. Ең жақын {nearest}.",

    "Uzbek":
        "{count} ta obyekt. {objects}. Eng yaqini {nearest}.",

    "Mongolian":
        "{count} объект. {objects}. Хамгийн ойр {nearest}.",

    "Khmer":
        "វត្ថុ {count}។ {objects}។ ជិតបំផុត {nearest}។",

    "Lao":
        "ວັດຖຸ {count}. {objects}. ໃກ້ທີ່ສຸດ {nearest}.",

}


# ============================================================
# SHORT FACE GREETINGS
# ============================================================

face_greetings = {

    "Hindi":
        "नमस्ते {name}",

    "Gujarati":
        "નમસ્તે {name}",

    "Bengali":
        "নমস্কার {name}",

    "Tamil":
        "வணக்கம் {name}",

    "Telugu":
        "నమస్కారం {name}",

    "Kannada":
        "ನಮಸ್ಕಾರ {name}",

    "Malayalam":
        "നമസ്കാരം {name}",

    "Marathi":
        "नमस्कार {name}",

    "Punjabi":
        "ਸਤ ਸ੍ਰੀ ਅਕਾਲ {name}",

    "Odia":
        "ନମସ୍କାର {name}",

    "Urdu":
        "السلام علیکم {name}",

    "Nepali":
        "नमस्ते {name}",

    "Japanese":
        "こんにちは {name}",

    "Chinese":
        "你好 {name}",

    "Korean":
        "안녕하세요 {name}",

    "Arabic":
        "مرحبا {name}",

    "French":
        "Bonjour {name}",

    "German":
        "Hallo {name}",

    "Spanish":
        "Hola {name}",

    "Portuguese":
        "Olá {name}",

    "Russian":
        "Привет {name}",

    "Italian":
        "Ciao {name}",

}


# ============================================================
# DETECTION COLORS
# ============================================================

random.seed(42)

detection_colors = [

    (
        random.randint(60, 255),
        random.randint(60, 255),
        random.randint(60, 255),
    )

    for _ in range(600)

]


# ============================================================
# BUILD SHORT SPEECH
# ============================================================

def build_speech_text(
    annotated_objects,
    lang
):

    if not annotated_objects:

        return ""


    # --------------------------------------------------------
    # ALERT-AWARE SELECTION (BEFORE TRUNCATION)
    # --------------------------------------------------------

    selected = select_speech_objects(
        annotated_objects,
        alert_objects,
        MAX_OBJECTS_TO_SPEAK
    )


    # --------------------------------------------------------
    # GROUP OBJECTS
    # --------------------------------------------------------

    counts = defaultdict(int)

    for obj in selected:

        counts[
            obj["name"]
        ] += 1


    parts = []


    for name, count in counts.items():

        if count > 1:

            parts.append(
                f"{count} {name}s"
            )

        else:

            parts.append(
                name
            )


    objects_text = ", ".join(
        parts
    )


    # --------------------------------------------------------
    # NEAREST OBJECT
    # --------------------------------------------------------

    nearest = min(

        selected,

        key=lambda x:
            x["distance"]

    )


    nearest_text = (

        f"{nearest['name']} "
        f"distance index {nearest['distance']:.1f}"

    )


    # --------------------------------------------------------
    # LANGUAGE TEMPLATE
    # --------------------------------------------------------

    template = speech_prefixes.get(

        lang,

        speech_prefixes[
            "English"
        ]

    )


    try:

        return template.format(

            count=len(
                annotated_objects
            ),

            objects=objects_text,

            nearest=nearest_text,

        )

    except Exception:

        return (

            f"{len(annotated_objects)} "
            f"objects. "
            f"{objects_text}. "
            f"Nearest "
            f"{nearest_text}."

        )


# ============================================================
# AUDIO PLAYBACK
# ============================================================

def play_audio_sync(
    filepath
):

    system = platform.system()


    try:

        # ----------------------------------------------------
        # WINDOWS
        # ----------------------------------------------------

        if system == "Windows":

            import ctypes

            alias = (
                f"tts_"
                f"{int(time.time() * 1000)}"
            )


            ctypes.windll.winmm.mciSendStringW(

                f'open "{filepath}" '
                f'type mpegvideo '
                f'alias {alias}',

                None,
                0,
                0,

            )


            ctypes.windll.winmm.mciSendStringW(

                f"play {alias} wait",

                None,
                0,
                0,

            )


            ctypes.windll.winmm.mciSendStringW(

                f"close {alias}",

                None,
                0,
                0,

            )


        # ----------------------------------------------------
        # MAC
        # ----------------------------------------------------

        elif system == "Darwin":

            os.system(
                f'afplay "{filepath}"'
            )


        # ----------------------------------------------------
        # LINUX
        # ----------------------------------------------------

        else:

            os.system(

                f'mpg321 "{filepath}" '
                f'> /dev/null 2>&1 || '
                f'mpg123 "{filepath}" '
                f'> /dev/null 2>&1 || '
                f'ffplay -nodisp -autoexit '
                f'"{filepath}" '
                f'> /dev/null 2>&1'

            )


    except Exception as e:

        print(
            f"[Audio Error] {e}"
        )


# ============================================================
# SPEECH WORKER
# ============================================================

def speech_worker():

    while True:

        item = speech_queue.get()


        if item is None:

            speech_queue.task_done()

            break


        text, lang = item


        filename = (

            "speech_trinexis_"
            f"{threading.current_thread().ident}.mp3"

        )


        try:

            code = language_code_map.get(

                lang,

                "en"

            )


            try:

                tts = gTTS(

                    text=text,

                    lang=code,

                    slow=False,

                )

            except Exception as e:

                print(

                    f"[TTS] "
                    f"{lang} ({code}) "
                    f"unsupported. "
                    f"Using English. "
                    f"{e}"

                )

                tts = gTTS(

                    text=text,

                    lang="en",

                    slow=False,

                )


            tts.save(
                filename
            )


            play_audio_sync(
                filename
            )


        except Exception as e:

            print(
                f"[TTS Worker Error] {e}"
            )


        finally:

            try:

                if os.path.exists(
                    filename
                ):

                    os.remove(
                        filename
                    )

            except Exception:
                pass


            speech_queue.task_done()


# ============================================================
# START SINGLE TTS WORKER
# ============================================================

threading.Thread(

    target=speech_worker,

    daemon=True,

).start()


# ============================================================
# SPEAK
# ============================================================

def speak(
    text,
    lang
):

    global last_spoken_time


    if not speech_enabled:

        return


    if not text:

        return


    now = time.time()


    # --------------------------------------------------------
    # COOLDOWN
    # --------------------------------------------------------

    if (

        now - last_spoken_time

        < SPEECH_COOLDOWN

    ):

        return


    # --------------------------------------------------------
    # REMOVE OLD SPEECH
    #
    # This is important.
    #
    # If YOLO detects many scenes quickly,
    # old speech shouldn't pile up.
    # --------------------------------------------------------

    while True:

        try:

            speech_queue.get_nowait()

            speech_queue.task_done()

        except queue.Empty:

            break


    # --------------------------------------------------------
    # ADD ONLY LATEST SPEECH
    # --------------------------------------------------------

    try:

        speech_queue.put_nowait(
            (
                text,
                lang
            )
        )

        last_spoken_time = now

    except queue.Full:

        pass


# ============================================================
# HEATMAP
# ============================================================

def update_heatmap(
    shape,
    boxes
):

    global heatmap_accumulator
    global last_heatmap_update

    now = time.time()

    if heatmap_accumulator is None:

        heatmap_accumulator = np.zeros(
            shape[:2],
            dtype=np.float32
        )

    elapsed = 0.0
    if last_heatmap_update is not None:
        elapsed = max(0.0, now - last_heatmap_update)

    # Frame-rate-independent exponential decay.
    heatmap_accumulator *= time_decay_factor(
        elapsed,
        HEATMAP_HALF_LIFE_S
    )

    for box in boxes:
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        cv2.circle(
            heatmap_accumulator,
            (cx, cy),
            35,
            1,
            -1,
        )

    last_heatmap_update = now



# ============================================================
# YOLO DETECTION
# ============================================================

def perform_detection(
    frame,
    conf=0.15
):

    try:

        results = model.predict(

            source=frame,

            conf=conf,

            imgsz=IMG_SIZE,

            iou=0.5,

            max_det=100,

            verbose=False,

        )


        if (

            results

            and len(results[0].boxes) > 0

        ):

            return results[0]


    except Exception as e:

        print(
            f"[YOLO Error] {e}"
        )


    return None


# ============================================================
# DRAW DETECTIONS
# ============================================================

def annotate_frame(
    frame,
    result
):

    global detection_log
    global stats


    annotated = []

    heatmap_boxes = []

    confidences = []


    # ========================================================
    # LOOP OBJECTS
    # ========================================================

    for bbox in result.boxes:

        try:

            confidence = float(
                bbox.conf[0]
            )

            class_id = int(
                bbox.cls[0]
            )


            class_name = (

                result.names.get(

                    class_id,

                    f"obj_{class_id}"

                )

            )


            x1, y1, x2, y2 = (

                int(v)

                for v in bbox.xyxy[0]

            )


            width = max(
                x2 - x1,
                1
            )

            height = max(
                y2 - y1,
                1
            )


            # ------------------------------------------------
            # RELATIVE DISTANCE INDEX (NOT METRIC DISTANCE)
            # ------------------------------------------------

            distance_index = relative_distance_index(
                width,
                KNOWN_WIDTH,
                FOCAL_LENGTH
            )


            color = detection_colors[
                class_id
                % len(detection_colors)
            ]


            heatmap_boxes.append(

                (
                    x1,
                    y1,
                    x2,
                    y2
                )

            )


            confidences.append(
                confidence
            )


            # =================================================
            # GLASS FILL
            # =================================================

            overlay = frame.copy()


            cv2.rectangle(

                overlay,

                (x1, y1),

                (x2, y2),

                color,

                -1,

            )


            cv2.addWeighted(

                overlay,

                0.10,

                frame,

                0.90,

                0,

                frame,

            )


            # =================================================
            # BORDER
            # =================================================

            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                color,

                2,

            )


            # =================================================
            # CORNER ACCENTS
            # =================================================

            corner = min(

                20,

                max(width // 4, 1),

                max(height // 4, 1)

            )


            corners = [

                (
                    x1,
                    y1,
                    1,
                    1
                ),

                (
                    x2,
                    y1,
                    -1,
                    1
                ),

                (
                    x1,
                    y2,
                    1,
                    -1
                ),

                (
                    x2,
                    y2,
                    -1,
                    -1
                ),

            ]


            for (

                cx,
                cy,
                dx,
                dy

            ) in corners:

                cv2.line(

                    frame,

                    (cx, cy),

                    (
                        cx + corner * dx,
                        cy
                    ),

                    color,

                    3,

                )


                cv2.line(

                    frame,

                    (cx, cy),

                    (
                        cx,
                        cy + corner * dy
                    ),

                    color,

                    3,

                )


            # =================================================
            # LABEL
            # =================================================

            label = (

                f"{class_name} "
                f"{confidence:.0%} | "
                f"distance index {distance_index:.1f}"

            )


            (
                text_width,
                text_height
            ), _ = cv2.getTextSize(

                label,

                cv2.FONT_HERSHEY_SIMPLEX,

                0.45,

                1,

            )


            label_top = max(

                y1 - text_height - 12,

                0

            )


            cv2.rectangle(

                frame,

                (
                    x1,
                    label_top
                ),

                (
                    x1 + text_width + 10,
                    y1
                ),

                color,

                -1,

            )


            cv2.putText(

                frame,

                label,

                (
                    x1 + 5,
                    y1 - 6
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.45,

                (255, 255, 255),

                1,

                cv2.LINE_AA,

            )


            # =================================================
            # CENTER DOT
            # =================================================

            cv2.circle(

                frame,

                (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2
                ),

                3,

                color,

                -1,

            )


            # =================================================
            # SAVE OBJECT
            # =================================================

            annotated.append({

                "name":
                    class_name,

                "confidence":
                    round(
                        confidence,
                        3
                    ),

                "distance":
                    round(
                        distance_index,
                        1
                    ),

            })


            # =================================================
            # STATS
            # =================================================

            stats[
                "total_detections"
            ] += 1


            stats[
                "unique_objects"
            ].add(
                class_name
            )


            stats[
                "object_frequency"
            ][
                class_name
            ] += 1


        except Exception as e:

            print(
                f"[Detection Object Error] {e}"
            )


    # ========================================================
    # HEATMAP
    # ========================================================

    update_heatmap(

        frame.shape,

        heatmap_boxes

    )


    # ========================================================
    # LOGGING
    # ========================================================

    if annotated:

        now = datetime.now()


        average_confidence = round(

            sum(confidences)
            / len(confidences),

            3

        )


        detection_log.append({

            "timestamp":
                now.strftime(
                    "%H:%M:%S"
                ),

            "objects":
                annotated,

            "total_in_frame":
                len(annotated),

            "avg_confidence":
                average_confidence,

        })


        if len(
            detection_log
        ) > 500:

            del detection_log[
                :-500
            ]


        # ----------------------------------------------------
        # STATS
        # ----------------------------------------------------

        stats[
            "last_detection_time"
        ] = now.strftime(
            "%H:%M:%S"
        )


        stats[
            "avg_confidence"
        ] = average_confidence


        stats[
            "confidence_history"
        ].append(
            average_confidence
        )


        if len(
            stats[
                "confidence_history"
            ]
        ) > 100:

            stats[
                "confidence_history"
            ] = stats[
                "confidence_history"
            ][-100:]


        stats[
            "detection_timeline"
        ].append({

            "time":
                now.strftime(
                    "%H:%M:%S"
                ),

            "count":
                len(annotated),

        })


        if len(
            stats[
                "detection_timeline"
            ]
        ) > 60:

            stats[
                "detection_timeline"
            ] = stats[
                "detection_timeline"
            ][-60:]


        # ====================================================
        # SHORT SPEECH
        # ====================================================

        # Pass the complete detection list so alert-aware ranking happens
        # before the spoken shortlist is truncated.
        speech_text = (
            build_speech_text(
                annotated,
                language
            )
        )


        if speech_text:

            speak(

                speech_text,

                language

            )


    # ========================================================
    # OBJECT COUNT
    # ========================================================

    cv2.putText(

        frame,

        f"Objects: {len(annotated)}",

        (
            10,
            frame.shape[0] - 15
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2,

        cv2.LINE_AA,

    )


    return frame


# ============================================================
# CREATE CAMERA ERROR FRAME
# ============================================================

def create_camera_error_frame(
    message
):

    frame = np.zeros(

        (
            480,
            640,
            3
        ),

        dtype=np.uint8

    )


    cv2.putText(

        frame,

        "USB WEBCAM ERROR",

        (
            130,
            210
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.0,

        (0, 0, 255),

        2,

        cv2.LINE_AA,

    )


    cv2.putText(

        frame,

        message,

        (
            80,
            255
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1,

        cv2.LINE_AA,

    )


    cv2.putText(

        frame,

        f"Camera Index: {WEBCAM_INDEX}",

        (
            190,
            295
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (150, 200, 255),

        1,

        cv2.LINE_AA,

    )


    return frame


# ============================================================
# VIDEO FEED
# ============================================================

def generate_feed():

    global running
    global prev
    global stats
    global current_frame


    # ========================================================
    # OPEN EXTERNAL USB WEBCAM
    # ========================================================

    print(
        f"[TRINEXIS] Opening USB webcam "
        f"index {WEBCAM_INDEX}..."
    )


    cap = cv2.VideoCapture(

        WEBCAM_INDEX,

        CAMERA_BACKEND

    )


    # ========================================================
    # CAMERA CHECK
    # ========================================================

    if not cap.isOpened():

        print(

            f"[TRINEXIS] ERROR: "
            f"USB webcam index "
            f"{WEBCAM_INDEX} could not be opened."

        )


        error_frame = (
            create_camera_error_frame(
                "Connect external webcam"
            )
        )


        _, jpeg = cv2.imencode(

            ".jpg",

            error_frame

        )


        error_bytes = (
            jpeg.tobytes()
        )


        while True:

            yield (

                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + error_bytes
                + b"\r\n\r\n"

            )


            time.sleep(1)


    # ========================================================
    # CAMERA CONFIG
    # ========================================================

    cap.set(

        cv2.CAP_PROP_FRAME_WIDTH,

        CAMERA_WIDTH

    )


    cap.set(

        cv2.CAP_PROP_FRAME_HEIGHT,

        CAMERA_HEIGHT

    )


    cap.set(

        cv2.CAP_PROP_BUFFERSIZE,

        1

    )


    actual_width = int(

        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )

    )


    actual_height = int(

        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )

    )


    print(

        f"[TRINEXIS] USB webcam connected."

    )

    print(

        f"[TRINEXIS] Resolution: "
        f"{actual_width}x{actual_height}"

    )


    # ========================================================
    # FPS
    # ========================================================

    fps_counter = 0

    fps_time = time.time()


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        ret, frame = cap.read()


        # ====================================================
        # READ FAILURE
        # ====================================================

        if not ret:

            print(
                "[TRINEXIS] Webcam frame read failed."
            )

            time.sleep(
                0.05
            )

            continue


        # ====================================================
        # FPS
        # ====================================================

        fps_counter += 1


        if (

            time.time()
            - fps_time

            >= 1.0

        ):

            stats[
                "fps"
            ] = fps_counter

            stats[
                "capture_fps"
            ] = fps_counter


            fps_counter = 0

            fps_time = time.time()


        stats[
            "frames_processed"
        ] += 1


        # ====================================================
        # DETECTION
        # ====================================================

        if running:

            if (

                time.time()
                - prev

                >= INTERVAL

            ):

                # ------------------------------------------------
                # YOLO
                # ------------------------------------------------

                result = perform_detection(

                    frame,

                    confidence_threshold

                )


                # Track detector cadence separately from camera frame rate.
                now = time.time()
                recent_inference_times.append(now)
                cutoff = now - 5.0
                while (
                    recent_inference_times
                    and recent_inference_times[0] < cutoff
                ):
                    recent_inference_times.pop(0)
                stats[
                    "inference_fps"
                ] = rate_per_second(
                    recent_inference_times,
                    now,
                    5.0
                )


                if result is not None:

                    frame = annotate_frame(

                        frame,

                        result

                    )


                # ------------------------------------------------
                # FACE RECOGNITION
                # ------------------------------------------------

                if (

                    FACE_REC_ENABLED

                    and face_recognizer

                ):

                    try:

                        faces = (
                            face_recognizer
                            .recognize(
                                frame
                            )
                        )


                        for face in faces:

                            name = (
                                face[
                                    "name"
                                ]
                            )


                            left, top, right, bottom = (

                                face[
                                    "bbox"
                                ]

                            )


                            # ------------------------------------
                            # FACE COLOR
                            # ------------------------------------

                            if (
                                name
                                != "Unknown"
                            ):

                                color = (
                                    0,
                                    255,
                                    0
                                )

                            else:

                                color = (
                                    0,
                                    0,
                                    255
                                )


                            # ------------------------------------
                            # FACE BOX
                            # ------------------------------------

                            cv2.rectangle(

                                frame,

                                (
                                    left,
                                    top
                                ),

                                (
                                    right,
                                    bottom
                                ),

                                color,

                                2,

                            )


                            # ------------------------------------
                            # NAME
                            # ------------------------------------

                            (
                                tw,
                                th
                            ), _ = (
                                cv2.getTextSize(

                                    name,

                                    cv2.FONT_HERSHEY_SIMPLEX,

                                    0.7,

                                    2,

                                )
                            )


                            label_top = max(

                                top
                                - th
                                - 14,

                                0

                            )


                            cv2.rectangle(

                                frame,

                                (
                                    left,
                                    label_top
                                ),

                                (
                                    left
                                    + tw
                                    + 10,

                                    top
                                ),

                                color,

                                -1,

                            )


                            cv2.putText(

                                frame,

                                name,

                                (
                                    left + 5,
                                    top - 7
                                ),

                                cv2.FONT_HERSHEY_SIMPLEX,

                                0.7,

                                (
                                    255,
                                    255,
                                    255
                                ),

                                2,

                                cv2.LINE_AA,

                            )


                            # ------------------------------------
                            # GREETING
                            # ------------------------------------

                            if (
                                name
                                != "Unknown"
                            ):

                                now_face = (
                                    time.time()
                                )


                                previous_greeting = (
                                    last_face_greetings
                                    .get(
                                        name,
                                        0
                                    )
                                )


                                if (

                                    now_face
                                    - previous_greeting

                                    >=
                                    FACE_GREETING_COOLDOWN

                                ):

                                    template = (
                                        face_greetings
                                        .get(
                                            language,

                                            "Hello {name}"
                                        )
                                    )


                                    greeting = (
                                        template
                                        .format(
                                            name=name
                                        )
                                    )


                                    speak(

                                        greeting,

                                        language

                                    )


                                    last_face_greetings[
                                        name
                                    ] = (
                                        now_face
                                    )


                    except Exception as e:

                        print(
                            f"[Face Error] {e}"
                        )


                prev = time.time()


            # =================================================
            # DETECTING INDICATOR
            # =================================================

            cv2.circle(

                frame,

                (
                    25,
                    25
                ),

                8,

                (
                    0,
                    255,
                    0
                ),

                -1

            )


            cv2.putText(

                frame,

                "DETECTING",

                (
                    40,
                    32
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (
                    0,
                    255,
                    0
                ),

                2,

                cv2.LINE_AA

            )


        else:

            # =================================================
            # STANDBY
            # =================================================

            cv2.circle(

                frame,

                (
                    25,
                    25
                ),

                8,

                (
                    0,
                    0,
                    255
                ),

                -1

            )


            cv2.putText(

                frame,

                "STANDBY",

                (
                    40,
                    32
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (
                    0,
                    0,
                    255
                ),

                2,

                cv2.LINE_AA

            )


        # ====================================================
        # CAMERA INFO
        # ====================================================

        height, width = (
            frame.shape[:2]
        )


        cv2.putText(

            frame,

            f"Capture: {stats['capture_fps']} fps",

            (
                width - 220,
                28
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.5,

            (
                255,
                255,
                255
            ),

            1,

            cv2.LINE_AA

        )


        cv2.putText(

            frame,

            f"Inference: {stats['inference_fps']:.2f}/s",

            (
                width - 220,
                52
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.5,

            (
                100,
                200,
                255
            ),

            1,

            cv2.LINE_AA

        )


        cv2.putText(

            frame,

            f"Classes: {len(VOCABULARY)}",

            (
                width - 180,
                74
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.4,

            (
                100,
                200,
                255
            ),

            1,

            cv2.LINE_AA

        )


        # ====================================================
        # SAVE FRAME
        # ====================================================

        with frame_lock:

            current_frame = (
                frame.copy()
            )


        # ====================================================
        # JPEG
        # ====================================================

        success, jpeg = cv2.imencode(

            ".jpg",

            frame,

            [
                cv2.IMWRITE_JPEG_QUALITY,
                85
            ]

        )


        if not success:

            continue


        yield (

            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg.tobytes()
            + b"\r\n\r\n"

        )


    # ========================================================
    # RELEASE
    # ========================================================

    cap.release()


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# VIDEO
# ============================================================

@app.route("/video_feed")
def video_feed():

    return Response(

        generate_feed(),

        mimetype=(
            "multipart/"
            "x-mixed-replace;"
            "boundary=frame"
        )

    )


# ============================================================
# START
# ============================================================

@app.route(
    "/start_detection",
    methods=["POST"]
)
def start_detection():

    global running

    running = True

    stats[
        "session_start"
    ] = datetime.now().strftime(
        "%H:%M:%S"
    )

    return jsonify({

        "status":
            "running"

    })


# ============================================================
# STOP
# ============================================================

@app.route(
    "/stop_detection",
    methods=["POST"]
)
def stop_detection():

    global running

    running = False

    return jsonify({

        "status":
            "stopped"

    })


# ============================================================
# LANGUAGE
# ============================================================

@app.route(
    "/set_language",
    methods=["POST"]
)
def set_language_route():

    global language

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    selected = data.get(

        "language",

        "English"

    )


    if selected not in language_code_map:

        selected = "English"


    language = selected


    return jsonify({

        "status":
            "success",

        "language":
            language

    })


# ============================================================
# CONFIDENCE
# ============================================================

@app.route(
    "/set_confidence",
    methods=["POST"]
)
def set_confidence():

    global confidence_threshold


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        value = float(

            data.get(
                "threshold",
                0.15
            )

        )


        confidence_threshold = min(

            max(
                value,
                0.05
            ),

            0.95

        )


    except Exception:

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid confidence"

        }), 400


    return jsonify({

        "status":
            "success",

        "confidence":
            confidence_threshold

    })


# ============================================================
# INTERVAL
# ============================================================

@app.route(
    "/set_interval",
    methods=["POST"]
)
def set_interval_route():

    global INTERVAL


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        value = float(

            data.get(
                "interval",
                1.5
            )

        )


        INTERVAL = min(

            max(
                value,
                0.2
            ),

            10.0

        )


    except Exception:

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid interval"

        }), 400


    return jsonify({

        "status":
            "success",

        "interval":
            INTERVAL

    })


# ============================================================
# RESOLUTION
# ============================================================

@app.route(
    "/set_resolution",
    methods=["POST"]
)
def set_resolution():

    global IMG_SIZE


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        value = int(

            data.get(
                "resolution",
                640
            )

        )


        allowed = {

            416,
            640,
            832,
            1280

        }


        if value not in allowed:

            value = 640


        IMG_SIZE = value


    except Exception:

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid resolution"

        }), 400


    return jsonify({

        "status":
            "success",

        "resolution":
            IMG_SIZE

    })


# ============================================================
# MODEL
# ============================================================

@app.route(
    "/set_model",
    methods=["POST"]
)
def set_model():

    global model
    global MODEL_NAME


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    selected_model = data.get(

        "model",

        "yolov8s-worldv2.pt"

    )


    try:
        selected_model = normalize_model_name(
            selected_model
        )
    except ValueError as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


    try:

        new_model = YOLO(
            selected_model
        )


        # ----------------------------------------------------
        # YOLO WORLD
        # ----------------------------------------------------

        if "world" in (
            selected_model.lower()
        ):

            new_model.set_classes(
                VOCABULARY
            )


        model = new_model

        MODEL_NAME = (
            selected_model
        )


        stats[
            "model_name"
        ] = MODEL_NAME


        return jsonify({

            "status":
                "success",

            "model":
                MODEL_NAME

        })


    except Exception as e:

        print(
            f"[Model Error] {e}"
        )


        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# SPEECH TOGGLE
# ============================================================

@app.route(
    "/toggle_speech",
    methods=["POST"]
)
def toggle_speech():

    global speech_enabled


    speech_enabled = (
        not speech_enabled
    )


    # --------------------------------------------------------
    # Clear pending speech when disabled.
    # --------------------------------------------------------

    if not speech_enabled:

        while True:

            try:

                speech_queue.get_nowait()

                speech_queue.task_done()

            except queue.Empty:

                break


    return jsonify({

        "status":
            "success",

        "speech_enabled":
            speech_enabled

    })


# ============================================================
# SPEECH COOLDOWN
# ============================================================

@app.route(
    "/set_speech_cooldown",
    methods=["POST"]
)
def set_speech_cooldown():

    global SPEECH_COOLDOWN


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        SPEECH_COOLDOWN = min(

            max(

                float(
                    data.get(
                        "cooldown",
                        4.5
                    )
                ),

                1.0

            ),

            30.0

        )


    except Exception:

        return jsonify({

            "status":
                "error"

        }), 400


    return jsonify({

        "status":
            "success",

        "cooldown":
            SPEECH_COOLDOWN

    })


# ============================================================
# MAX SPEAK OBJECTS
# ============================================================

@app.route(
    "/set_max_speak_objects",
    methods=["POST"]
)
def set_max_speak_objects():

    global MAX_OBJECTS_TO_SPEAK


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        MAX_OBJECTS_TO_SPEAK = min(

            max(

                int(
                    data.get(
                        "max_objects",
                        2
                    )
                ),

                1

            ),

            4

        )


    except Exception:

        return jsonify({

            "status":
                "error"

        }), 400


    return jsonify({

        "status":
            "success",

        "max_objects":
            MAX_OBJECTS_TO_SPEAK

    })


# ============================================================
# CUSTOM VOCABULARY
# ============================================================

@app.route(
    "/set_custom_vocab",
    methods=["POST"]
)
def set_custom_vocab():

    global VOCABULARY


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    new_words = data.get(
        "words",
        []
    )


    if not isinstance(
        new_words,
        list
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "words must be a list"

        }), 400


    cleaned = []


    for word in new_words:

        word = str(
            word
        ).strip()


        if word:

            cleaned.append(
                word
            )


    if cleaned:

        VOCABULARY = list(

            dict.fromkeys(

                VOCABULARY
                + cleaned

            )

        )


        try:

            model.set_classes(
                VOCABULARY
            )

        except Exception as e:

            print(
                f"[Vocabulary Error] {e}"
            )


    return jsonify({

        "status":
            "success",

        "total_classes":
            len(VOCABULARY)

    })


# ============================================================
# ALERT OBJECTS
# ============================================================

@app.route(
    "/set_alerts",
    methods=["POST"]
)
def set_alerts():

    global alert_objects


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    objects = data.get(
        "objects",
        []
    )


    if not isinstance(
        objects,
        list
    ):

        objects = []


    alert_objects = {

        str(
            obj
        ).strip()

        for obj in objects

        if str(
            obj
        ).strip()

    }


    return jsonify({

        "status":
            "success",

        "alerts":
            sorted(
                alert_objects
            ),

        "total":
            len(
                alert_objects
            )

    })


# ============================================================
# LANGUAGES
# ============================================================

@app.route(
    "/get_languages",
    methods=["GET"]
)
def get_languages():

    indian = [

        "Hindi",
        "Gujarati",
        "Bengali",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Marathi",
        "Punjabi",
        "Odia",
        "Assamese",
        "Urdu",
        "Sindhi",
        "Konkani",
        "Maithili",
        "Dogri",
        "Bodo",
        "Santali",
        "Kashmiri",
        "Nepali",
        "Manipuri",
        "Sanskrit",

    ]


    international = [

        "English",
        "Spanish",
        "French",
        "German",
        "Japanese",
        "Chinese",
        "Korean",
        "Arabic",
        "Portuguese",
        "Russian",
        "Italian",
        "Dutch",
        "Turkish",
        "Thai",
        "Vietnamese",
        "Indonesian",
        "Swahili",
        "Polish",
        "Ukrainian",
        "Romanian",
        "Greek",
        "Czech",
        "Swedish",
        "Finnish",
        "Hungarian",
        "Norwegian",
        "Danish",
        "Hebrew",
        "Filipino",
        "Malay",
        "Burmese",
        "Sinhala",
        "Afrikaans",
        "Amharic",
        "Catalan",
        "Croatian",
        "Serbian",
        "Slovak",
        "Slovenian",
        "Estonian",
        "Latvian",
        "Lithuanian",
        "Georgian",
        "Armenian",
        "Azerbaijani",
        "Kazakh",
        "Uzbek",
        "Mongolian",
        "Khmer",
        "Lao",

    ]


    return jsonify({

        "current":
            language,

        "indian":
            indian,

        "international":
            international,

        "all":
            indian + international,

    })


# ============================================================
# LOGS
# ============================================================

@app.route(
    "/get_logs",
    methods=["GET"]
)
def get_logs():

    uptime = int(

        time.time()
        - stats[
            "uptime_start"
        ]

    )


    hours, remainder = divmod(

        uptime,

        3600

    )


    minutes, seconds = divmod(

        remainder,

        60

    )


    frequency = dict(

        sorted(

            stats[
                "object_frequency"
            ].items(),

            key=lambda x:
                x[1],

            reverse=True

        )[:20]

    )


    return jsonify({

        "logs":
            detection_log[-30:],

        "stats": {

            "total_detections":
                stats[
                    "total_detections"
                ],

            "unique_objects":
                len(
                    stats[
                        "unique_objects"
                    ]
                ),

            "unique_list":
                sorted(
                    list(
                        stats[
                            "unique_objects"
                        ]
                    )
                ),

            "fps":
                stats[
                    "fps"
                ],

            "capture_fps":
                stats[
                    "capture_fps"
                ],

            "inference_fps":
                stats[
                    "inference_fps"
                ],

            "model_name":
                stats[
                    "model_name"
                ],

            "frames_processed":
                stats[
                    "frames_processed"
                ],

            "avg_confidence":
                stats[
                    "avg_confidence"
                ],

            "last_detection_time":
                stats[
                    "last_detection_time"
                ],

            "uptime":
                (
                    f"{hours:02d}:"
                    f"{minutes:02d}:"
                    f"{seconds:02d}"
                ),

            "object_frequency":
                frequency,

            "confidence_history":
                stats[
                    "confidence_history"
                ][-30:],

            "detection_timeline":
                stats[
                    "detection_timeline"
                ][-30:],

            "speech_enabled":
                speech_enabled,

            "speech_cooldown":
                SPEECH_COOLDOWN,

            "max_speak_objects":
                MAX_OBJECTS_TO_SPEAK,

            "vocabulary_size":
                len(VOCABULARY),

            "language":
                language,

            "speech_mode":
                "concise",

            "face_recognition_enabled":
                FACE_REC_ENABLED,

            "camera_index":
                WEBCAM_INDEX,

            "camera_source":
                "Configurable camera",

        }

    })


# ============================================================
# CLEAR LOGS
# ============================================================

@app.route(
    "/clear_logs",
    methods=["POST"]
)
def clear_logs():

    global detection_log
    global heatmap_accumulator


    detection_log = []


    stats[
        "total_detections"
    ] = 0


    stats[
        "unique_objects"
    ] = set()


    stats[
        "object_frequency"
    ] = defaultdict(int)


    stats[
        "confidence_history"
    ] = []


    stats[
        "detection_timeline"
    ] = []


    stats[
        "last_detection_time"
    ] = None


    heatmap_accumulator = None


    return jsonify({

        "status":
            "success"

    })


# ============================================================
# SNAPSHOT
# ============================================================

@app.route(
    "/snapshot",
    methods=["GET"]
)
def snapshot():

    with frame_lock:

        if current_frame is not None:

            success, jpeg = cv2.imencode(

                ".jpg",

                current_frame,

                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    95
                ]

            )


            if success:

                return Response(

                    jpeg.tobytes(),

                    mimetype="image/jpeg",

                    headers={

                        "Content-Disposition":

                            (
                                "attachment; "
                                f"filename="
                                f"trinexis_"
                                f"{datetime.now().strftime('%H%M%S')}"
                                ".jpg"
                            )

                    }

                )


    return jsonify({

        "error":
            "No frame available"

    }), 404


# ============================================================
# HEATMAP
# ============================================================

@app.route(
    "/heatmap",
    methods=["GET"]
)
def get_heatmap():

    if (

        heatmap_accumulator
        is not None

    ):

        try:

            normalized = cv2.normalize(

                heatmap_accumulator,

                None,

                0,

                255,

                cv2.NORM_MINMAX

            )


            colored = cv2.applyColorMap(

                normalized.astype(
                    np.uint8
                ),

                cv2.COLORMAP_JET

            )


            success, jpeg = cv2.imencode(

                ".jpg",

                colored

            )


            if success:

                return Response(

                    jpeg.tobytes(),

                    mimetype="image/jpeg"

                )


        except Exception as e:

            print(
                f"[Heatmap Error] {e}"
            )


    return jsonify({

        "error":
            "No heatmap data"

    }), 404


# ============================================================
# EXPORT LOGS
# ============================================================

@app.route(
    "/export_logs",
    methods=["GET"]
)
def export_logs():

    data = json.dumps(

        detection_log,

        indent=2,

        ensure_ascii=False

    )


    buffer = io.BytesIO(

        data.encode(
            "utf-8"
        )

    )


    buffer.seek(0)


    return send_file(

        buffer,

        mimetype=(
            "application/json"
        ),

        as_attachment=True,

        download_name=(

            "trinexis_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ".json"

        )

    )


# ============================================================
# CLASSES
# ============================================================

@app.route(
    "/get_classes",
    methods=["GET"]
)
def get_classes():

    return jsonify({

        "classes":
            VOCABULARY,

        "total":
            len(VOCABULARY)

    })


# ============================================================
# CAMERA INFORMATION
# ============================================================

@app.route(
    "/get_camera",
    methods=["GET"]
)
def get_camera():

    return jsonify({

        "status":
            "success",

        "camera_index":
            WEBCAM_INDEX,

        "camera_source":
            "External USB Webcam",

        "width":
            CAMERA_WIDTH,

        "height":
            CAMERA_HEIGHT,

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ok",

        "service":
            "TRINEXIS",

        "model":
            MODEL_NAME,

        "camera":
            "External USB Webcam",

        "camera_index":
            WEBCAM_INDEX,

        "speech":
            speech_enabled,

        "face_recognition":
            FACE_REC_ENABLED,

        "classes":
            len(VOCABULARY),

        "languages":
            len(language_code_map),

    })


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(
    404
)
def not_found(error):

    return jsonify({

        "status":
            "error",

        "message":
            "Endpoint not found"

    }), 404


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)

    print(
        "  TRINEXIS — Intelligent Vision Platform"
    )

    print("=" * 65)

    print(
        f"  Model             : {MODEL_NAME}"
    )

    print(
        f"  Classes           : {len(VOCABULARY)}"
    )

    print(
        f"  Languages         : {len(language_code_map)}"
    )

    print(
        "  Camera            : External USB Webcam"
    )

    print(
        f"  Camera Index      : {WEBCAM_INDEX}"
    )

    print(
        f"  Resolution        : "
        f"{CAMERA_WIDTH}x{CAMERA_HEIGHT}"
    )

    print(
        "  Speech            : "
        f"{'ENABLED' if speech_enabled else 'DISABLED'}"
    )

    print(
        "  Speech Mode       : CONCISE"
    )

    print(
        f"  Speech Objects    : "
        f"{MAX_OBJECTS_TO_SPEAK}"
    )

    print(
        f"  Speech Cooldown   : "
        f"{SPEECH_COOLDOWN}s"
    )

    print(
        "  Face Recognition  : "
        f"{'ENABLED' if FACE_REC_ENABLED else 'DISABLED'}"
    )

    print(
        "  URL               : "
        "http://localhost:5000"
    )

    print("=" * 65)
    print()


    # --------------------------------------------------------
    # FLASK
    # --------------------------------------------------------

    app.run(

        debug=False,

        host=os.environ.get(
            "TRINEXIS_HOST",
            "127.0.0.1"
        ),

        port=int(
            os.environ.get(
                "TRINEXIS_PORT",
                "5000"
            )
        ),

        threaded=True

    )