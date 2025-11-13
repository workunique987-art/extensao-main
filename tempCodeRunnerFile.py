
        print(f"Q{q_data['question']}: {len(q_data['bubbles'])} bubbles")
        for bubble in q_data['bubbles']:
            print(f"  {bubble['choice']}: center{bubble['center']}")
    
    return template_path, position_data

if __name__ == "__main__":
    
    template_path, position_data = demonstrate_improved_layout()

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Gabarito gerado como \"{template_path}\"")