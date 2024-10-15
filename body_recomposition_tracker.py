import os
import csv
import math

def get_user_input():
    """
    Prompts the user for all necessary inputs and returns them.
    """
    try:
        n_days = int(input("Enter the number of days for your journey: "))
        if n_days < 2:
            raise ValueError("Number of days must be at least 2 to perform interpolation.")
        
        w_init = float(input("Enter your initial weight (kgs): "))
        w_final = float(input("Enter your desired final weight (kgs): "))
        
        bf_init = float(input("Enter your initial body fat percentage (%): "))
        bf_final = float(input("Enter your desired final body fat percentage (%): "))
        
        m_init = float(input("Enter your initial muscle mass (kgs): "))
        m_final = float(input("Enter your desired final muscle mass (kgs): "))
        
        # Additional Inputs
        print("\n--- Additional Information for Progression Modeling ---")
        print("Select your training experience level:")
        print("1. New to Training")
        print("2. Beginner")
        print("3. Intermediate")
        print("4. Veteran")
        experience_level = int(input("Enter the number corresponding to your experience level (1-4): "))
        if experience_level not in [1, 2, 3, 4]:
            raise ValueError("Experience level must be between 1 and 4.")
        
        gender = input("Enter your gender (M/F): ").strip().upper()
        if gender not in ['M', 'F']:
            raise ValueError("Gender must be 'M' or 'F'.")
        
        age = int(input("Enter your age: "))
        if age <= 0:
            raise ValueError("Age must be a positive integer.")
        
        return (n_days, w_init, w_final, bf_init, bf_final, m_init, m_final,
                experience_level, gender, age)
    except ValueError as e:
        print(f"Input error: {e}")
        exit(1)

def calculate_progression_factors(experience_level, gender, age):
    """
    Calculates progression factors based on experience level, gender, and age.
    
    Returns a tuple of (weight_factor, body_fat_factor, muscle_factor).
    """
    # Base factors
    if experience_level == 1:  # New to Training
        base_weight = 1.2
        base_bf = 1.3
        base_muscle = 1.5
    elif experience_level == 2:  # Beginner
        base_weight = 1.0
        base_bf = 1.1
        base_muscle = 1.3
    elif experience_level == 3:  # Intermediate
        base_weight = 0.8
        base_bf = 0.9
        base_muscle = 1.1
    elif experience_level == 4:  # Veteran
        base_weight = 0.5
        base_bf = 0.6
        base_muscle = 0.8
    
    # Gender adjustments
    if gender == 'M':
        gender_multiplier = 1.0
    else:  # Female
        gender_multiplier = 0.9
    
    # Age adjustments
    if age < 25:
        age_multiplier = 1.1
    elif 25 <= age < 35:
        age_multiplier = 1.0
    elif 35 <= age < 45:
        age_multiplier = 0.9
    elif 45 <= age < 55:
        age_multiplier = 0.8
    else:
        age_multiplier = 0.7
    
    # Final factors
    weight_factor = base_weight * gender_multiplier * age_multiplier
    body_fat_factor = base_bf * gender_multiplier * age_multiplier
    muscle_factor = base_muscle * gender_multiplier * age_multiplier
    
    return weight_factor, body_fat_factor, muscle_factor

def calculate_daily_targets(n_days, initial, final, factor):
    """
    Calculates daily targets using a sigmoid function to model non-linear progression.
    
    Parameters:
        n_days (int): Total number of days.
        initial (float): Initial value.
        final (float): Final desired value.
        factor (float): Progression factor to adjust the curve.
        
    Returns:
        list of floats: Daily target values.
    """
    targets = []
    midpoint = n_days / 2
    steepness = factor  # Higher steepness means faster initial progress
    
    for day in range(1, n_days + 1):
        # Sigmoid function scaled between 0 and 1
        sigmoid = 1 / (1 + math.exp(-steepness * (day - midpoint) / midpoint))
        target = initial + (final - initial) * sigmoid
        targets.append(target)
    
    return targets

def generate_csv(days, weights, body_fats, muscles, output_path):
    """
    Generates a CSV file with the provided data.
    
    Parameters:
        days (list): List of day numbers.
        weights (list): List of weights per day.
        body_fats (list): List of body fat percentages per day.
        muscles (list): List of muscle mass per day.
        output_path (str): Path to save the CSV file.
    """
    headers = ['Day', 'Weight (kgs)', 'Body Fat (%)', 'Muscle (kgs)']
    rows = zip(days, weights, body_fats, muscles)
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([row[0], f"{row[1]:.2f}", f"{row[2]:.2f}", f"{row[3]:.2f}"])
    print(f"CSV file successfully saved to {output_path}")

def main():
    # Step 1: Get user input
    (n_days, w_init, w_final, bf_init, bf_final, m_init, m_final,
     experience_level, gender, age) = get_user_input()
    
    # Step 2: Calculate progression factors
    weight_factor, bf_factor, muscle_factor = calculate_progression_factors(
        experience_level, gender, age)
    
    # Step 3: Calculate daily targets
    days = list(range(1, n_days + 1))
    weights = calculate_daily_targets(n_days, w_init, w_final, weight_factor)
    body_fats = calculate_daily_targets(n_days, bf_init, bf_final, bf_factor)
    muscles = calculate_daily_targets(n_days, m_init, m_final, muscle_factor)
    
    # Step 4: Ensure final values are exact
    weights[-1] = w_final
    body_fats[-1] = bf_final
    muscles[-1] = m_final
    
    # Step 5: Prepare output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'out')
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 6: Define output file path
    output_file = os.path.join(output_dir, 'body_recomposition_targets.csv')
    
    # Step 7: Generate CSV
    generate_csv(days, weights, body_fats, muscles, output_file)

if __name__ == "__main__":
    main()

