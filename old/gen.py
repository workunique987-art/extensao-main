import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math
from google.colab.patches import cv2_imshow
import json

def generate_gabarito_png_improved(
    filename="gabarito_improved.png",
    num_questions=50,
    choices=("A", "B", "C", "D", "E"),
    margin=50,
    spacing_y=20,
    bubble_diameter=20,
    title="GABARITO FIXO",
    subtitle="Nome: _________________________   Numero: ____   Turma: ______",
    font_path=None,
    add_reference_marks=True
):
    try:
        if font_path is None:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        title_font = ImageFont.truetype(font_path, 100)
        subtitle_font = ImageFont.truetype(font_path, 48)
        q_font = ImageFont.truetype(font_path, 56)
        choice_font = ImageFont.truetype(font_path, 56)
        header_font = ImageFont.truetype(font_path, 40)  # Smaller font for choice headers
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        q_font = ImageFont.load_default()
        choice_font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    if num_questions > 10:
        columns = num_questions // 10
    else:
        columns = 1

    rows_per_col = math.ceil(num_questions / columns)
    estimated_row_height = spacing_y + bubble_diameter
    
    header_height = 40
    required_height = int(margin * 2 + header_height + 10 + rows_per_col * estimated_row_height + 50)

    calculated_width = 300 * columns
    page_size = (1240, 877)

    img = Image.new("RGB", page_size, "white")
    draw = ImageDraw.Draw(img)

    w, h = page_size
    
    draw.text((margin, margin//2), title, font=title_font, fill="black")
    top = margin + 15 + header_height  # Reserve space for headers
    bottom = h - margin
    usable_height = bottom - top
    col_width = (w - 2*margin) / columns
    row_height = min(spacing_y + bubble_diameter, usable_height / rows_per_col)

    bubble_positions = []
    
    q = 1
    for col in range(columns):
        x0 = margin + col * col_width
        x_question_num = x0 + 20 
        temp_bbox = draw.textbbox((0,0), f"{q:02d}.", font=q_font)
        q_text_width = temp_bbox[2] - temp_bbox[0]
        x_choices_start = x_question_num + q_text_width + 30  
        
        header_y = margin + 15
        for i, ch in enumerate(choices):
            cx = int(x_choices_start + i * (bubble_diameter + 20))
            bbox = draw.textbbox((0, 0), ch, font=header_font)
            w_ch = bbox[2] - bbox[0]
            h_ch = bbox[3] - bbox[1]
            tx = cx + (bubble_diameter - w_ch) / 2
            ty = header_y
            draw.text((tx, ty), ch, font=header_font, fill="black")
            
            line_y_start = ty + h_ch + 2
            line_y_end = top - 5
            if line_y_end > line_y_start:  
                draw.line([(cx + bubble_diameter//2, line_y_start), 
                          (cx + bubble_diameter//2, line_y_end)], 
                         fill="black", width=1)

        for row in range(rows_per_col):
            if q > num_questions:
                break
            y = int(top + row * row_height)
            draw.text((x_question_num, y), f"{q:02d}.", font=q_font, fill="black")
            
            question_bubbles = []
            for i, ch in enumerate(choices):
                cx = int(x_choices_start + i * (bubble_diameter + 20))
                cy = int(y + (bubble_diameter/4) - bubble_diameter/2)
                
                # Draw bubble WITHOUT letter inside (clean for marking)
                draw.ellipse([cx, cy, cx + bubble_diameter, cy + bubble_diameter], 
                           outline="black", width=2)
                
                # Store position for reference
                question_bubbles.append({
                    'choice': ch,
                    'center': (cx + bubble_diameter//2, cy + bubble_diameter//2),
                    'bbox': (cx, cy, cx + bubble_diameter, cy + bubble_diameter),
                    'header_pos': (cx + bubble_diameter//2, header_y)  # Store header position too
                })
            
            bubble_positions.append({
                'question': q,
                'bubbles': question_bubbles,
                'question_pos': (x_question_num, y)
            })
            q += 1

    # Add reference marks for precise detection
    if add_reference_marks:
        # Corner marks (special patterns)
        mark_size = 15
        # Top-left: Cross pattern
        draw.line([(margin, margin), (margin+mark_size, margin)], fill="black", width=3)
        draw.line([(margin, margin), (margin, margin+mark_size)], fill="black", width=3)
        
        # Top-right: L pattern  
        draw.line([(w-margin, margin), (w-margin-mark_size, margin)], fill="black", width=3)
        draw.line([(w-margin, margin), (w-margin, margin+mark_size)], fill="black", width=3)
        
        # Bottom-left: Square pattern
        draw.rectangle([(margin, h-margin-mark_size), (margin+mark_size, h-margin)], 
                      outline="black", width=3)
        
        # Bottom-right: Circle pattern
        draw.ellipse([(w-margin-mark_size, h-margin-mark_size), (w-margin, h-margin)], 
                    outline="black", width=3)
        
        # Add alignment marks along the sides with more margin
        for i in range(3):
            y_mark = margin + header_height + (h - 2*margin - header_height) * (i+1) // 4
            # Left side - moved further left
            draw.line([(margin-15, y_mark), (margin-5, y_mark)], fill="black", width=2)
            # Right side - moved further right
            draw.line([(w-margin+5, y_mark), (w-margin+15, y_mark)], fill="black", width=2)

    footer_text = "Assinale apenas uma opcao por questao. Use caneta preta ou azul."
    bbox = draw.textbbox((0, 0), footer_text, font=subtitle_font)
    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]

    draw.text((w - margin - fw, h - margin - 15), subtitle, font=subtitle_font, fill="black")
    draw.text((w - margin - fw, h - margin), footer_text, font=subtitle_font, fill="black")

    img.save(filename, dpi=(300,300))
    
    # Also save the bubble positions for precise grading
    position_data = {
        'bubble_positions': bubble_positions,
        'page_size': page_size,
        'margin': margin,
        'bubble_diameter': bubble_diameter,
        'choices': choices
    }
    
    # Save positions as JSON for the grading function
    with open(filename.replace('.png', '_positions.json'), 'w') as f:
        json.dump(position_data, f, default=str)  # str for serialization
    
    return filename, position_data