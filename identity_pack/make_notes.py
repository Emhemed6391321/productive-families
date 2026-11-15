#!/usr/bin/env python3
"""Field-notes card made from the handwritten list (only the clearly legible items), Tripoli-B identity. 1080 x 2040."""
import math
from PIL import Image, ImageDraw
from pack_lib import *
from make_welcome_set import medallion, crown
from make_tips import wrap, badge

W, H = 1080, 2040
NAME, PHONE = "تنسيقية حجاج طرابلس ب", "0934455422"
BRONZE_T = (120, 90, 40)
SECTIONS = [
 ("النقل والباصات", [
    "بناء علاقة وطيدة مع السائق ومعاونه",
    "أغلب السائقين لا يعرفون الطرق، لذا فالمرشد عنصر محوري",
    "تعليق لافتة كبيرة (٦٠×٨٠) أمام الباص وخلفه",
    "تكييف الباصات قد لا يعمل أحيانًا مع ارتفاع الحرارة، وقد يبقى الحجاج لساعات",
 ]),
 ("النفرة ومزدلفة", [
    "مرافقة الحجاج في مرحلة النفرة من عرفة إلى مزدلفة",
    "الذهاب سيرًا على الأقدام من مزدلفة",
    "المبيت في مزدلفة: إحضار الماء والشراشف",
 ]),
 ("الأمتعة والتجهيز", [
    "عدم حمل الأمتعة الكثيرة، والاكتفاء بأمتعة قليلة",
    "توفير الشعارات والستيكرات",
    "تصوير الجوازات وصور التأشيرات",
    "لافتة لطاولة الإدارة في فندق التنسيقية",
 ]),
 ("توعية وإرشاد", [
    "توعية المرافق بالاهتمام بالحاج نفسه",
    "الهدي على الدولة",
 ]),
]
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

def build():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); frame(img, 26, GOLD, 3, 12); cx = W // 2
    paste(img, sky_layer(W, .4), 0, 1890)
    medallion(img, 140, 140, 64, shadow=False); d = ImageDraw.Draw(img)
    d.text((W - 70, 112), "الهيئة العامة لشؤون الحج والعمرة", font=font(600, 28), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar")
    d.text((W - 70, 160), NAME, font=font(700, 46), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.line((220, 215, W - 70, 215), fill=GOLD, width=2)
    d.text((cx, 330), "ملاحظات ميدانية", font=font(700, 104), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((cx, 425), "لمشرفي الحجاج خلال الرحلة", font=font(700, 42), fill=GOLD, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, cx, 478, half=300, gap=30, col=GOLD, width=3, size=11); d = ImageDraw.Draw(img)
    fb = font(600, 33); lh = 50; y = 530; gap = 26; hh = 70
    for si, (title, items) in enumerate(SECTIONS, 1):
        rows = [wrap(fb, t, 780) for t in items]; body = sum(len(r) for r in rows) * lh + len(rows) * 16 + 30
        box = (60, y, W - 60, y + hh + body); soft_shadow(img, box, 30, alpha=50, blur=12, off=6); d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, 30, fill=CREAM, outline=(222, 204, 168), width=2)
        d.rounded_rectangle((box[0], box[1], box[2], box[1] + hh), 30, fill=GREEN); d.rectangle((box[0], box[1] + hh - 30, box[2], box[1] + hh), fill=GREEN); d.line((box[0], box[1] + hh, box[2], box[1] + hh), fill=GOLD, width=3)
        d.ellipse((box[2] - 70, box[1] + 11, box[2] - 14, box[1] + 59), fill=GOLD); d.text((box[2] - 42, box[1] + 36), str(si).translate(AR), font=font(700, 34), fill=GREEN_DK, anchor="mm", direction="rtl", language="ar")
        d.text((box[2] - 92, box[1] + 37), title, font=font(700, 38), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
        yy = box[1] + hh + 24
        for r in rows:
            d.polygon([(box[2] - 40, yy + 24), (box[2] - 30, yy + 14), (box[2] - 20, yy + 24), (box[2] - 30, yy + 34)], fill=GOLD)
            for k, l in enumerate(r): d.text((box[2] - 62, yy + 25 + k * lh), l, font=fb, fill=GREEN, anchor="rm", direction="rtl", language="ar")
            yy += len(r) * lh + 16
        y = box[3] + gap
    d.rectangle((0, H - 78, W, H), fill=GREEN_DK); d.rectangle((0, H - 78, W, H - 73), fill=GOLD)
    d.text((W - 60, H - 38), NAME, font=font(700, 32), fill=CREAM, anchor="rm", direction="rtl", language="ar"); d.text((60, H - 38), PHONE, font=font(700, 36), fill=GOLD_LT, anchor="lm")
    return img, y
if __name__ == "__main__":
    im, y = build(); print("content ends at", y); im.convert("RGB").save("Notes/Field-notes-card.png", optimize=True)
