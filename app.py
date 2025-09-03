# app.py — замените содержимое этим кодом
from flask import Flask, request, jsonify
import os, time, re
from PIL import Image
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def seo_filename(keyword, orig_filename):
    ext = orig_filename.rsplit(".", 1)[1].lower() if "." in orig_filename else "jpg"
    safe = re.sub(r"[^a-z0-9\-]+", "-", (keyword or "image").strip().lower())
    safe = re.sub(r"-+", "-", safe).strip("-")
    ts = int(time.time())
    return f"{safe}-{ts}.{ext}"


def optimise_image(in_path, out_path):
    try:
        img = Image.open(in_path).convert("RGB")
        img.save(out_path, optimize=True, quality=80)
    except Exception:
        # если PIL не смог — просто перемещаем файл
        os.replace(in_path, out_path)


def detect_keyword():
    # первые варианты, которые часто используют
    priority = ("keyword", "text_1", "text", "q", "query", "title", "name")
    for name in priority:
        v = request.form.get(name)
        if v and v.strip():
            return v.strip()
    # fallback: любое непустое поле формы
    for k, v in request.form.items():
        if v and v.strip():
            return v.strip()
    # fallback 2: берём имя первого файла без расширения
    for fkey in request.files:
        f = request.files.get(fkey)
        if f and f.filename:
            return os.path.splitext(f.filename)[0]
    return None


@app.route("/", methods=["GET"])
def home():
    return "Tilda Image Server — OK"


@app.route("/debug", methods=["POST", "GET"])
def debug():
    # Возвращаем, что именно пришло — для отладки Tilda ↔ Replit
    logger.info("=== ВХОДЯЩИЙ ЗАПРОС ОТ TILDA ===")
    logger.info(f"Метод: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        form_preview = {k: (v[:200] + "..." if len(v) > 200 else v) for k, v in request.form.items()}
        logger.info(f"Form данные: {form_preview}")
    except Exception:
        form_preview = {}
    
    json_data = request.get_json(silent=True)
    if json_data:
        logger.info(f"JSON данные: {json_data}")
    
    file_info = {}
    for key in request.files:
        files = request.files.getlist(key)
        file_info[key] = [f.filename for f in files if f.filename]
    
    if file_info:
        logger.info(f"Файлы: {file_info}")
    
    logger.info("=== КОНЕЦ ЗАПРОСА ===")
    
    return jsonify({
        "method": request.method,
        "form_keys": list(request.form.keys()),
        "form_preview": form_preview,
        "file_keys": list(request.files.keys()),
        "json_body": json_data,
        "success": True,
        "message": "Данные получены! Смотрите Console в Replit для подробностей."
    })


# Поддерживаем несколько эндпоинтов, чтобы не было путаницы
@app.route("/submit", methods=["POST"])
@app.route("/upload", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def submit():
    # Логируем входящий запрос
    logger.info(f"=== НОВЫЙ ЗАПРОС НА {request.endpoint} ===")
    logger.info(f"Form поля: {list(request.form.keys())}")
    logger.info(f"Файловые поля: {list(request.files.keys())}")
    
    # детектируем ключевое слово
    keyword = detect_keyword()
    logger.info(f"Найден keyword: '{keyword}'")
    if not keyword:
        return jsonify({
            "error": "Keyword is required or not found in form.",
            "success": False,
            "received_form_keys": list(request.form.keys()),
            "received_file_keys": list(request.files.keys()),
            "hint": "Make sure Tilda field name for the text is 'keyword' or 'text_1', or use /debug to see what Tilda sends."
        }), 400

    # собираем все файлы из всех файловых полей
    files = []
    for fk in request.files:
        files += request.files.getlist(fk)

    if not files:
        return jsonify({"error": "No files uploaded", "success": False}), 400

    results = []
    for f in files:
        orig = f.filename or "file"
        if orig == "":
            continue
        if not allowed(orig):
            return jsonify({"error": f"Bad file type: {orig}", "success": False}), 400

        tmp_name = f"tmp_{int(time.time()*1000)}_{orig}"
        tmp_path = os.path.join(UPLOAD_FOLDER, tmp_name)
        f.save(tmp_path)

        newname = seo_filename(keyword, orig)
        out_path = os.path.join(UPLOAD_FOLDER, newname)

        try:
            optimise_image(tmp_path, out_path)
        except Exception as e:
            # в крайнем случае — переместим файл без обработки
            try:
                os.replace(tmp_path, out_path)
            except Exception:
                pass
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        # простая генерация метаданных (можно расширить)
        base = (keyword or "Image").strip().capitalize()
        title = f"{base} | Optimised Photo"
        description = f"Optimised image about {keyword} for web and social."
        alt = f"{base} - SEO optimised image"
        hashtags = " ".join([f"#{t}" for t in re.sub(r'[^a-z0-9 ]', '', keyword.lower()).split()][:5])

        results.append({
            "original": orig,
            "saved": newname,
            "title": title,
            "description": description,
            "alt": alt,
            "hashtags": hashtags
        })

    return jsonify({"success": True, "keyword": keyword, "results": results}), 200