from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.upload import upload_image


class MultiImageActionsMixin:
    """
    Shared helpers for managing multi-image relationships.
    - Handle uploaded files on create/update
    - Delete removed images
    - Update image order
    - Provide a dedicated upload endpoint
    """

    image_model = None
    image_fk_field = None
    file_field = "image"
    cloud_folder = "home"

    def _upload_file(self, file):
        return upload_image(file, folder=self.cloud_folder)

    def _handle_images(self, instance):
        existing_ids = self.request.data.getlist("existing_images")
        qs = self.image_model.objects.filter(**{self.image_fk_field: instance})

        if existing_ids:
            qs.exclude(id__in=existing_ids).delete()
        else:
            qs.delete()

        files = self.request.FILES.getlist("images")
        for index, uploaded in enumerate(files):
            url = self._upload_file(uploaded)
            self.image_model.objects.create(
                **{
                    self.image_fk_field: instance,
                    "image": url,
                    "order": index,
                }
            )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._handle_images(instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self._handle_images(instance)
        return instance

    @action(detail=True, methods=["post"])
    def sort_images(self, request, pk=None):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Invalid payload, expected list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for item in request.data:
            self.image_model.objects.filter(id=item["id"]).update(order=item["order"])
        return Response({"success": True})

    @action(detail=True, methods=["post"])
    def images(self, request, pk=None):
        parent = self.get_object()
        files = request.FILES.getlist("images")
        objs = []
        for index, uploaded in enumerate(files):
            url_or_file = self._upload_file(uploaded)
            objs.append(
                self.image_model(
                    **{
                        self.image_fk_field: parent,
                        self.file_field: url_or_file,
                        "order": index,
                    }
                )
            )
        self.image_model.objects.bulk_create(objs)
        return Response({"success": True})
