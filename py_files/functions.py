import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yaml

def cleaning_productivity_data(df):
    """
    Cleans the Extended_Employee_Performance_and_Productivity_Data.csv DataFrame by 
    performing multiple data preparation steps, including
    dropping unnecessary columns, filtering rows, normalizing numeric values, and renaming
    columns. This function also categorizes work types for easier analysis.

    Parameters:
    df (pandas.DataFrame): The input dataset to clean. Expected to contain columns such as 
    'Employee_ID', 'Hire_Date', 'Team_Size', 'Department', 'Remote_Work_Frequency', 
    'Promotions', 'Training_Hours', 'Employee_Satisfaction_Score', and 'Performance_Score'.

    Returns:
    pandas.DataFrame(df_cleaned): The cleaned dataset with the following transformations:
        - Columns 'Employee_ID', 'Hire_Date', and 'Team_Size' are dropped.
        - Rows are filtered to include only 'IT' department and exclude certain 'Remote_Work_Frequency' values (75 and 25).
        - 'Remote_Work_Frequency' values are replaced with labels ('Remote', 'Hybrid', 'Onsite') and renamed to 'work_type'.
        - 'Promotions' and 'Training_Hours' columns are normalized to a 1-5 scale, and a 'Motivation_Score' is calculated as the average of four factors.
        - Column names are standardized to lowercase, and work types are set as an ordered categorical variable.

    Raises:
    KeyError: If any of the required columns ('Department', 'Remote_Work_Frequency', etc.) are missing.
    ValueError: If unexpected data types are encountered in columns used for numeric calculations 
                (e.g., non-numeric values in 'Promotions' or 'Training_Hours').

    Examples:
    >>> import pandas as pd
    >>> # Load a sample dataset
    >>> df = pd.read_csv("employee_data.csv")
    >>> # Apply the cleaning function
    >>> df_cleaned = cleaning(df)
    >>> # View the cleaned DataFrame
    >>> print(df_cleaned.head())

    Notes:
    - The function filters only for rows in the 'IT' department and excludes 'Remote_Work_Frequency' values of 25 and 75.
    - Converts 'Remote_Work_Frequency' values into readable labels ('Remote', 'Hybrid', 'Onsite') and renames the column to 'work_type'.
    - Adds a 'Motivation_Score' column as the average of normalized 'Employee_Satisfaction_Score', 'Performance_Score', 'Promotions', and 'Training_Hours' on a 1-5 scale.
    - Column names are converted to lowercase, and 'work_type' is set as an ordered categorical variable.
    """
    
    # Drop unnecessary columns, columns_to_drop = ['Employee_ID', 'Hire_Date', 'Team_Size']
    df_cleaned = df.drop(columns=['Employee_ID', 'Hire_Date', 'Team_Size'], errors='ignore')

    # Filter for only IT department and Remote work Frequencies to a more managable, 100, 50, 0
    df_cleaned = df_cleaned[(df_cleaned['Department'] == 'IT') & 
                (df_cleaned['Remote_Work_Frequency'] != 75) & 
                (df_cleaned['Remote_Work_Frequency'] != 25)].copy()

    # Replace Remote_Work_Frequency values with readable labels
    df_cleaned['Remote_Work_Frequency'] = df_cleaned['Remote_Work_Frequency'].replace({
        100: 'Remote',
        50: 'Hybrid',
        0: 'Onsite'
    })

    # Normalize 'Promotions' and 'Training Hours' to a 1-5 range to create a Motivations Score
    df_cleaned['Promotions_Normalized'] = (df_cleaned['Promotions'] / df_cleaned['Promotions'].max()) * 4 + 1
    df_cleaned['Training_Hours_Normalized'] = (df_cleaned['Training_Hours'] / df_cleaned['Training_Hours'].max()) * 4 + 1

    # Calculate the Motivation Score within a 1-5 range
    df_cleaned['Motivation_Score'] = (
    df_cleaned['Employee_Satisfaction_Score'] +
    df_cleaned['Performance_Score'] +
    df_cleaned['Promotions_Normalized'] +
    df_cleaned['Training_Hours_Normalized']
    ) / 4  # Averaging the four factors

    # Round the Motivation Score to 2 decimal places
    df_cleaned['Motivation_Score'] = df_cleaned['Motivation_Score'].round(2)

    # Drop the temporary normalization columns
    df_cleaned = df_cleaned.drop(columns=['Promotions_Normalized', 'Training_Hours_Normalized']).reset_index(drop=True)

    # Change column names to lowercase
    df_cleaned.columns = df_cleaned.columns.str.lower()

    # Rename 'remote_work_frequency' to 'work_type'
    df_cleaned = df_cleaned.rename(columns={'remote_work_frequency': 'work_type'})

    # Set the order of work_type categories
    df_cleaned['work_type'] = pd.Categorical(
    df_cleaned['work_type'],
    categories=['Remote', 'Hybrid', 'Onsite'],
    ordered=True
    )
    #display all columns
    pd.set_option('display.max_columns', None)
    print(df_cleaned.head())

    return df_cleaned

