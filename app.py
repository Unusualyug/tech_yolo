# LEGACY FROZEN VARIANT: app23.py is the maintained backend.
# This file is retained for historical comparison only.

import cv2
import time
import threading
import queue
import platform
import random
import json
import numpy as np
from flask import Flask, render_template, Response, jsonify, request, send_file
from ultralytics import YOLO
from datetime import datetime
from gtts import gTTS
from collections import defaultdict
import os
import io

app = Flask(__name__)

# ============================================================
#  YOLO-WORLD MODEL
# ============================================================
MODEL_NAME = "yolov8s-worldv2.pt"
print(f"[TRINEXIS] Loading {MODEL_NAME}...")
model = YOLO(MODEL_NAME)

# ============================================================
#  FACE RECOGNITION
# ============================================================
try:
    from modules.faces import FaceRecognizer
    face_recognizer = FaceRecognizer()
    FACE_REC_ENABLED = True
    print("[TRINEXIS] FaceRecognizer loaded!")
except Exception as e:
    face_recognizer = None
    FACE_REC_ENABLED = False
    print(f"[TRINEXIS] FaceRecognizer skipped: {e}")

# ============================================================
#  VOCABULARY — 500+ real-world objects
# ============================================================
VOCABULARY = [
    "person", "man", "woman", "child", "baby", "face", "hand", "eye",
    "head", "arm", "leg", "foot", "finger", "hair", "smile",
    "shirt", "t-shirt", "pants", "jeans", "dress", "skirt", "jacket",
    "coat", "hoodie", "sweater", "hat", "cap", "helmet", "glasses",
    "sunglasses", "shoe", "sneaker", "boot", "sandal", "sock",
    "glove", "scarf", "tie", "belt", "watch", "ring", "necklace",
    "earring", "bracelet", "backpack", "handbag", "purse", "wallet",
    "suitcase", "bag", "umbrella",
    "car", "truck", "bus", "motorcycle", "bicycle", "scooter",
    "train", "airplane", "helicopter", "boat", "ship", "van",
    "taxi", "ambulance", "fire truck", "police car", "tractor",
    "forklift", "wheel", "tire", "engine",
    "chair", "table", "desk", "couch", "sofa", "bed", "pillow",
    "blanket", "mattress", "shelf", "bookshelf", "cabinet", "wardrobe",
    "drawer", "door", "window", "curtain", "lamp", "chandelier",
    "mirror", "clock", "picture frame", "painting", "poster",
    "rug", "carpet", "vase", "candle", "flower pot", "plant",
    "toilet", "sink", "bathtub", "shower", "faucet", "towel",
    "trash can", "broom", "mop", "bucket",
    "cell phone", "smartphone", "laptop", "computer", "monitor",
    "keyboard", "mouse", "tablet", "ipad", "television", "tv",
    "remote control", "speaker", "headphones", "earbuds", "microphone",
    "camera", "webcam", "printer", "scanner", "router", "charger",
    "cable", "usb", "battery", "power bank", "smartwatch",
    "drone", "robot", "game controller", "console",
    "bottle", "cup", "glass", "mug", "plate", "bowl", "fork",
    "knife", "spoon", "chopsticks", "pot", "pan", "wok",
    "kettle", "teapot", "blender", "microwave", "oven", "stove",
    "refrigerator", "freezer", "toaster", "coffee maker",
    "apple", "banana", "orange", "grape", "strawberry", "watermelon",
    "lemon", "lime", "mango", "pineapple", "tomato", "potato",
    "onion", "carrot", "broccoli", "corn", "pepper", "mushroom",
    "bread", "cake", "pizza", "burger", "sandwich", "hot dog",
    "donut", "cookie", "candy", "chocolate", "ice cream",
    "egg", "cheese", "butter", "milk", "juice", "water bottle",
    "wine glass", "beer", "coffee", "tea",
    "pen", "pencil", "marker", "highlighter", "eraser", "ruler",
    "scissors", "stapler", "tape", "glue", "notebook", "notepad",
    "paper", "document", "folder", "binder", "envelope", "stamp",
    "calculator", "whiteboard", "blackboard", "projector",
    "ball", "football", "soccer ball", "basketball", "tennis ball",
    "baseball", "volleyball", "golf ball", "cricket bat",
    "tennis racket", "badminton racket", "skateboard", "surfboard",
    "snowboard", "ski", "bicycle helmet", "dumbbell", "weight",
    "yoga mat", "jump rope", "frisbee", "kite", "fishing rod",
    "dog", "cat", "bird", "fish", "horse", "cow", "pig", "sheep",
    "goat", "chicken", "duck", "rabbit", "hamster", "mouse",
    "snake", "lizard", "frog", "turtle", "butterfly", "bee",
    "ant", "spider", "elephant", "lion", "tiger", "bear",
    "monkey", "giraffe", "zebra", "deer", "fox", "wolf",
    "eagle", "owl", "parrot", "penguin", "shark", "dolphin",
    "whale", "octopus", "crab", "lobster", "snail",
    "tree", "flower", "grass", "bush", "leaf", "branch", "log",
    "rock", "stone", "mountain", "hill", "river", "lake", "ocean",
    "wave", "cloud", "sun", "moon", "star", "rain", "snow",
    "rainbow", "fire", "smoke", "sand", "beach", "path", "road",
    "bridge", "fence", "gate", "wall", "building", "house",
    "skyscraper", "tower", "tent", "flag", "sign", "traffic light",
    "street light", "bench", "mailbox", "fire hydrant", "parking meter",
    "hammer", "screwdriver", "wrench", "pliers", "drill", "saw",
    "nail", "screw", "bolt", "nut", "wire", "pipe", "ladder",
    "toolbox", "tape measure", "level", "axe", "shovel", "rake",
    "mask", "syringe", "bandage", "pill", "medicine", "thermometer",
    "stethoscope", "wheelchair", "crutch", "first aid kit",
    "fire extinguisher", "life jacket", "cone", "barrier",
    "teddy bear", "doll", "toy car", "lego", "puzzle", "balloon",
    "stuffed animal", "action figure", "board game", "dice",
    "playing card", "guitar", "piano", "drum", "violin", "flute",
    "trumpet", "book", "magazine", "newspaper", "comic",
    "toothbrush", "toothpaste", "soap", "shampoo", "comb", "brush",
    "razor", "hair dryer", "tissue", "toilet paper", "perfume",
    "lotion", "sunscreen", "lipstick", "makeup",
    "key", "lock", "coin", "money", "credit card", "id card",
    "passport", "ticket", "receipt", "label", "tag", "sticker",
    "button", "zipper", "hook", "hanger", "basket", "box",
    "crate", "barrel", "jar", "can", "tin", "container",
    "lid", "cap", "straw", "napkin", "tablecloth", "apron",
    "suit", "uniform", "costume", "crown", "medal", "trophy",
    "gift", "ribbon", "wreath", "lantern", "torch", "lighter",
    "match", "ashtray", "telescope", "binoculars", "compass",
    "map", "globe", "hourglass", "magnet", "sponge",
]

