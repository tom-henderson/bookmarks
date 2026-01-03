from datetime import datetime, timedelta
from calendar import month_abbr
from django.db.models import Count
from django.db.models.functions import TruncDate


def build_activity_chart(queryset, start_date):
    """
    Build activity chart data structure for exactly one year of data.
    
    Args:
        queryset: Django queryset to aggregate (e.g., Bookmark.objects.filter(...))
        start_date: datetime.date object for chart start (typically Jan 1)
    
    Returns:
        Dict with 'weeks' (list of weeks, each containing day dicts) 
        and 'month_labels' (list of month label dicts with offset positions).
    """
    # Calculate end date as exactly 1 year from start
    end_date = start_date + timedelta(days=365)
    
    # Query database for bookmark counts by date
    activity_data = queryset.filter(
        date_added__date__gte=start_date,
        date_added__date__lte=end_date
    ).annotate(
        date=TruncDate('date_added')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Convert to dict for O(1) lookup
    activity_dict = {str(item['date']): item['count'] for item in activity_data}
    
    # Build grid of all dates in the date range
    activity_grid = []
    current_date = start_date
    while current_date <= end_date:
        count = activity_dict.get(str(current_date), 0)
        activity_grid.append({
            'date': str(current_date),
            'count': count,
            'day_of_week': current_date.weekday()  # 0=Monday, 6=Sunday
        })
        current_date += timedelta(days=1)
    
    # Build weeks and month labels
    weeks = []
    current_week = []
    month_labels = []
    week_index = 0
    current_month = None
    
    # Adjust first day to start_date's day of week (convert to 0=Sunday)
    first_day_of_week = (activity_grid[0]['day_of_week'] + 1) % 7  # Convert Mon=0 to Sun=0
    
    # Add empty cells for the first week to align with Sunday
    for i in range(first_day_of_week):
        current_week.append({'date': None, 'count': 0, 'level': 0, 'title': None})
    
    # Process each day
    for index, day_data in enumerate(activity_grid):
        date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
        day_of_week = (day_data['day_of_week'] + 1) % 7  # Convert to 0=Sunday
        count = day_data['count']
        month = date_obj.month
        
        # Track month changes for labels (on Sundays)
        if day_of_week == 0 and month != current_month:
            month_labels.append({
                'week_index': week_index,
                'offset': week_index * 14 - 14,  # 11px width + 3px gap
                'label': month_abbr[month]
            })
            current_month = month
        
        # Determine color level (0-4) based on bookmark count
        level = 0
        if count > 0:
            level = 1
        if count >= 3:
            level = 2
        if count >= 5:
            level = 3
        if count >= 8:
            level = 4
        
        title = '{}: {} bookmark{}'.format(
            day_data['date'],
            count,
            's' if count != 1 else ''
        )
        
        current_week.append({
            'date': day_data['date'],  # Always include date for real days
            'count': count,
            'level': level,
            'title': title,
            'clickable': count > 0  # Only days with bookmarks are clickable
        })
        
        # Start new week on Saturday (day 6) or at end of data
        if day_of_week == 6 or index == len(activity_grid) - 1:
            weeks.append(current_week)
            current_week = []
            week_index += 1
    
    return {
        'weeks': weeks,
        'month_labels': month_labels
    }
