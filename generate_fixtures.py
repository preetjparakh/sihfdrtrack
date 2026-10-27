import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

base = Path(__file__).resolve().parent
seed = json.loads((base / "seed.json").read_text())
out = base / "fixtures"
out.mkdir(exist_ok=True)
fonts = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
def font(size):
    for name in fonts:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

labels = [
    ("fdr_number", "FDR Number"), ("bank_id", "Issuing Bank"),
    ("depositor_name", "Depositor"), ("principal_amount", "Principal INR"),
    ("currency", "Currency"), ("issue_date", "Issue Date"),
    ("maturity_date", "Maturity Date"), ("beneficiary_name", "Beneficiary"),
    ("lien_status", "Lien Status"), ("lien_in_favour_of", "Lien In Favour Of")
]
manifest = []
for doc in seed["documents"]:
    image = Image.new("RGB", (1600, 1600), "white")
    draw = ImageDraw.Draw(image)
    layout = int(doc["layout_id"][1:])
    x = 65 + layout * 8
    draw.rectangle((35, 35, 1560, 1550), outline="black", width=3)
    draw.text((x, 65), "SYNTHETIC - FOR PROTOTYPE ONLY", fill="black", font=font(32))
    draw.text((x, 130), "FIXED DEPOSIT RECEIPT", fill="black", font=font(42))
    draw.text((x, 195), "Fictional bank document - no financial value", fill="black", font=font(26))
    pairs = list(labels)
    if layout == 2:
        pairs = pairs[2:] + pairs[:2]
    elif layout == 3:
        pairs = list(reversed(pairs))
    y = 280
    for key, label in pairs:
        value = doc["ground_truth"].get(key)
        text = "NOT STATED" if value is None else str(value)
        if key == "principal_amount" and layout == 4:
            text = "10,00,000.00" if text == "1000000.00" else text
        if key in ("issue_date", "maturity_date") and layout == 5 and len(text) == 10 and text[4] == "-":
            year, month, day = text.split("-")
            text = f"{day}-{month}-{year}"
        if layout in (1, 3, 5):
            draw.text((x, y), label + ": " + text, fill="black", font=font(28))
        else:
            draw.text((x, y), label, fill="black", font=font(27))
            draw.text((x + 470, y), text, fill="black", font=font(27))
        y += 92
    draw.text((x, 1380), "No real stamp, signature or bank authorization", fill="black", font=font(25))
    if doc["variant"] == "rotated":
        image = image.rotate(2, fillcolor="white")
    elif doc["variant"] == "low_contrast":
        image = image.point(lambda n: int(170 + n / 3))
    elif doc["variant"] == "blurred":
        image = image.resize((240, 240)).resize((1600, 1600)).filter(ImageFilter.GaussianBlur(5))
    image.save(out / (doc["id"] + ".png"))
    image.save(out / (doc["id"] + ".pdf"), "PDF", resolution=150)
    manifest.append({"document_id": doc["id"], "png": "fixtures/" + doc["id"] + ".png", "pdf": "fixtures/" + doc["id"] + ".pdf", "submission_id": doc["submission_id"]})
(out / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Generated {len(manifest)} PNGs and {len(manifest)} image-based PDFs")
