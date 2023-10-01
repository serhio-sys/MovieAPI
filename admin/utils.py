from admin.serializers import MovieAdminSerializer,UserAdminSerializer,GenreAdminSerializer,CommentAdminSerializer

serializer_dict = {
    "movie":MovieAdminSerializer,
    "user":UserAdminSerializer,
    "genre":GenreAdminSerializer,
    "comment":CommentAdminSerializer
}
