from . import permissions
from rest_framework import pagination
from rest_framework import mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.models import Gallery, Photo
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.mixins import (
    ListModelMixin as ListMM,
    CreateModelMixin as CreateMM,
    RetrieveModelMixin as RetrieveMM,
    UpdateModelMixin as UpdateMM,
    DestroyModelMixin as DestroyMM,
)


class CRUDPagination(pagination.PageNumberPagination):       
    page_size = 25

class CRUDMixins(ListMM, CreateMM, UpdateMM, RetrieveMM, DestroyMM):
    parser_classes = (FormParser, JSONParser, MultiPartParser)
    permission_classes = [permissions.IsAuthOrStaff]
    pagination_class = CRUDPagination
    UPDATE_METHODS = [
        "post",
        "put",
        "patch",
    ]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def querysearch(self):
        # perform query search on list view GET method

        qs = self.get_queryset()
        search = self.request.GET.get("q")
        query_filter = {}
        if search is not None:
            search = re.sub("/", "", search)
            if isinstance(self, Gallery):
                query_filter = {"name__icontains": qs}
            elif isinstance(self, Photo):
                query_filter = {"title__icontains": qs}
            qs = qs.filter(**query_filter).distinct()
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Check the serialized data is valid
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *arg, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # First we filter the queryset and check for any lookups
        # Example: api/gallery/q=lookup_this_gallery
        # Default behavior (no lookups) will return the unfiltered queryset
        qs = self.get_queryset()

        pqs = self.paginate_queryset(qs)

        if pqs is not None: # If pagination page is available
            serializer = self.get_serializer(pqs, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
