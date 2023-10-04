from admin.serializers import MovieAdminSerializer, UserAdminSerializer, GenreAdminSerializer, CommentAdminSerializer,\
                              TokenAdminSerializer

serializer_dict = {
    "movie": MovieAdminSerializer,
    "user": UserAdminSerializer,
    "genre": GenreAdminSerializer,
    "comment": CommentAdminSerializer,
    "token": TokenAdminSerializer
}
