def convert_timedelta_to_string(timedelta):
    time_string = (
        str(timedelta.days)
        + " days "
        + str(timedelta.seconds // 3600)
        + " hours "
        + str((timedelta.seconds // 60) % 60)
        + " minutes "
    )
    return time_string
