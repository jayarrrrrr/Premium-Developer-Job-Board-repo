from django.db.models import Q


class SearchService:
    @staticmethod
    def build_filters(search_term=None, location=None):
        query = Q()
        if search_term:
            query &= (
                Q(title__icontains=search_term)
                | Q(company__icontains=search_term)
                | Q(summary__icontains=search_term)
            )
        if location:
            query &= Q(location__icontains=location)
        return query


class PaginationService:
    def __init__(self, page_size=10):
        self.page_size = page_size

    def get_page_offset(self, page):
        try:
            current_page = max(1, int(page))
        except (TypeError, ValueError):
            current_page = 1
        offset = (current_page - 1) * self.page_size
        return current_page, offset

    def get_meta(self, total_count, current_page):
        return {
            'page': current_page,
            'page_size': self.page_size,
            'total_items': total_count,
        }
