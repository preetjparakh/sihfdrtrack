import re
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pypdfium2
import easyocr
from PIL import Image

_reader: Optional[easyocr.Reader] = None

def get_ocr_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader

def render_document_to_pil(file_path: Path) -> List[Tuple[Image.Image, int]]:
    """
    Renders image or PDF to a list of (PIL.Image, page_number).
    """
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        pdf = pypdfium2.PdfDocument(file_path)
        pages = []
        for i, page in enumerate(pdf):
            pil_img = page.render(scale=2).to_pil()
            pages.append((pil_img, i + 1))
        return pages
    else:
        img = Image.open(file_path).convert("RGB")
        return [(img, 1)]

def normalize_date(date_str: str) -> Tuple[Optional[str], bool]:
    s = date_str.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s, False

    m = re.match(r"^(\d{2})-(\d{2})-(\d{4})$", s)
    if m:
        d, mth, y = m.groups()
        return f"{y}-{mth}-{d}", False

    m_slash = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m_slash:
        p1, p2, y = int(m_slash.group(1)), int(m_slash.group(2)), m_slash.group(3)
        if p1 <= 12 and p2 <= 12:
            return s, True
        elif p1 > 12:
            return f"{y}-{p2:02d}-{p1:02d}", False
        else:
            return f"{y}-{p1:02d}-{p2:02d}", False

    return s, False

def normalize_amount(amount_str: str) -> str:
    cleaned = re.sub(r"[^\d.]", "", amount_str)
    try:
        val = float(cleaned)
        return f"{val:.2f}"
    except ValueError:
        return amount_str

def clean_bbox(bbox) -> Optional[List[List[int]]]:
    if not bbox:
        return None
    try:
        return [[int(pt[0]), int(pt[1])] for pt in bbox]
    except Exception:
        return None

