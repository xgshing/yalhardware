from django.db.models import Avg, Count
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.views.frontend.auth_helpers import frontend_order_permissions
from apps.reviews.models import Review
from apps.reviews.serializers.frontend.review_append import ReviewAppendSerializer
from apps.reviews.serializers.frontend.review_create import ReviewCreateSerializer
from apps.reviews.serializers.frontend.review_read import ReviewReadSerializer
from apps.reviews.services.insights import (
    build_customers_say_summary,
    build_review_topics,
)


class ReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Review.objects.select_related("order_item", "order_item__product", "user")
        .prefetch_related("reply")
        .order_by("-created_at")
    )

    def get_permissions(self):
        if self.action in {"create", "append"}:
            return frontend_order_permissions()
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        order_item_id = params.get("order_item_id")
        product_id = params.get("product_id")
        mode = (params.get("filter") or "all").strip().lower()

        if order_item_id:
            queryset = queryset.filter(order_item_id=order_item_id)
        if product_id:
            queryset = queryset.filter(order_item__product_id=product_id)

        if mode == "with_media":
            queryset = queryset.exclude(images=[])
        elif mode in {"low_rating", "3_or_below"}:
            queryset = queryset.filter(rating__lte=3)
        elif mode in {"with_followup", "contains_followup"}:
            queryset = queryset.exclude(append_content="")
        elif mode in {"1", "2", "3", "4", "5"}:
            queryset = queryset.filter(rating=int(mode))

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewReadSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total = queryset.count()

        try:
            page = max(int(request.query_params.get("page", 1)), 1)
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = max(int(request.query_params.get("page_size", 10)), 1)
        except (TypeError, ValueError):
            page_size = 10

        start = (page - 1) * page_size
        end = start + page_size

        serializer = self.get_serializer(queryset[start:end], many=True)
        return Response(
            {
                "results": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        )

    def create(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(
            ReviewReadSerializer(review, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def append(self, request):
        serializer = ReviewAppendSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewReadSerializer(review, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        product_id = request.query_params.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self.queryset.filter(order_item__product_id=product_id)
        review_count = qs.count()
        if review_count == 0:
            return Response(
                {
                    "review_count": 0,
                    "average_rating": 0,
                    "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0},
                    "summary_text": "There are not enough customer reviews yet to generate a reliable summary.",
                    "topics": [],
                    "highlights": [],
                }
            )

        avg_rating = float(qs.aggregate(avg=Avg("rating")).get("avg") or 0)
        reviews = list(qs.values("content", "append_content"))
        review_texts = []
        for item in reviews:
            content = (item.get("content") or "").strip()
            append_content = (item.get("append_content") or "").strip()
            if content:
                review_texts.append(content)
            if append_content:
                review_texts.append(append_content)

        topics = build_review_topics(review_texts)
        summary_text = build_customers_say_summary(review_texts, avg_rating)
        highlights = [topic["title"] for topic in topics[:3]]
        distribution_rows = qs.values("rating").annotate(count=Count("id"))
        rating_distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for row in distribution_rows:
            key = str(row["rating"])
            if key in rating_distribution:
                rating_distribution[key] = int(row["count"])

        return Response(
            {
                "review_count": review_count,
                "average_rating": round(avg_rating, 1),
                "rating_distribution": rating_distribution,
                "summary_text": summary_text,
                "topics": topics,
                "highlights": highlights,
            }
        )