def describe_work_type_stats(df_cleaned, column_name='work_type', work_types=['Remote', 'Hybrid', 'Onsite']):   
    """
    Filters the DataFrame for specified work type values, groups by the work type column, 
    and calculates descriptive statistics for each group. The function displays all columns 
    in the output for easier analysis.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to analyze.
    column_name (str): The name of the column to filter and group by. Default is 'work_type'.
    work_types (list): A list of work type values to filter for (e.g., ['Remote', 'Hybrid', 'Onsite']).

    Returns:
    pandas.DataFrame: A DataFrame with descriptive statistics for each specified work type.

    Raises:
    KeyError: If the specified column name does not exist in the DataFrame.
    TypeError: If the input DataFrame is not a pandas DataFrame or if `column_name` is not a string.
    ValueError: If `work_types` is not a list.

    Notes:
    - The function uses `pd.set_option('display.max_columns', None)` to display all columns 
      in the output, making it easier to view all descriptive statistics.
    - The `observed=True` parameter in `groupby` limits grouping to observed categories only,
      which improves performance and aligns with future behavior in pandas.

    Examples:
    >>> import pandas as pd
    >>> # Assume df_cleaned is a DataFrame with a 'work_type' column
    >>> describe_stats = describe_work_type_stats(df_cleaned)
    >>> print(describe_stats)
    """
    
    # Filter data for specified work types
    filtered_df = df_cleaned[df_cleaned[column_name].isin(work_types)]

    # Group by work type and calculate descriptive statistics
    describe_stats = filtered_df.groupby(column_name, observed=True).describe()

    # Set display option to show all columns
    pd.set_option('display.max_columns', None)
    print(describe_stats)

    return describe_stats

def plot_work_type_distribution(df_cleaned, work_type):
    """
    Plots a donut chart showing the distribution in percentage of values of the work_type column.
    
    Parameters:
    df_cleaned(pandas.DataFrame): The DataFrame containing the data.
    work_type (str): The name of the column to analyze and plot.
    
    Returns:
    pandas.Series: The counts of each category in the specified column.

    Examples:
    counts = plot_work_type_distribution(df_cleaned, 'work_type')
    print(counts)

    Notes:
    The function saves the donut chart to the figures folder.
    
    """
    # Count the occurrences of each unique value in the specified column
    value_counts = df_cleaned['work_type'].value_counts()

    # Plot a donut chart
    plt.figure(figsize=(6, 6))
    plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=140, wedgeprops={'width': 0.3})
    plt.title(f"Distribution of {'Work Type'.capitalize()}")
    plt.show()

    #saves figure
    plt.savefig("../figures/distribution_of_work_type.jpeg", format="jpeg")

    # Return the counts
    return value_counts

