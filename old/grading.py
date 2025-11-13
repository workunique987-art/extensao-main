def grade_with_precise_positions(binary_img, bubble_positions, expected_answers, threshold, debug=False):
    """
    Grade using precisely known bubble positions
    """
    question_results = []
    score = 0
    
    debug_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR) if debug else None
    
    for q_data in bubble_positions:
        q_num = q_data['question']
        bubbles = q_data['bubbles']
        
        bubble_status = {}
        marked_choices = []
        
        for bubble in bubbles:
            choice = bubble['choice']
            x1, y1, x2, y2 = bubble['bbox']
            
            # Extract bubble region
            bubble_roi = binary_img[max(0,y1):min(binary_img.shape[0],y2), 
                                  max(0,x1):min(binary_img.shape[1],x2)]
            
            if bubble_roi.size == 0:
                filled_ratio = 0
            else:
                # Calculate filled percentage
                total_pixels = bubble_roi.size
                filled_pixels = np.sum(bubble_roi > 0)
                filled_ratio = filled_pixels / total_pixels
            
            bubble_status[choice] = filled_ratio
            
            if filled_ratio > threshold:
                marked_choices.append(choice)
        
        # Determine answer
        if len(marked_choices) == 1:
            student_answer = marked_choices[0]
            is_correct = (student_answer == expected_answers[q_num-1])
            if is_correct:
                score += 1
        else:
            student_answer = "MULTI" if len(marked_choices) > 1 else "NONE"
            is_correct = False
        
        question_results.append({
            'question': q_num,
            'student_answer': student_answer,
            'correct_answer': expected_answers[q_num-1],
            'is_correct': is_correct,
            'bubble_status': bubble_status
        })
        
        # Debug visualization - after processing all bubbles for this question
        if debug:
            correct_answer = expected_answers[q_num-1]
            
            for bubble in bubbles:
                choice = bubble['choice']
                center_x, center_y = bubble['center']
                filled_ratio = bubble_status[choice]
                
                # Determine colors based on answer status
                if choice == correct_answer and choice == student_answer:
                    # Correctly marked answer - Green
                    color = (0, 255, 0)
                    status_text = "CORRECT"
                elif choice == correct_answer and student_answer != "MULTI" and student_answer != "NONE":
                    # Correct answer but student marked wrong one - Blue (should have marked this)
                    color = (255, 0, 0)  # Blue
                    status_text = "SHOULD BE"
                elif choice == student_answer and not is_correct and student_answer != "MULTI" and student_answer != "NONE":
                    # Wrong answer marked by student - Red
                    color = (0, 0, 255)  # Red
                    status_text = "WRONG"
                elif filled_ratio > threshold:
                    # Multiple choice marked - Orange
                    color = (0, 165, 255)  # Orange
                    status_text = "MULTI"
                else:
                    # Unmarked bubble - Gray
                    color = (128, 128, 128)  # Gray
                    status_text = "empty"
                
                # Draw circle around bubble
                cv2.circle(debug_img, (center_x, center_y), 20, color, 3)
                
                # Add text showing fill ratio and status
                cv2.putText(debug_img, f"{filled_ratio:.2f}", 
                           (center_x-25, center_y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                cv2.putText(debug_img, status_text, 
                           (center_x-25, center_y+35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Add question summary
            question_pos = q_data.get('question_pos', (bubbles[0]['center'][0] - 100, bubbles[0]['center'][1]))
            summary_color = (0, 255, 0) if is_correct else (0, 0, 255)
            summary_text = f"Q{q_num}: Student={student_answer}, Correct={correct_answer} ({'✓' if is_correct else '✗'})"
            cv2.putText(debug_img, summary_text, 
                       (int(question_pos[0]), int(question_pos[1]) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, summary_color, 2)
    
    if debug:
        print("Grading visualization:")
        print("- GREEN: Correctly marked answer")
        print("- BLUE: Correct answer (should have been marked)")
        print("- RED: Wrong answer marked by student") 
        print("- ORANGE: Multiple answers marked")
        print("- GRAY: Unmarked bubble")
        cv2_imshow(debug_img)
        
        # Add legend to the debug image
        legend_img = np.zeros((200, 400, 3), dtype=np.uint8)
        legend_img.fill(255)  # White background
        
        legend_items = [
            ((50, 30), (0, 255, 0), "GREEN: Correct answer marked"),
            ((50, 60), (255, 0, 0), "BLUE: Correct answer (unmarked)"),
            ((50, 90), (0, 0, 255), "RED: Wrong answer marked"),
            ((50, 120), (0, 165, 255), "ORANGE: Multiple answers"),
            ((50, 150), (128, 128, 128), "GRAY: Unmarked bubble")
        ]
        
        for (pos, color, text) in legend_items:
            cv2.circle(legend_img, (pos[0]-20, pos[1]), 8, color, -1)
            cv2.putText(legend_img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        print("\nLegend:")
        cv2_imshow(legend_img)
    
    return {
        'total_score': score,
        'max_score': len(bubble_positions),
        'percentage': (score / len(bubble_positions)) * 100,
        'question_results': question_results,
        'multiple_answers': len([r for r in question_results if r['student_answer'] == 'MULTI']),
        'unanswered': len([r for r in question_results if r['student_answer'] == 'NONE'])
    }

def estimate_bubble_positions(binary_img, num_questions, choices):
    """
    Estimate bubble positions using detected elements (fallback method)
    """
    h, w = binary_img.shape
    
    # Detect circles using HoughCircles for more precise bubble detection
    circles = cv2.HoughCircles(
        binary_img, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=30, 
        param1=50, 
        param2=15, 
        minRadius=8, 
        maxRadius=15
    )
    
    bubble_positions = []
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        # Group circles by y-coordinate (rows)
        circles_by_row = {}
        for (x, y, r) in circles:
            row_key = (y // 30) * 30  # Group by approximate row
            if row_key not in circles_by_row:
                circles_by_row[row_key] = []
            circles_by_row[row_key].append((x, y, r))
        
        # Sort rows and process
        sorted_rows = sorted(circles_by_row.keys())
        question_num = 1
        
        for row_key in sorted_rows:
            if question_num > num_questions:
                break
                
            row_circles = sorted(circles_by_row[row_key], key=lambda c: c[0])  # Sort by x
            
            # Should have exactly len(choices) circles per question
            if len(row_circles) >= len(choices):
                question_bubbles = []
                for i, (x, y, r) in enumerate(row_circles[:len(choices)]):
                    question_bubbles.append({
                        'choice': choices[i],
                        'center': (x, y),
                        'bbox': (x-r, y-r, x+r, y+r)
                    })
                
                bubble_positions.append({
                    'question': question_num,
                    'bubbles': question_bubbles
                })
                question_num += 1
    
    return bubble_positions

def grade_gabarito_improved(
    image_path,
    expected_answers,
    position_data=None,
    choices=("A", "B", "C", "D", "E"),
    threshold=0.4,
    debug=False
):
    """
    Grade improved answer sheets with header labels
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Preprocess
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Enhanced preprocessing
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10
    )
    
    # Remove small noise
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    if debug:
        print("Preprocessed binary image:")
        cv2_imshow(binary)
    
    if position_data is None:
        print("Warning: No position data provided. Using estimation...")
        bubble_positions = estimate_bubble_positions(binary, len(expected_answers), choices)
    else:
        bubble_positions = position_data['bubble_positions']
    
    return grade_with_precise_positions(binary, bubble_positions, expected_answers, threshold, debug)

def print_grade_report(grade_results):
    """Print a formatted grade report"""
    results = grade_results
    print(f"\n=== GRADE REPORT ===")
    print(f"Score: {results['total_score']}/{results['max_score']}")
    print(f"Percentage: {results['percentage']:.1f}%")
    print(f"Multiple answers: {results['multiple_answers']}")
    print(f"Unanswered: {results['unanswered']}")
    
    # Calculate accuracy for answered questions
    answered_questions = len(results['question_results']) - results['unanswered'] - results['multiple_answers']
    if answered_questions > 0:
        accuracy = (results['total_score'] / answered_questions) * 100
        print(f"Accuracy (answered questions): {accuracy:.1f}%")
    
    print(f"\n=== DETAILED RESULTS ===")
    for item in results['question_results']:
        status = "○" if item['is_correct'] else "X"
        if item['student_answer'] in ['MULTI', 'NONE']:
            status = "!"  # Special status for multiple or no answers
        
        print(f"Q{item['question']:02d}: {status} Student={item['student_answer']:5} Correct={item['correct_answer']} ", end="")
        
        # Show bubble status for incorrect answers
        if not item['is_correct'] and item['student_answer'] not in ['MULTI', 'NONE']:
            marked_ratio = item['bubble_status'][item['student_answer']]
            correct_ratio = item['bubble_status'][item['correct_answer']]
            print(f"(marked: {marked_ratio:.2f}, correct: {correct_ratio:.2f})", end="")
        print()
    
    print(f"\n=== INCORRECT ANSWERS ===")
    incorrect = [r for r in results['question_results'] if not r['is_correct']]
    if incorrect:
        for item in incorrect:
            if item['student_answer'] == 'MULTI':
                marked = [ch for ch, ratio in item['bubble_status'].items() if ratio > 0.4]
                print(f"Q{item['question']:02d}: MULTIPLE answers {marked}, Correct={item['correct_answer']}")
            elif item['student_answer'] == 'NONE':
                print(f"Q{item['question']:02d}: UNANSWERED, Correct={item['correct_answer']}")
            else:
                print(f"Q{item['question']:02d}: Student={item['student_answer']}, Correct={item['correct_answer']}")
    else:
        print("No incorrect answers!")