def run_ocr_on_file(file_path: Path) -> Tuple[List[Dict[str, Any]], str, float]:
    reader = get_ocr_reader()
    pages = render_document_to_pil(file_path)

    all_blocks = []
    full_text_lines = []

    for img, page_num in pages:
        temp_img_path = file_path.parent / f"_temp_ocr_{uuid.uuid4().hex[:6]}.png"
        img.save(temp_img_path)
        try:
            results = reader.readtext(str(temp_img_path))
        finally:
            temp_img_path.unlink(missing_ok=True)

        for bbox, text, conf in results:
            all_blocks.append((bbox, text.strip(), float(conf), page_num))
            full_text_lines.append(text.strip())

    full_raw_text = "\n".join(full_text_lines)
    if not all_blocks:
        return [], "", 0.0

    avg_conf = sum(b[2] for b in all_blocks) / len(all_blocks)

    if len(all_blocks) < 3 or avg_conf < 0.25:
        return [], full_raw_text, avg_conf

    extracted_dict = {}

    # 1. Inline matching (Label: Value in same text block)
    for bbox, text, conf, page_num in all_blocks:
        if ":" in text:
            parts = text.split(":", 1)
            lbl = parts[0].strip().lower()
            val = parts[1].strip()
            if "fdr number" in lbl:
                extracted_dict["fdr_number"] = (val, conf, clean_bbox(bbox), page_num)
            elif "issuing bank" in lbl or "bank" in lbl:
                extracted_dict["bank_id"] = (val, conf, clean_bbox(bbox), page_num)
            elif "depositor" in lbl:
                extracted_dict["depositor_name"] = (val, conf, clean_bbox(bbox), page_num)
            elif "principal" in lbl:
                extracted_dict["principal_amount"] = (val, conf, clean_bbox(bbox), page_num)
            elif "currency" in lbl:
                extracted_dict["currency"] = (val, conf, clean_bbox(bbox), page_num)
            elif "issue date" in lbl:
                extracted_dict["issue_date"] = (val, conf, clean_bbox(bbox), page_num)
            elif "maturity date" in lbl:
                extracted_dict["maturity_date"] = (val, conf, clean_bbox(bbox), page_num)
            elif "beneficiary" in lbl:
                extracted_dict["beneficiary_name"] = (val, conf, clean_bbox(bbox), page_num)
            elif "lien status" in lbl:
                extracted_dict["lien_status"] = (val, conf, clean_bbox(bbox), page_num)
            elif "lien in favour" in lbl:
                extracted_dict["lien_in_favour_of"] = (val, conf, clean_bbox(bbox), page_num)

    # 2. Spatial two-column matching
    def y_center(b):
        return sum([pt[1] for pt in b]) / 4.0
    def x_left(b):
        return min([pt[0] for pt in b])

    labels_map = {
        "fdr number": "fdr_number",
        "issuing bank": "bank_id",
        "depositor": "depositor_name",
        "principal inr": "principal_amount",
        "principal": "principal_amount",
        "currency": "currency",
        "issue date": "issue_date",
        "maturity date": "maturity_date",
        "beneficiary": "beneficiary_name",
        "lien status": "lien_status",
        "lien in favour of": "lien_in_favour_of",
        "lien in favour": "lien_in_favour_of"
    }

    for i, (b_lbl, t_lbl, c_lbl, p_lbl) in enumerate(all_blocks):
        lbl_clean = t_lbl.strip().lower().replace(":", "")
        field_key = labels_map.get(lbl_clean)
        if field_key and field_key not in extracted_dict:
            yc = y_center(b_lbl)
            candidates = []
            for j, (b_val, t_val, c_val, p_val) in enumerate(all_blocks):
                if i != j and p_val == p_lbl:
                    val_yc = y_center(b_val)
                    if abs(val_yc - yc) < 45 and x_left(b_val) > x_left(b_lbl) + 40:
                        candidates.append((abs(val_yc - yc), t_val, c_val, clean_bbox(b_val), p_val))
            if candidates:
                candidates.sort(key=lambda c: c[0])
                extracted_dict[field_key] = (candidates[0][1], candidates[0][2], candidates[0][3], candidates[0][4])

    # 3. Regex Fallbacks on raw text
    if "fdr_number" not in extracted_dict:
        m = re.search(r"FDR-2026-[0-9A-Za-z]+", full_raw_text)
        if m: extracted_dict["fdr_number"] = (m.group(0), 0.75, None, 1)
    if "bank_id" not in extracted_dict:
        m = re.search(r"DEMO-BANK-\d+", full_raw_text)
        if m: extracted_dict["bank_id"] = (m.group(0), 0.75, None, 1)
    if "currency" not in extracted_dict:
        if "INR" in full_raw_text: extracted_dict["currency"] = ("INR", 0.95, None, 1)
    if "principal_amount" not in extracted_dict:
        m = re.search(r"\b\d{1,2}(?:,\d{2})*,\d{3}\.\d{2}\b|\b\d{6,8}\.\d{2}\b", full_raw_text)
        if m: extracted_dict["principal_amount"] = (m.group(0), 0.85, None, 1)

    field_records = []
    for field, (raw_val, conf, bbox, page_num) in extracted_dict.items():
        norm_val = raw_val
        status_flag = "EXTRACTED"

        if field == "fdr_number":
            m = re.match(r"(FDR-2026-)(.+)", raw_val)
            if m:
                prefix, num = m.groups()
                norm_num = num.replace("O", "0").replace("o", "0")
                norm_val = prefix + norm_num
        elif field == "principal_amount":
            norm_val = normalize_amount(raw_val)
        elif field in ("issue_date", "maturity_date"):
            norm_val, is_ambiguous = normalize_date(raw_val)
            if is_ambiguous:
                status_flag = "FLAGGED_AMBIGUOUS_DATE"

        field_records.append({
            "field": field,
            "raw_value": str(raw_val),
            "normalized_value": str(norm_val),
            "confidence": round(conf, 4) if conf is not None else None,
            "page": page_num,
            "bounding_box": bbox,
            "review_status": status_flag
        })

    return field_records, full_raw_text, avg_conf