def plot_stacked_work_and_overtime_hours(df_cleaned):
    """
    Plots the average work hours and overtime hours by work type as a stacked bar chart.

    The function calculates the average 'work_hours_per_week' and 'overtime_hours' 
    grouped by 'work_type' and plots these values in a stacked bar chart.

    Parameters:
    - df_cleaned(pandas.DataFrame): The input DataFrame expected to contain 'work_type', 'work_hours_per_week', and 'overtime_hours' columns.

    Returns:
    - None: The function displays the plot in the Jupyter notebook output and 
            saves the figure as a JPEG file

    Example Usage:
    # Assume df_cleaned is a DataFrame with the necessary columns.
    plot_stacked_work_and_overtime_hours(df_cleaned)
    
    Notes:
    - The stacked chart shows total hours per work type with sections representing 
      regular work hours and overtime hours.
    """
    
    # Calculate the mean work hours and overtime hours by work type
    mean_hours = df_cleaned.groupby('work_type', observed=True)[['work_hours_per_week', 'overtime_hours']].mean()

    # Plot a stacked bar chart
    plt.figure(figsize=(10, 6))
    work_types = mean_hours.index
    work_hours = mean_hours['work_hours_per_week']
    overtime_hours = mean_hours['overtime_hours']
    
    # Create stacked bars
    plt.bar(work_types, work_hours, label='Work Hours', color='skyblue')
    plt.bar(work_types, overtime_hours, bottom=work_hours, label='Overtime Hours', color='salmon')
    
    # Add labels and title
    plt.title("Average Work and Overtime Hours by Work Type")
    plt.ylabel("Average Hours")
    plt.xlabel("Work Type")
    plt.legend()

    #saves chart as a jpeg
    plt.savefig("../figures/work_hours.jpeg", format="jpeg", dpi=300)

    # Show the plot
    plt.show()

    return mean_hours

def calculate_avg_median_scores_by_work_type(df_cleaned):
    """
    Calculates the average (mean) and median scores for Performance, Motivation, 
    and Employee Satisfaction by work type.

    Parameters:
    - df_cleaned(pandas.DataFrame): The input DataFrame, expected to contain 'work_type', 'performance_score', 'motivation_score', and 
    'employee_satisfaction_score' columns. 
    
    Returns:
    - pandas.DataFrame: A pivot table showing the mean and median of each score type 
                        (Performance, Motivation, Satisfaction) by work type.

    Example Usage:
    >>> # Assume df_cleaned is a DataFrame with the necessary columns.
    >>> pivot_avg_scores = calculate_avg_median_scores_by_work_type(df_cleaned)
    >>> display(pivot_avg_scores)

    Notes:
    - The function creates a pivot table grouped by 'work_type', calculating both 
      mean and median values for 'performance_score', 'motivation_score', and 
      'employee_satisfaction_score'.
    """
    
    # Create the pivot table with mean and median for each score by work type
    pivot_avg_scores = df_cleaned.pivot_table(
        values=['performance_score', 'motivation_score', 'employee_satisfaction_score'],
        index='work_type',
        aggfunc=['mean', 'median'],
        observed=True
    )

    # Display the pivot table
    print(pivot_avg_scores)
    
    return pivot_avg_scores

