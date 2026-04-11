from django.http import HttpResponse


def health(request):
    """轻量健康检查接口，用于部署探活和本地连通性校验。"""
    return HttpResponse("ok", status=200)
