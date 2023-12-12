import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    # Create an empty dataframe with unique IDs as both index and columns
    unique_ids = sorted(set(df['id_start'].unique()) | set(df['id_end'].unique()))
    distance_matrix = pd.DataFrame(index=unique_ids, columns=unique_ids).fillna(0)

    # Populate the distance matrix with cumulative distances
    for _, row in df.iterrows():
        start, end, distance = row['id_start'], row['id_end'], row['distance']
        distance_matrix.at[start, end] += distance
        distance_matrix.at[end, start] += distance  # Accounting for bidirectional distances

    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    # Extract unique 'id_start' and 'id_end' values
    unique_ids = pd.concat([df['id_start'], df['id_end']]).unique()

    # Create a DataFrame to store unrolled data
    unrolled_df = pd.DataFrame(columns=['id_start', 'id_end', 'distance'])

    # Iterate through unique combinations of 'id_start' and 'id_end'
    for start_id in unique_ids:
        for end_id in unique_ids:
            if start_id != end_id:
                # Check if the combination already exists in the input DataFrame
                existing_entry = df[(df['id_start'] == start_id) & (df['id_end'] == end_id)]

                if not existing_entry.empty:
                    # If the combination exists, append the entry to the unrolled DataFrame
                    unrolled_df = unrolled_df.append(existing_entry, ignore_index=True)
                else:
                    # If the combination does not exist, add a row with distance set to 0
                    unrolled_df = unrolled_df.append({'id_start': start_id, 'id_end': end_id, 'distance': 0}, ignore_index=True)

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    # Filter dataframe for the specified reference_id
    reference_data = df[df['id_start'] == reference_id]

    # Calculate the average distance for the reference_id
    average_distance = reference_data['distance'].mean()

    # Calculate the lower and upper bounds for the 10% threshold
    lower_bound = average_distance - (0.1 * average_distance)
    upper_bound = average_distance + (0.1 * average_distance)

    # Filter dataframe based on the 10% threshold
    filtered_ids = df[(df['distance'] >= lower_bound) & (df['distance'] <= upper_bound)]['id_start']

    # Remove duplicates and sort the resulting list
    sorted_ids = sorted(set(filtered_ids))

    return pd.Series(sorted_ids)


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    # Define rate coefficients for each vehicle type
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Add columns to the DataFrame for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    from datetime import time
    # Define time ranges and discount factors
    time_ranges_weekday = [(time(0, 0, 0), time(10, 0, 0)),
                           (time(10, 0, 0), time(18, 0, 0)),
                           (time(18, 0, 0), time(23, 59, 59))]

    time_ranges_weekend = [(time(0, 0, 0), time(23, 59, 59))]

    discount_factors_weekday = [0.8, 1.2, 0.8]
    discount_factor_weekend = 0.7

    # Add placeholder columns for vehicle types
    df['moto'] = df['car'] = df['rv'] = df['bus'] = df['truck'] = 0

    # Add columns for time-based toll rates
    df['start_day'] = df['end_day'] = df['id_start'].apply(lambda x: 'Monday')
    df['start_time'] = time(0, 0, 0)
    df['end_time'] = time(23, 59, 59)

    # Apply discount factors based on time ranges
    for i, (start_time, end_time) in enumerate(time_ranges_weekday):
        mask = (df['start_time'] >= start_time) & (df['end_time'] <= end_time)
        df.loc[mask, ['start_time', 'end_time']] = start_time, end_time
        df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] = df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] * discount_factors_weekday[i]

    for start_time, end_time in time_ranges_weekend:
        mask = (df['start_time'] >= start_time) & (df['end_time'] <= end_time)
        df.loc[mask, ['start_time', 'end_time']] = start_time, end_time
        df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] = df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] * discount_factor_weekend

    return df