def plot_average_scores_by_work_type(df_cleaned, work_type):
    """
    Calculates and plots the average scores for specified metrics by work type.

    This function groups the data by work type, calculates the mean scores for the specified columns, 
    and generates a bar chart to visualize the average scores. The plot can optionally be saved to a specified path.

    Parameters:
    df_cleaned(pandas.DataFrame): The DataFrame containing the data.
    work_type_column (str): The name of the column representing work type (e.g., 'Remote', 'Hybrid', 'Onsite'). Default is 'work_type'.
    score_columns (list): A list of column names for the metrics to calculate average scores for (e.g., ['performance_score', 'employee_satisfaction_score', 'motivation_score']).

    Returns:
    mean_score 
    saves the file as a jpeg
    Displays a bar chart of average scores by work type.

    Example Usage:
    plot_average_scores_by_work_type(df_cleaned, 'work_type')
    display(mean_scores_melted)

     Notes:
    - This function requires Seaborn for the bar chart and Matplotlib for plotting and saving the image.
    """
    
    # Calculate mean scores by work type
    mean_scores = df_cleaned.groupby('work_type', observed=True)[['performance_score', 'employee_satisfaction_score', 'motivation_score']].mean().reset_index()

    # Melt the DataFrame for easier plotting
    mean_scores_melted = mean_scores.melt(id_vars='work_type', var_name='Score Type', value_name='Average_Score')

    # Plot a bar chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=mean_scores_melted, x='Score Type', y='Average_Score', hue='work_type')
    plt.title("Average Scores of Performance, Satisfaction, and Motivation by Work Type")
    plt.ylabel("Average Score")
    plt.savefig("../figures/average_scores.jpeg", format="jpeg", dpi=300)
    plt.show()

    #display long format table
    print(mean_scores_melted)
    
    return mean_scores

def plot_scores_by_work_type(df_cleaned):
    """
    Creates box plots for Employee Satisfaction Score, Motivation Score, and Performance Score
    by work type.

    Parameters:
    - df_cleaned (pandas.DataFrame): The input DataFrame, expected to contain 'work_type', 'employee_satisfaction_score', 'motivation_score', 
    and 'performance_score' columns.
                             
    Returns:
    - None: The function displays the plot in the Jupyter notebook output and saves the figure as a JPEG file.

    Example Usage:
    >>> # Assume df_cleaned is a DataFrame with the necessary columns.
    >>> plot_scores_by_work_type(df_cleaned)
    
    Notes:
    - The function generates a box plot for each score type (Satisfaction, Motivation, Performance) 
      grouped by 'work_type' in a 1-row, 3-column layout.
    """
    
    # Set up the figure and individual box plots
    plt.figure(figsize=(14, 6))
    
    # Employee Satisfaction Score
    plt.subplot(1, 3, 1)
    sns.boxplot(x='work_type', y='employee_satisfaction_score', data=df_cleaned)
    plt.title('Employee Satisfaction Score by Work Type')

    # Motivation Score
    plt.subplot(1, 3, 2)
    sns.boxplot(x='work_type', y='motivation_score', data=df_cleaned)
    plt.title('Motivation Score by Work Type')

    # Performance Score
    plt.subplot(1, 3, 3)
    sns.boxplot(x='work_type', y='performance_score', data=df_cleaned)
    plt.title('Performance Score by Work Type')

    # Adjust layout for spacing
    plt.tight_layout()

    #save the plot
    plt.savefig("../figures/average_scores.jpeg", format="jpeg", dpi=300)
    
    # Show the plot
    plt.show()

def heat_map(df_cleaned):
    """
    Plots a heatmap showing the correlation between numerical columns in the DataFrame.

    Parameters:
    df_cleaned (pandas.DataFrame): The DataFrame containing the data.

    Returns:
    pandas.DataFrame: The correlation matrix of the numerical columns.

    Examples:
    correlation_matrix = heat_map(df_cleaned)
    print(correlation_matrix)

    Notes:
    The function saves the heatmap to the figures folder.
    
    """
    numerical_df = df_cleaned.select_dtypes(include='number')

    # Calculate the correlation matrix for numerical columns
    correlation_matrix = numerical_df.corr()

    # Plot the heatmap
    plt.figure(figsize=(12, 8))  # Adjust the figure size as needed
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap of Numerical Values")

    #save the plot
    plt.savefig("../figures/heat_map.jpeg", format="jpeg", dpi=300)

    #display the plot
    plt.show()