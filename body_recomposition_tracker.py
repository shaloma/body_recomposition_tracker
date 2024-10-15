import os
import csv

def get_user_input():
    """
    Prompts the user for all necessary inputs and returns them.
    """
    try:
        n_days = int(input("Enter the number of days for your journey: "))
        if n_days < 1:
            raise ValueError("Number of days must be at least 1.")

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

    Returns a tuple of (weight_max_daily_change, body_fat_max_daily_change, muscle_max_daily_change).
    """
    # Base maximum daily changes based on experience level
    if experience_level == 1:  # New to Training
        base_weight = 0.07  # kg per day
        base_bf = 0.14      # % per day
        base_muscle = 0.07  # kg per day
    elif experience_level == 2:  # Beginner
        base_weight = 0.06
        base_bf = 0.13
        base_muscle = 0.06
    elif experience_level == 3:  # Intermediate
        base_weight = 0.05
        base_bf = 0.12
        base_muscle = 0.05
    elif experience_level == 4:  # Veteran
        base_weight = 0.04
        base_bf = 0.10
        base_muscle = 0.04

    # Gender adjustments
    if gender == 'M':
        gender_multiplier = 1.0
    else:  # Female
        gender_multiplier = 0.9

    # Age adjustments
    if age < 25:
        age_multiplier = 1.0
    elif 25 <= age < 35:
        age_multiplier = 0.95
    elif 35 <= age < 45:
        age_multiplier = 0.90
    elif 45 <= age < 55:
        age_multiplier = 0.85
    else:
        age_multiplier = 0.80

    # Final maximum daily changes
    weight_max_daily_change = base_weight * gender_multiplier * age_multiplier
    body_fat_max_daily_change = base_bf * gender_multiplier * age_multiplier
    muscle_max_daily_change = base_muscle * gender_multiplier * age_multiplier

    return weight_max_daily_change, body_fat_max_daily_change, muscle_max_daily_change

def calculate_required_daily_change(initial, final, n_days, is_loss=True):
    """
    Calculates the required daily change to reach the target by the final day.

    Parameters:
        initial (float): Initial value.
        final (float): Final desired value.
        n_days (int): Total number of days.
        is_loss (bool): True if the parameter is expected to decrease (e.g., body fat), False if increase (e.g., muscle mass).

    Returns:
        float: Required daily change.
    """
    total_change = final - initial
    daily_change = total_change / n_days
    if is_loss:
        daily_change = -abs(daily_change)  # Ensure it's negative
    else:
        daily_change = abs(daily_change)   # Ensure it's positive
    return daily_change

def validate_daily_changes(daily_weight_change, daily_bf_change, daily_muscle_change,
                           weight_max, bf_max, muscle_max):
    """
    Validates that the required daily changes do not exceed the maximum allowed changes.

    Parameters:
        daily_weight_change (float): Required daily weight change.
        daily_bf_change (float): Required daily body fat change.
        daily_muscle_change (float): Required daily muscle mass change.
        weight_max (float): Maximum allowed daily weight change.
        bf_max (float): Maximum allowed daily body fat change.
        muscle_max (float): Maximum allowed daily muscle mass change.

    Returns:
        bool: True if all changes are within limits, False otherwise.
    """
    if abs(daily_weight_change) > weight_max:
        print(f"Required daily weight change ({abs(daily_weight_change):.4f} kg/day) exceeds the maximum allowed ({weight_max:.4f} kg/day).")
        return False
    if abs(daily_bf_change) > bf_max:
        print(f"Required daily body fat change ({abs(daily_bf_change):.4f}%/day) exceeds the maximum allowed ({bf_max:.4f}%/day).")
        return False
    if abs(daily_muscle_change) > muscle_max:
        print(f"Required daily muscle mass change ({abs(daily_muscle_change):.4f} kg/day) exceeds the maximum allowed ({muscle_max:.4f} kg/day).")
        return False
    return True

def calculate_daily_targets(n_days, initial, final, daily_change):
    """
    Calculates daily targets using linear progression.

    Parameters:
        n_days (int): Total number of days.
        initial (float): Initial value.
        final (float): Final desired value.
        daily_change (float): Daily change.

    Returns:
        list of floats: Daily target values.
    """
    targets = []
    for day in range(n_days):
        target = initial + daily_change * day
        targets.append(target)
    # Ensure the last day matches exactly
    targets[-1] = final
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

    # Step 2: Calculate progression factors (maximum allowed daily changes)
    weight_max_daily_change, bf_max_daily_change, muscle_max_daily_change = calculate_progression_factors(
        experience_level, gender, age)

    # Step 3: Calculate required daily changes to reach targets
    daily_weight_change = calculate_required_daily_change(w_init, w_final, n_days, is_loss=(w_final < w_init))
    daily_bf_change = calculate_required_daily_change(bf_init, bf_final, n_days, is_loss=(bf_final < bf_init))
    daily_muscle_change = calculate_required_daily_change(m_init, m_final, n_days, is_loss=(m_final < m_init))

    # Step 4: Validate daily changes
    valid = validate_daily_changes(daily_weight_change, daily_bf_change, daily_muscle_change,
                                   weight_max_daily_change, bf_max_daily_change, muscle_max_daily_change)
    if not valid:
        print("Please adjust your goals or extend the duration to meet realistic daily changes.")
        exit(1)

    # Step 5: Calculate daily targets
    weights = calculate_daily_targets(n_days, w_init, w_final, daily_weight_change)
    body_fats = calculate_daily_targets(n_days, bf_init, bf_final, daily_bf_change)
    muscles = calculate_daily_targets(n_days, m_init, m_final, daily_muscle_change)

    # Step 6: Prepare output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'out')
    os.makedirs(output_dir, exist_ok=True)

    # Step 7: Define output file path
    output_file = os.path.join(output_dir, 'body_recomposition_targets.csv')

    # Step 8: Generate CSV
    days = list(range(1, n_days + 1))
    generate_csv(days, weights, body_fats, muscles, output_file)

if __name__ == "__main__":
    main()
