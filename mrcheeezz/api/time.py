def format_number(number):
    return "{:,}".format(number)

def time_to_ago(time):
    full_weeks_ago = int(time * (365 / 7))
    full_days_ago = int(time * 365)
    full_hours_ago = int(time * (365 * 24))
    full_minutes_ago = int(time * (365 * 24 * 60))
    full_seconds_ago = int(time * (365 * 24 * 60 * 60))
    full_milliseconds = int(time * (365 * 24 * 60 * 60 * 1000))

    years_ago = int(time)
    months_ago = int((time - years_ago) * 12)
    weeks_ago = int((time - years_ago - (months_ago / 12)) * (365 / 7))
    days_ago = int((time - years_ago - (months_ago / 12) - (weeks_ago / (365 / 7))) * 365)
    hours_ago = int((time - years_ago - (months_ago / 12) - (weeks_ago / (365 / 7)) - (days_ago / 365)) * (365 * 24))
    minutes_ago = int((time - years_ago - (months_ago / 12) - (weeks_ago / (365 / 7)) - (days_ago / 365) - (hours_ago / (24 * 365))) * (365 * 24 * 60))
    seconds_ago = int((time - years_ago - (months_ago / 12) - (weeks_ago / (365 / 7)) - (days_ago / 365) - (hours_ago / (24 * 365)) - (minutes_ago / (60 * 24 * 365))) * (365 * 24 * 60 * 60))

    times = {
        "years_ago": years_ago,
        "months_ago": months_ago,
        "weeks_ago": weeks_ago,
        "days_ago": days_ago,
        "hours_ago": hours_ago,
        "minutes_ago": minutes_ago,
        "seconds_ago": seconds_ago,
    }

    formatted_times = {
        "years_ago": f"{years_ago} year",
        "months_ago": f"{months_ago} month",
        "weeks_ago": f"{weeks_ago} week",
        "days_ago": f"{days_ago} day",
        "hours_ago": f"{hours_ago} hour",
        "minutes_ago": f"{minutes_ago} minute",
        "seconds_ago": f"{seconds_ago} second",
    }

    full_times = {
        "full_weeks_ago": full_weeks_ago,
        "full_days_ago": full_days_ago,
        "full_hours_ago": full_hours_ago,
        "full_minutes_ago": full_minutes_ago,
        "full_seconds_ago": full_seconds_ago,
        "full_milliseconds": full_milliseconds,
    }

    time_string = ''

    for time_key, formatted_time in formatted_times.items():
        number = int("".join(filter(str.isdigit, formatted_time)))

        if number > 999:
            formatted_times[time_key] = format_number(number)

        if number > 1:
            formatted_times[time_key] = formatted_times[time_key] + 's'

        if number != 0:
            time_string = time_string + formatted_times[time_key] + ' '

    return {
        "times": times,
        "full_times": full_times,
        "formatted_times": formatted_times,
        "time_string": time_string.strip()
    }
