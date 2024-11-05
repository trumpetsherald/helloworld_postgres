import random
import datetime
import numpy as np
import pandas as pd

def generate_nginx_log_data(
        day=None,
        avg_rate=10,
        time_min=1,
        time_max=1000,
        time_avg=300,
        status_dist={"200": .95,"201": .01,"404": .03,"500": .01},
        method_dist={"GET": 0.1, "POST": 0.9},
        response_size_min=1000,
        response_size_max=1000000,
        uri_dist={"/login": 0.1, "/main": 0.85, "/settings": 0.05},
        agent_dist={"safari": 0.2, "chrome": 0.3, "firefox": 0.3, "edge": 0.1, "other": 0.1},
        output_file="nginx_log_data.csv"
):
    # Set default day to today if not provided
    if day is None:
        day = datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                              microsecond=0)
        # Define diurnal pattern: an array of multipliers for each hour
        # Peak traffic at 12 PM (noon) and 6 PM, low traffic at 3 AM
    hourly_pattern = [
        0.1, 0.05, 0.05, 0.05, 0.05, 0.1,
        0.2, 0.3, 0.6, 0.8, 1.0, 1.2,
        1.5, 1.0, 0.8, 0.9, 1.1, 1.5,
        1.2, 1.0, 0.8, 0.5, 0.3, 0.2
    ]

    # Generate request times based on diurnal pattern
    request_times = []
    for hour in range(24):
        # Calculate the number of requests for this hour
        hour_rate = int(
            avg_rate * hourly_pattern[hour] * 3600)  # 3600 seconds in an hour
        hour_start = day + datetime.timedelta(hours=hour)

        # Generate timestamps within the hour
        hour_times = [
            hour_start + datetime.timedelta(seconds=int(second))
            for second in np.random.randint(0, 3600, hour_rate)
        ]
        request_times.extend(hour_times)

    # Sort all request times to keep them in order
    request_times.sort()

    # Total requests based on generated timestamps
    total_requests = len(request_times)

    # Generate request durations using a normal distribution within min, max, and avg constraints
    request_durations = np.clip(
        np.random.normal(time_avg, (time_max - time_min) / 3, total_requests),
        time_min, time_max
    ).astype(int)

    # Correlate response sizes with request durations (response_size proportional to request_duration)
    response_sizes = [
        int(response_size_min + (response_size_max - response_size_min) * (
                    duration - time_min) / (
                        time_max - time_min) + random.randint(-5000, 5000))
        for duration in request_durations
    ]
    response_sizes = np.clip(response_sizes, response_size_min,
                             response_size_max).tolist()

    # Generate methods based on distribution
    methods = random.choices(list(method_dist.keys()),
                             weights=method_dist.values(), k=total_requests)

    # Generate URIs based on distribution
    uris = random.choices(list(uri_dist.keys()), weights=uri_dist.values(),
                          k=total_requests)

    # Generate user agents based on distribution
    user_agents = random.choices(list(agent_dist.keys()),
                                 weights=agent_dist.values(), k=total_requests)

    # Generate status codes based on distribution
    status_codes = random.choices(list(status_dist.keys()),
                                 weights=status_dist.values(), k=total_requests)

    # Combine data into a DataFrame
    df = pd.DataFrame({
        "request_time": [rt.isoformat() for rt in request_times],
        "status_code": status_codes,
        "request_duration": request_durations,
        "method": methods,
        "response_size": response_sizes,
        "uri": uris,
        "user_agent": user_agents
    })

    return df

if __name__ == "__main__":
    # Example usage
    frame = generate_nginx_log_data()

    # Output to CSV
    frame.to_csv("nginx_log_data.csv", index=False)

    # Output to JSON
    frame.to_json("nginx_log_data.json", orient="records", indent=4)