VOCABULARY = list(dict.fromkeys(VOCABULARY))
model.set_classes(VOCABULARY)
print(f"[TRINEXIS] {len(VOCABULARY)} classes loaded!")

# ============================================================
#  GLOBAL STATE
# ============================================================
FOCAL_LENGTH = 360
KNOWN_WIDTH = 60
INTERVAL = 1.5
prev = 0
running = False
confidence_threshold = 0.15
language = "English"
detection_log = []
IMG_SIZE = 640

# ============================================================
#  CAMERA CONFIGURATION
# ============================================================
# camera_test.py found index 1 and 3 as valid cameras.
# Index 1 is selected as the default external webcam.
CAMERA_INDEX = 1

current_frame = None
frame_lock = threading.Lock()
heatmap_accumulator = None

stats = {
    "total_detections": 0,
    "unique_objects": set(),
    "session_start": None,
    "fps": 0,
    "model_name": MODEL_NAME,
    "frames_processed": 0,
    "avg_confidence": 0,
    "last_detection_time": None,
    "object_frequency": defaultdict(int),
    "confidence_history": [],
    "detection_timeline": [],
    "uptime_start": time.time()
}

# ============================================================
#  ALL INDIAN REGIONAL LANGUAGES + INTERNATIONAL (30+ Languages)
# ============================================================
language_code_map = {
    # --- Indian Regional Languages ---
    "Hindi": "hi",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Odia": "or",           # Odia / Oriya
    "Assamese": "as",       # Assamese (limited gTTS support, falls back to bn)
    "Urdu": "ur",
    "Sindhi": "sd",
    "Konkani": "gom",       # Konkani (Goan)
    "Maithili": "mai",
    "Dogri": "doi",
    "Bodo": "brx",
    "Santali": "sat",
    "Kashmiri": "ks",
    "Nepali": "ne",
    "Manipuri": "mni-Mtei",
    "Sanskrit": "sa",

    # --- International Languages ---
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
#  SMART TRANSLATIONS — Full sentence for multiple objects
#  Uses {objects} for the combined list, {count} for total
# ============================================================
translations = {
    # --- Indian Regional ---
    "Hindi": "कुल {count} वस्तुएं मिलीं। {objects}",
    "Gujarati": "કુલ {count} વસ્તુઓ મળી। {objects}",
    "Bengali": "মোট {count}টি বস্তু পাওয়া গেছে। {objects}",
    "Tamil": "மொத்தம் {count} பொருட்கள் கண்டறியப்பட்டன। {objects}",
    "Telugu": "మొత్తం {count} వస్తువులు కనుగొనబడ్డాయి। {objects}",
    "Kannada": "ಒಟ್ಟು {count} ವಸ್ತುಗಳು ಪತ್ತೆಯಾಗಿವೆ। {objects}",
    "Malayalam": "ആകെ {count} വസ്തുക്കൾ കണ്ടെത്തി। {objects}",
    "Marathi": "एकूण {count} वस्तू सापडल्या। {objects}",
    "Punjabi": "ਕੁੱਲ {count} ਵਸਤੂਆਂ ਮਿਲੀਆਂ। {objects}",
    "Odia": "ମୋଟ {count}ଟି ଜିନିଷ ଚିହ୍ନଟ ହୋଇଛି। {objects}",
    "Assamese": "মুঠ {count}টা বস্তু পোৱা গৈছে। {objects}",
    "Urdu": "کل {count} چیزیں ملیں۔ {objects}",
    "Sindhi": "ڪُل {count} شيون مليون. {objects}",
    "Konkani": "एकूण {count} वस्तू सापडल्यो। {objects}",
    "Maithili": "कुल {count} वस्तु भेटल। {objects}",
    "Dogri": "कुल {count} चीजां मिल्लियां। {objects}",
    "Bodo": "जम्मा {count} बस्तु मोन्नाय। {objects}",
    "Santali": "ᱡᱚᱛᱚ {count} ᱡᱤᱱᱤᱥ ᱧᱟᱢᱮᱫᱟ। {objects}",
    "Kashmiri": "کُل {count} چیزٕ لبِتھ۔ {objects}",
    "Nepali": "जम्मा {count} वस्तुहरू फेला पर्यो। {objects}",
    "Manipuri": "পুম্নমক {count} পোৎলম শিল্লে। {objects}",
    "Sanskrit": "समग्रं {count} वस्तूनि अन्वेषितानि। {objects}",

    # --- International ---
    "English": "Detected {count} objects in the scene. {objects}",
    "Spanish": "Se detectaron {count} objetos en la escena. {objects}",
    "French": "Détecté {count} objets dans la scène. {objects}",
    "German": "{count} Objekte in der Szene erkannt. {objects}",
    "Japanese": "シーン内で{count}個のオブジェクトを検出しました。{objects}",
    "Chinese": "在场景中检测到{count}个物体。{objects}",
    "Korean": "장면에서 {count}개의 물체가 감지되었습니다. {objects}",
    "Arabic": "تم اكتشاف {count} كائنات في المشهد. {objects}",
    "Portuguese": "Detectados {count} objetos na cena. {objects}",
    "Russian": "Обнаружено {count} объектов на сцене. {objects}",
    "Italian": "Rilevati {count} oggetti nella scena. {objects}",
    "Dutch": "{count} objecten gedetecteerd in de scène. {objects}",
    "Turkish": "Sahnede {count} nesne tespit edildi. {objects}",
    "Thai": "ตรวจพบ {count} วัตถุในฉาก {objects}",
    "Vietnamese": "Phát hiện {count} đối tượng trong cảnh. {objects}",
    "Indonesian": "Terdeteksi {count} objek dalam adegan. {objects}",
    "Swahili": "Vitu {count} vimegunduliwa kwenye eneo. {objects}",
    "Polish": "Wykryto {count} obiektów na scenie. {objects}",
    "Ukrainian": "Виявлено {count} об'єктів на сцені. {objects}",
    "Romanian": "Detectate {count} obiecte în scenă. {objects}",
    "Greek": "Εντοπίστηκαν {count} αντικείμενα στη σκηνή. {objects}",
    "Czech": "Detekováno {count} objektů ve scéně. {objects}",
    "Swedish": "{count} objekt upptäckta i scenen. {objects}",
    "Finnish": "Havaittu {count} kohdetta näkymässä. {objects}",
    "Hungarian": "{count} objektum észlelve a jelenetben. {objects}",
    "Norwegian": "{count} objekter oppdaget i scenen. {objects}",
    "Danish": "{count} objekter registreret i scenen. {objects}",
    "Hebrew": "זוהו {count} אובייקטים בסצנה. {objects}",
    "Filipino": "Nakakita ng {count} bagay sa eksena. {objects}",
    "Malay": "{count} objek dikesan dalam adegan. {objects}",
    "Burmese": "မြင်ကွင်းထဲတွင် အရာဝတ္ထု {count} ခု တွေ့ရှိသည်။ {objects}",
    "Sinhala": "දර්ශනයේ වස්තූන් {count}ක් හඳුනාගන්නා ලදී. {objects}",
    "Afrikaans": "{count} voorwerpe in die toneel bespeur. {objects}",
    "Amharic": "በትዕይንቱ ውስጥ {count} ዕቃዎች ተገኝተዋል። {objects}",
    "Catalan": "Detectats {count} objectes a l'escena. {objects}",
    "Croatian": "Otkriveno {count} objekata u sceni. {objects}",
    "Serbian": "Откривено {count} објеката у сцени. {objects}",
    "Slovak": "Zistených {count} objektov v scéne. {objects}",
    "Slovenian": "Zaznanih {count} predmetov v prizoru. {objects}",
    "Estonian": "Stseenis tuvastati {count} objekti. {objects}",
    "Latvian": "Ainā konstatēti {count} objekti. {objects}",
    "Lithuanian": "Scenoje aptikta {count} objektų. {objects}",
    "Georgian": "სცენაში აღმოჩენილია {count} ობიექტი. {objects}",
    "Armenian": "Տեսարանում հայտնաբերվել է {count} օբյdelays. {objects}",
    "Azerbaijani": "Səhnədə {count} obyekt aşkar edildi. {objects}",
    "Kazakh": "Көріністе {count} нысан анықталды. {objects}",
    "Uzbek": "Sahnada {count} ta obyekt aniqlandi. {objects}",
    "Mongolian": "Тайзнаас {count} объект илрүүлсэн. {objects}",
    "Khmer": "រកឃើញវត្ថុ {count} នៅក្នុងឈុត។ {objects}",
    "Lao": "ກວດພົບ {count} ວັດຖຸໃນສາກ. {objects}",
}

# Per-object detail templates (for building the {objects} string)
object_detail_templates = {
    "Hindi": "{name} {distance} सेंटीमीटर दूर, विश्वास {confidence} प्रतिशत",
    "Gujarati": "{name} {distance} સેન્ટીમીટર દૂર, વિશ્વાસ {confidence} ટકા",
    "Bengali": "{name} {distance} সেন্টিমিটার দূরে, আত্মবিশ্বাস {confidence} শতাংশ",
    "Tamil": "{name} {distance} சென்டிமீட்டர் தொலைவில், நம்பிக்கை {confidence} சதவீதம்",
    "Telugu": "{name} {distance} సెంటీమీటర్ల దూరంలో, విశ్వాసం {confidence} శాతం",
    "Kannada": "{name} {distance} ಸೆಂಟಿಮೀಟರ್ ದೂರದಲ್ಲಿ, ವಿಶ್ವಾಸ {confidence} ಶೇಕಡಾ",
    "Malayalam": "{name} {distance} സെന്റിമീറ്റർ അകലെ, ആത്മവിശ്വാസം {confidence} ശതമാനം",
    "Marathi": "{name} {distance} सेंटीमीटर अंतरावर, आत्मविश्वास {confidence} टक्के",
    "Punjabi": "{name} {distance} ਸੈਂਟੀਮੀਟਰ ਦੂਰ, ਭਰੋਸਾ {confidence} ਪ੍ਰਤੀਸ਼ਤ",
    "Odia": "{name} {distance} ସେଣ୍ଟିମିଟର ଦୂରରେ, ବିଶ୍ୱାସ {confidence} ପ୍ରତିଶତ",
    "Urdu": "{name} {distance} سینٹی میٹر دور، اعتماد {confidence} فیصد",
    "Nepali": "{name} {distance} सेन्टिमिटर टाढा, विश्वास {confidence} प्रतिशत",
    "English": "{name} at {distance} centimeters away with {confidence} percent confidence",
    "Spanish": "{name} a {distance} centímetros de distancia con {confidence} por ciento de confianza",
    "French": "{name} à {distance} centimètres avec {confidence} pour cent de confiance",
    "German": "{name} bei {distance} Zentimetern Entfernung mit {confidence} Prozent Vertrauen",
    "Japanese": "{name}が{distance}センチメートル先に{confidence}パーセントの確信度で検出",
    "Chinese": "{name}在{distance}厘米处，置信度{confidence}百分比",
    "Korean": "{name}이(가) {distance}센티미터 거리에 {confidence}퍼센트 신뢰도로 감지됨",
    "Arabic": "{name} على بعد {distance} سنتيمتر بثقة {confidence} بالمائة",
    "Portuguese": "{name} a {distance} centímetros com {confidence} por cento de confiança",
    "Russian": "{name} на расстоянии {distance} сантиметров с уверенностью {confidence} процентов",
    "Italian": "{name} a {distance} centimetri con {confidence} percento di fiducia",
}

random.seed(42)
detection_colors = [
    (random.randint(60, 255), random.randint(60, 255), random.randint(60, 255))
    for _ in range(600)
]

# ============================================================
#  SMART SPEECH BUILDER — Announces ALL objects naturally
# ============================================================
def build_speech_text(annotated_objects, lang):
    """
    Builds a complete, natural-sounding sentence listing ALL detected objects
    with their distances and confidence levels.
    """
    count = len(annotated_objects)
    if count == 0:
        return ""

    # Get the per-object detail template (fallback to English)
    detail_tpl = object_detail_templates.get(lang, object_detail_templates["English"])

    # Build individual object descriptions
    object_descriptions = []
    for obj in annotated_objects:
        desc = detail_tpl.format(
            name=obj["name"],
            distance=f"{obj['distance']:.0f}",
            confidence=f"{obj['confidence'] * 100:.0f}"
        )
        object_descriptions.append(desc)

    # Join all object descriptions with natural separators
    if lang in ["Japanese", "Chinese", "Korean"]:
        # CJK languages use different punctuation
        objects_str = "。".join(object_descriptions)
    elif lang in ["Arabic", "Urdu", "Kashmiri", "Sindhi"]:
        # RTL languages
        objects_str = "، ".join(object_descriptions)
    else:
        objects_str = ". ".join(object_descriptions)

    # Get the main sentence template (fallback to English)
    main_tpl = translations.get(lang, translations["English"])

    # Build the final complete sentence
    full_text = main_tpl.format(count=count, objects=objects_str)

    return full_text


# ============================================================
#  SYNCHRONOUS SPEECH SYSTEM — Plays completely before next
# ============================================================
speech_queue = queue.Queue()
speech_enabled = True
last_spoken_time = 0
SPEECH_COOLDOWN = 4.0  # seconds between announcements
MAX_OBJECTS_TO_SPEAK = 8  # Limit to prevent 60-second speeches

def play_audio_sync(filepath):
    """Play audio file synchronously (blocks until finished) on any OS."""
    sys_type = platform.system()
    try:
        if sys_type == "Windows":
            import ctypes
            # Windows MCI — plays MP3 synchronously, no popup windows
            alias = f"tts_{int(time.time()*1000)}"
            ctypes.windll.winmm.mciSendStringW(
                f'open "{filepath}" type mpegvideo alias {alias}', None, 0, 0
            )
            ctypes.windll.winmm.mciSendStringW(
                f'play {alias} wait', None, 0, 0
            )
            ctypes.windll.winmm.mciSendStringW(
                f'close {alias}', None, 0, 0
            )
        elif sys_type == "Darwin":
            # macOS — afplay blocks until done
            os.system(f'afplay "{filepath}"')
        else:
            # Linux — try mpg321 first, then mpg123, then aplay via ffmpeg
            os.system(
                f'mpg321 "{filepath}" > /dev/null 2>&1 || '
                f'mpg123 "{filepath}" > /dev/null 2>&1 || '
                f'ffplay -nodisp -autoexit "{filepath}" > /dev/null 2>&1'
            )
    except Exception as e:
        print(f"[Audio Playback Error] {e}")


def speech_worker():
    """Single sequential worker — ensures one announcement finishes before the next starts."""
    while True:
        item = speech_queue.get()
        if item is None:
            break

        text, lang = item
        fn = f"speech_trinexis_{threading.current_thread().ident}.mp3"

        try:
            code = language_code_map.get(lang, "en")

            # Some languages may not be supported by gTTS; fallback gracefully
            try:
                tts = gTTS(text=text, lang=code, slow=False)
            except Exception:
                # Fallback to English if the language code is unsupported
                print(f"[TTS] Language '{lang}' ({code}) not supported by gTTS, falling back to English")
                tts = gTTS(text=text, lang="en", slow=False)

            tts.save(fn)
            play_audio_sync(fn)

        except Exception as e:
            print(f"[TTS Worker Error] {e}")
        finally:
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            speech_queue.task_done()


# Exactly ONE worker thread — sequential, no overlap
threading.Thread(target=speech_worker, daemon=True).start()


def speak(text, lang):
    """
    Rate-limited speech dispatcher.
    Clears any stale backlog so only the latest detection is announced.
    """
    global last_spoken_time
    now = time.time()

    if not speech_enabled:
        return

    if now - last_spoken_time < SPEECH_COOLDOWN:
        return

    # Flush stale queued items
    while not speech_queue.empty():
        try:
            speech_queue.get_nowait()
            speech_queue.task_done()
        except queue.Empty:
            break

    speech_queue.put((text, lang))
    last_spoken_time = now


# ============================================================
#  HEATMAP
# ============================================================
def update_heatmap(shape, boxes):
    global heatmap_accumulator
    if heatmap_accumulator is None:
        heatmap_accumulator = np.zeros(shape[:2], dtype=np.float32)
    for b in boxes:
        cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
        cv2.circle(heatmap_accumulator, (cx, cy), 35, 1, -1)
    heatmap_accumulator *= 0.995


# ============================================================
#  DETECTION
# ============================================================
def perform_detection(frame, conf=0.15):
    results = model.predict(
        source=frame,
        conf=conf,
        imgsz=IMG_SIZE,
        iou=0.5,
        max_det=500,
        verbose=False
    )
    return results[0] if results and len(results[0].boxes) > 0 else None


def annotate_frame(frame, result):
    global detection_log, stats
    annotated = []
    boxes_hm = []
    confs = []

    for bbox in result.boxes:
        conf = float(bbox.conf[0])
        class_id = int(bbox.cls[0])
        class_name = result.names.get(class_id, f"obj_{class_id}")
        x1, y1, x2, y2 = [int(v) for v in bbox.xyxy[0]]
        w = max(x2 - x1, 1)
        h = max(y2 - y1, 1)
        distance_cm = (KNOWN_WIDTH * FOCAL_LENGTH) / w
        color = detection_colors[class_id % len(detection_colors)]

        boxes_hm.append((x1, y1, x2, y2))
        confs.append(conf)

        # Glass fill overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)

        # Border
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Corner accents
        cl = min(20, w // 4, h // 4)
        for (cx, cy, dx, dy) in [
            (x1, y1, 1, 1), (x2, y1, -1, 1),
            (x1, y2, 1, -1), (x2, y2, -1, -1)
        ]:
            cv2.line(frame, (cx, cy), (cx + cl * dx, cy), color, 3)
            cv2.line(frame, (cx, cy), (cx, cy + cl * dy), color, 3)

        # Confidence bar
        cv2.rectangle(frame, (x1, y2 + 3), (x2, y2 + 8), (30, 30, 30), -1)
        cv2.rectangle(frame, (x1, y2 + 3), (x1 + int(w * conf), y2 + 8), color, -1)

        # Label
        label = f"{class_name} {conf:.0%} | {distance_cm:.0f}cm"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(frame, (x1, y1 - th - 12), (x1 + tw + 10, y1), color, -1)
        cv2.putText(frame, label, (x1 + 5, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Center dot
        cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 3, color, -1)

        annotated.append({
            "name": class_name,
            "confidence": round(conf, 3),
            "distance": round(distance_cm, 1)
        })

        stats["total_detections"] += 1
        stats["unique_objects"].add(class_name)
        stats["object_frequency"][class_name] += 1

    update_heatmap(frame.shape, boxes_hm)

    if annotated:
        now = datetime.now()
        avg_c = round(sum(confs) / len(confs), 3)

        detection_log.append({
            "timestamp": now.strftime("%H:%M:%S"),
            "objects": annotated,
            "total_in_frame": len(annotated),
            "avg_confidence": avg_c
        })
        if len(detection_log) > 500:
            detection_log = detection_log[-500:]

        stats["last_detection_time"] = now.strftime("%H:%M:%S")
        stats["avg_confidence"] = avg_c
        stats["confidence_history"].append(avg_c)
        if len(stats["confidence_history"]) > 100:
            stats["confidence_history"] = stats["confidence_history"][-100:]
        stats["detection_timeline"].append({
            "time": now.strftime("%H:%M:%S"),
            "count": len(annotated)
        })
        if len(stats["detection_timeline"]) > 60:
            stats["detection_timeline"] = stats["detection_timeline"][-60:]

        # Build and speak a COMPLETE sentence describing ALL objects
        # Sort by confidence (highest first), limit to avoid absurdly long speech
        sorted_objects = sorted(annotated, key=lambda x: x["confidence"], reverse=True)
        objects_to_speak = sorted_objects[:MAX_OBJECTS_TO_SPEAK]
        speech_text = build_speech_text(objects_to_speak, language)

        if speech_text:
            speak(speech_text, language)

    # Object count overlay
    cv2.putText(frame, f"Objects: {len(annotated)}", (10, frame.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    return frame


# ============================================================
#  VIDEO FEED + FACE RECOGNITION
# ============================================================
def generate_feed():
    global running, prev, stats, current_frame
    # Use the validated external webcam from camera_test.py.
    # Camera test result: index 1 and 3 work; index 1 is the preferred webcam.
    print(f"[TRINEXIS] Opening webcam at camera index {CAMERA_INDEX}...")

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if cap.isOpened():
        print(f"[TRINEXIS] Webcam connected successfully: index {CAMERA_INDEX}")
    else:
        print(f"[TRINEXIS] Failed to open webcam index {CAMERA_INDEX}")

    if not cap or not cap.isOpened():
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "NO CAMERA", (180, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        _, j = cv2.imencode('.jpg', blank)
        fb = j.tobytes()
        while True:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + fb + b'\r\n\r\n'
            time.sleep(1)
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    fps_c = 0
    fps_t = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        fps_c += 1
        if time.time() - fps_t >= 1.0:
            stats["fps"] = fps_c
            fps_c = 0
            fps_t = time.time()
        stats["frames_processed"] += 1

        if running:
            if time.time() - prev >= INTERVAL:
                # 1. YOLO-World Object Detection
                det = perform_detection(frame, confidence_threshold)
                if det:
                    frame = annotate_frame(frame, det)

                # 2. Face Recognition
                if FACE_REC_ENABLED and face_recognizer:
                    try:
                        faces = face_recognizer.recognize(frame)
                        for face in faces:
                            name = face["name"]
                            left, top, right, bottom = face["bbox"]
                            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

                            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                            # Name label with background
                            (tw, th), _ = cv2.getTextSize(
                                name, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                            )
                            cv2.rectangle(
                                frame, (left, top - th - 14),
                                (left + tw + 10, top), color, -1
                            )
                            cv2.putText(
                                frame, name, (left + 5, top - 7),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (255, 255, 255), 2, cv2.LINE_AA
                            )

                            if name != "Unknown":
                                greetings = {
                                    "Hindi": f"नमस्ते {name}",
                                    "Gujarati": f"નમસ્તે {name}",
                                    "Bengali": f"নমস্কার {name}",
                                    "Tamil": f"வணக்கம் {name}",
                                    "Telugu": f"నమస్కారం {name}",
                                    "Kannada": f"ನಮಸ್ಕಾರ {name}",
                                    "Malayalam": f"നമസ്കാരം {name}",
                                    "Marathi": f"नमस्कार {name}",
                                    "Punjabi": f"ਸਤ ਸ੍ਰੀ ਅਕਾਲ {name}",
                                    "Odia": f"ନମସ୍କାର {name}",
                                    "Urdu": f"السلام علیکم {name}",
                                    "Nepali": f"नमस्ते {name}",
                                    "Japanese": f"こんにちは {name}",
                                    "Chinese": f"你好 {name}",
                                    "Korean": f"안녕하세요 {name}",
                                    "Arabic": f"مرحبا {name}",
                                    "French": f"Bonjour {name}",
                                    "German": f"Hallo {name}",
                                    "Spanish": f"Hola {name}",
                                    "Portuguese": f"Olá {name}",
                                    "Russian": f"Привет {name}",
                                    "Italian": f"Ciao {name}",
                                }
                                greeting = greetings.get(language, f"Hello {name}")
                                speak(greeting, language)

                    except Exception as e:
                        print(f"[Face Error] {e}")

                prev = time.time()

            cv2.circle(frame, (25, 25), 8, (0, 255, 0), -1)
            cv2.putText(frame, "DETECTING", (40, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            cv2.circle(frame, (25, 25), 8, (0, 0, 255), -1)
            cv2.putText(frame, "STANDBY", (40, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

        h, w = frame.shape[:2]
        cv2.putText(frame, f"FPS: {stats['fps']}", (w - 120, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Classes: {len(VOCABULARY)}", (w - 120, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 200, 255), 1, cv2.LINE_AA)

        with frame_lock:
            current_frame = frame.copy()

        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'

    cap.release()


# ============================================================
#  ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global running
    running = True
    stats["session_start"] = datetime.now().strftime("%H:%M:%S")
    return jsonify({"status": "running"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global running
    running = False
    return jsonify({"status": "stopped"})

@app.route('/set_language', methods=['POST'])
def set_language_route():
    global language
    language = request.json.get('language', 'English')
    return jsonify({"status": "success", "language": language})

@app.route('/set_confidence', methods=['POST'])
def set_confidence():
    global confidence_threshold
    confidence_threshold = float(request.json.get('threshold', 0.15))
    return jsonify({"status": "success"})

@app.route('/set_interval', methods=['POST'])
def set_interval_route():
    global INTERVAL
    INTERVAL = float(request.json.get('interval', 1.5))
    return jsonify({"status": "success"})

@app.route('/set_resolution', methods=['POST'])
def set_resolution():
    global IMG_SIZE
    IMG_SIZE = int(request.json.get('resolution', 640))
    return jsonify({"status": "success"})

@app.route('/set_model', methods=['POST'])
def set_model():
    global model, MODEL_NAME
    m = request.json.get('model', 'yolov8s-worldv2.pt')
    try:
        model = YOLO(m)
        if 'world' in m.lower():
            model.set_classes(VOCABULARY)
        MODEL_NAME = m
        stats["model_name"] = m
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/toggle_speech', methods=['POST'])
def toggle_speech():
    global speech_enabled
    speech_enabled = not speech_enabled
    return jsonify({"status": "success", "speech_enabled": speech_enabled})

@app.route('/set_speech_cooldown', methods=['POST'])
def set_speech_cooldown():
    global SPEECH_COOLDOWN
    SPEECH_COOLDOWN = float(request.json.get('cooldown', 4.0))
    return jsonify({"status": "success", "cooldown": SPEECH_COOLDOWN})

@app.route('/set_max_speak_objects', methods=['POST'])
def set_max_speak_objects():
    global MAX_OBJECTS_TO_SPEAK
    MAX_OBJECTS_TO_SPEAK = int(request.json.get('max_objects', 8))
    return jsonify({"status": "success", "max_objects": MAX_OBJECTS_TO_SPEAK})

@app.route('/set_custom_vocab', methods=['POST'])
def set_custom_vocab():
    global VOCABULARY
    new_words = request.json.get('words', [])
    if new_words:
        VOCABULARY = list(dict.fromkeys(VOCABULARY + new_words))
        model.set_classes(VOCABULARY)
    return jsonify({"status": "success", "total_classes": len(VOCABULARY)})

@app.route('/get_languages', methods=['GET'])
def get_languages():
    """Returns all supported languages for the frontend dropdown."""
    indian = [
        "Hindi", "Gujarati", "Bengali", "Tamil", "Telugu", "Kannada",
        "Malayalam", "Marathi", "Punjabi", "Odia", "Assamese", "Urdu",
        "Sindhi", "Konkani", "Maithili", "Dogri", "Bodo", "Santali",
        "Kashmiri", "Nepali", "Manipuri", "Sanskrit"
    ]
    international = [
        "English", "Spanish", "French", "German", "Japanese", "Chinese",
        "Korean", "Arabic", "Portuguese", "Russian", "Italian", "Dutch",
        "Turkish", "Thai", "Vietnamese", "Indonesian", "Swahili", "Polish",
        "Ukrainian", "Romanian", "Greek", "Czech", "Swedish", "Finnish",
        "Hungarian", "Norwegian", "Danish", "Hebrew", "Filipino", "Malay",
        "Burmese", "Sinhala", "Afrikaans", "Amharic", "Catalan", "Croatian",
        "Serbian", "Slovak", "Slovenian", "Estonian", "Latvian", "Lithuanian",
        "Georgian", "Armenian", "Azerbaijani", "Kazakh", "Uzbek", "Mongolian",
        "Khmer", "Lao"
    ]
    return jsonify({
        "current": language,
        "indian": indian,
        "international": international,
        "all": indian + international
    })

@app.route('/get_logs', methods=['GET'])
def get_logs():
    uptime = int(time.time() - stats["uptime_start"])
    h, r = divmod(uptime, 3600)
    m, s = divmod(r, 60)
    freq = dict(sorted(
        stats["object_frequency"].items(),
        key=lambda x: x[1], reverse=True
    )[:20])
    return jsonify({
        "logs": detection_log[-30:],
        "stats": {
            "total_detections": stats["total_detections"],
            "unique_objects": len(stats["unique_objects"]),
            "unique_list": sorted(list(stats["unique_objects"])),
            "fps": stats["fps"],
            "model_name": stats["model_name"],
            "frames_processed": stats["frames_processed"],
            "avg_confidence": stats["avg_confidence"],
            "last_detection_time": stats["last_detection_time"],
            "uptime": f"{h:02d}:{m:02d}:{s:02d}",
            "object_frequency": freq,
            "confidence_history": stats["confidence_history"][-30:],
            "detection_timeline": stats["detection_timeline"][-30:],
            "speech_enabled": speech_enabled,
            "speech_cooldown": SPEECH_COOLDOWN,
            "max_speak_objects": MAX_OBJECTS_TO_SPEAK,
            "vocabulary_size": len(VOCABULARY),
            "language": language,
            "face_recognition_enabled": FACE_REC_ENABLED,
        }
    })

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global detection_log, stats
    detection_log = []
    stats["total_detections"] = 0
    stats["unique_objects"] = set()
    stats["object_frequency"] = defaultdict(int)
    stats["confidence_history"] = []
    stats["detection_timeline"] = []
    return jsonify({"status": "success"})

@app.route('/snapshot', methods=['GET'])
def snapshot():
    with frame_lock:
        if current_frame is not None:
            _, j = cv2.imencode('.jpg', current_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return Response(
                j.tobytes(), mimetype='image/jpeg',
                headers={
                    "Content-Disposition":
                        f"attachment; filename=trinexis_{datetime.now().strftime('%H%M%S')}.jpg"
                }
            )
    return jsonify({"error": "No frame"}), 404

@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    if heatmap_accumulator is not None:
        norm = cv2.normalize(heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(norm.astype(np.uint8), cv2.COLORMAP_JET)
        _, j = cv2.imencode('.jpg', colored)
        return Response(j.tobytes(), mimetype='image/jpeg')
    return jsonify({"error": "No data"}), 404

@app.route('/export_logs', methods=['GET'])
def export_logs():
    buf = io.BytesIO(json.dumps(detection_log, indent=2).encode())
    buf.seek(0)
    return send_file(
        buf, mimetype='application/json', as_attachment=True,
        download_name=f"trinexis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

@app.route('/get_classes', methods=['GET'])
def get_classes():
    return jsonify({"classes": VOCABULARY, "total": len(VOCABULARY)})

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"  TRINEXIS — Intelligent Vision System")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Classes: {len(VOCABULARY)}")
    print(f"  Languages: {len(language_code_map)} supported")
    print(f"  Face Recognition: {'ENABLED' if FACE_REC_ENABLED else 'DISABLED'}")
    print(f"  Speech: {'ENABLED' if speech_enabled else 'DISABLED'}")
    print(f"  URL: http://localhost:5000")
    print(f"{'='*60}\n")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)