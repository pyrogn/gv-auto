import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


def load_data(file_path):
    return pd.read_csv(file_path)


def interpolate_missing_values(df):
    df["bricks"] = df["bricks"].interpolate(method="linear")
    return df


def plot_progression_of_bricks(df, output_path):
    plt.figure(figsize=(10, 6))
    plt.plot(df["day"], df["bricks"], marker="o", linestyle="-", color="b")
    plt.title("Progression of Golden Bricks Count by Day")
    plt.xlabel("Day")
    plt.ylabel("Bricks")
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def calculate_average_new_bricks(df):
    df["new_bricks"] = df["bricks"].diff().fillna(0)
    return df["new_bricks"].mean()


def plot_average_new_bricks(df, average_new_bricks, output_path):
    plt.figure(figsize=(10, 6))
    plt.bar(df["day"], df["new_bricks"], color="orange")
    plt.axhline(
        y=average_new_bricks,
        color="r",
        linestyle="--",
        label=f"Average: {average_new_bricks:.2f}",
    )
    plt.title("Average Number of New Bricks Every Day")
    plt.xlabel("Day")
    plt.ylabel("New Bricks")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def fit_models(df):
    valid_days = df.dropna().day.values.reshape(-1, 1)
    valid_bricks = df.dropna().bricks.values

    # Linear regression model
    linear_model = LinearRegression()
    linear_model.fit(valid_days, valid_bricks)

    # Polynomial regression model
    poly = PolynomialFeatures(degree=2)  # Using a quadratic polynomial for this example
    valid_days_poly = poly.fit_transform(valid_days)

    poly_model = LinearRegression()
    poly_model.fit(valid_days_poly, valid_bricks)

    return linear_model, poly_model, poly


def project_bricks_to_1000(df, linear_model, poly_model, poly):
    future_days = np.arange(1, 201).reshape(-1, 1)  # Predict for the next 200 days

    # Linear projection
    predicted_bricks_linear = linear_model.predict(future_days)

    # Polynomial projection
    future_days_poly = poly.transform(future_days)
    predicted_bricks_poly = poly_model.predict(future_days_poly)

    try:
        day_1000_bricks_linear = future_days[
            np.where(predicted_bricks_linear >= 1000)[0][0]
        ][0]
    except IndexError:
        day_1000_bricks_linear = None

    try:
        day_1000_bricks_poly = future_days[
            np.where(predicted_bricks_poly >= 1000)[0][0]
        ][0]
    except IndexError:
        day_1000_bricks_poly = None

    return (
        future_days,
        predicted_bricks_linear,
        predicted_bricks_poly,
        day_1000_bricks_linear,
        day_1000_bricks_poly,
    )


def plot_projection_to_1000_bricks(
    df,
    future_days,
    predicted_bricks_linear,
    predicted_bricks_poly,
    day_1000_bricks_linear,
    day_1000_bricks_poly,
    output_path,
):
    plt.figure(figsize=(10, 6))
    plt.plot(
        df["day"], df["bricks"], marker="o", linestyle="-", color="b", label="Actual"
    )

    # Plot linear projection
    plt.plot(
        future_days,
        predicted_bricks_linear,
        linestyle="--",
        color="g",
        label="Linear Projection",
    )

    # Plot polynomial projection
    plt.plot(
        future_days,
        predicted_bricks_poly,
        linestyle="--",
        color="orange",
        label="Polynomial Projection",
    )

    plt.axhline(y=1000, color="r", linestyle="--", label="1000 Bricks")
    if day_1000_bricks_linear:
        plt.axvline(
            x=day_1000_bricks_linear,
            color="purple",
            linestyle="--",
            label=f"Linear: Day {day_1000_bricks_linear}",
        )
    if day_1000_bricks_poly:
        plt.axvline(
            x=day_1000_bricks_poly,
            color="blue",
            linestyle="--",
            label=f"Polynomial: Day {day_1000_bricks_poly}",
        )
    plt.title("Projection of When Bricks Count Will Reach 1000")
    plt.xlabel("Day")
    plt.ylabel("Bricks")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def main():
    # Load the dataset
    df = load_data("brick_stats.csv")

    # Fill missing values using linear interpolation
    df = interpolate_missing_values(df)

    # Plot 1: Progression of count by day
    plot_progression_of_bricks(df, "plots/progression_of_bricks_by_day.png")

    # Calculate average number of new bricks every day
    average_new_bricks = calculate_average_new_bricks(df)

    # Plot 2: Average number of new bricks every day
    plot_average_new_bricks(
        df, average_new_bricks, "plots/average_new_bricks_by_day.png"
    )

    # Fit linear and polynomial models
    linear_model, poly_model, poly = fit_models(df)

    # Projecting when the count will reach 1000 bricks using linear and polynomial regression
    (
        future_days,
        predicted_bricks_linear,
        predicted_bricks_poly,
        day_1000_bricks_linear,
        day_1000_bricks_poly,
    ) = project_bricks_to_1000(df, linear_model, poly_model, poly)

    # Plot 3: Projection of when the count will reach 1000 bricks
    plot_projection_to_1000_bricks(
        df,
        future_days,
        predicted_bricks_linear,
        predicted_bricks_poly,
        day_1000_bricks_linear,
        day_1000_bricks_poly,
        "plots/projection_1000_bricks.png",
    )

    # Print statistics
    print(f"Average number of new bricks every day: {average_new_bricks:.2f}")
    if day_1000_bricks_linear:
        print(
            f"Projected day to reach 1000 bricks (Linear): Day {day_1000_bricks_linear}"
        )
    else:
        print(
            "The projected count of bricks does not reach 1000 within the prediction range (Linear)."
        )
    if day_1000_bricks_poly:
        print(
            f"Projected day to reach 1000 bricks (Polynomial): Day {day_1000_bricks_poly}"
        )
    else:
        print(
            "The projected count of bricks does not reach 1000 within the prediction range (Polynomial)."
        )


if __name__ == "__main__":
    main()
