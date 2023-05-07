from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    해당 게시글을 작성한 사용자만 쓰기, 보기, 수정, 삭제 권한이 주어진다.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
