import json
from PIL import Image, ImageDraw
import os

def create_marked_demo_sheet():
    """
    Create a marked answer sheet by asking for each question's answer
    """
    print("=== Answer Sheet Marker ===")
    print("This will create a marked answer sheet for grading demonstration.")
    print()
    
    try:
        num_questions = int(input("Enter number of questions (default 20): ") or "20")
    except ValueError:
        num_questions = 20
        print(f"Using default: {num_questions} questions")
    
    if not os.path.exists(template_name):
        print(f"\nError: Template file '{template_name}' not found!")
        print("Please run main.py first to generate the template.")
        return None
    
    if not os.path.exists(position_file):
        print(f"\nError: Position file '{position_file}' not found!")
        print("Please run main.py first to generate the template.")
        return None
    
    try:
        with open(position_file, 'r') as f:
            position_data = json.load(f)
    except Exception as e:
        print(f"Error loading position data: {e}")
        return None
    
    print(f"\nEnter answers for {num_questions} questions:")
    print("Options: A, B, C, D, E (or leave blank for unanswered)")
    print()
    
    user_answers = {}
    for q in range(1, num_questions + 1):
        while True:
            answer = input(f"Q{q:02d}: ").upper().strip()
            if answer == "":
                user_answers[q] = None
                break
            elif answer in ['A', 'B', 'C', 'D', 'E']:
                user_answers[q] = answer
                break
            else:
                print("Invalid answer! Please enter A, B, C, D, E or leave blank.")
    
    try:
        img = Image.open(template_name)
        draw = ImageDraw.Draw(img)
        
        marked_count = 0
        for q_data in position_data['bubble_positions']:
            q_num = q_data['question']
            if q_num <= num_questions and user_answers.get(q_num):
                answer = user_answers[q_num]
                for bubble in q_data['bubbles']:
                    if bubble['choice'] == answer:
                        cx, cy = bubble['center']
                        # Fill the bubble
                        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill="black")
                        marked_count += 1
                        break
        
        # Save marked sheet
        output_name = "my_marked_sheet.png"
        img.save(output_name)
        
        print(f"\nSuccessfully created marked sheet: {output_name}")
        print(f"Marked {marked_count} out of {num_questions} questions")
        
        print(f"\n=== YOUR ANSWERS ===")
        for q in range(1, num_questions + 1):
            answer = user_answers.get(q)
            status = answer if answer else "UNANSWERED"
            print(f"Q{q:02d}: {status}")
        
        return output_name, user_answers
        
    except Exception as e:
        print(f"Error creating marked sheet: {e}")
        return None

def quick_demo():
    """
    Quick demo with predefined answers
    """
    print("=== Quick Demo Mode ===")
    
    # Predefined answers for a quick test
    demo_answers = {
        1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
        6: "A", 7: "B", 8: "C", 9: "D", 10: "E",
        11: "A", 12: "B", 13: "C", 14: "D", 15: "E", 
        16: "A", 17: "B", 18: "C", 19: "D", 20: "E"
    }
    
    if not os.path.exists(template_name) or not os.path.exists(position_file):
        print("Please run main.py first to generate the template!")
        return None
    
    try:
        with open(position_file, 'r') as f:
            position_data = json.load(f)
        
        img = Image.open(template_name)
        draw = ImageDraw.Draw(img)
        
        for q_data in position_data['bubble_positions']:
            q_num = q_data['question']
            if q_num in demo_answers:
                answer = demo_answers[q_num]
                for bubble in q_data['bubbles']:
                    if bubble['choice'] == answer:
                        cx, cy = bubble['center']
                        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill="black")
                        break
        
        output_name = "./templates/marked_demo.png"
        img.save(output_name)
        print(f"Created quick demo: {output_name}")
        return output_name, demo_answers
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":

    template_name = "./templates/gabarito_demo.png"
    position_file = "./templates/gabarito_demo_positions.json"

    print("Choose mode:")
    print("1. Interactive - Enter your own answers")
    print("2. Quick Demo - Use predefined answers")
    
    choice = input("Enter choice (1 or 2, default 1): ").strip()
    
    if choice == "2":
        result = quick_demo()
    else:
        result = create_marked_demo_sheet()
    
    if result:
        marked_file, answers = result
        print(f"\nYou can now grade this sheet by running:")
        print(f"   python grade_it.py")
        print(f"\nOr manually grade it with:")
        print(f"   from grade_it import grade_gabarito_improved, print_grade_report")
        print(f"   results = grade_gabarito_improved('{marked_file}', expected_answers, position_data)")
        print(f"   print_grade_report(results)")
    else:
        print("\nFailed to create marked sheet.")