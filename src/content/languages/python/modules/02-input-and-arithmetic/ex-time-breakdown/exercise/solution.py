def format_time(total_seconds):
    """Convert total_seconds into a 'M:SS' string."""
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


if __name__ == "__main__":
    print(format_time(200))   # 3:20
    print(format_time(60))    # 1:00
    print(format_time(0))     # 0:00
    print(format_time(3661))  # 61:01
    print(format_time(9))     # 0:09
