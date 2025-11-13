def demonstrate_improved_layout():
    """Generate and display the improved layout"""
    template_path, position_data = generate_gabarito_png_improved(
        "demonstration_gabarito.png", 
        num_questions=20,  # Smaller for demonstration
        add_reference_marks=True
    )
    
    print("Generated improved template with:")
    print("- Choice headers above bubbles")
    print("- Better spacing between question numbers and bubbles")
    print("- Reference marks for alignment")
    print(f"- Saved positions to: {template_path.replace('.png', '_positions.json')}")
    
    # Display the image
    img = Image.open(template_path)
    print(f"\nTemplate size: {img.size}")
    
    # Show bubble positions for verification
    print(f"\nFirst 3 questions bubble positions:")
    for i in range(min(3, len(position_data['bubble_positions']))):
        q_data = position_data['bubble_positions'][i]
        print(f"Q{q_data['question']}: {len(q_data['bubbles'])} bubbles")
        for bubble in q_data['bubbles']:
            print(f"  {bubble['choice']}: center{bubble['center']}")
    
    return template_path, position_data