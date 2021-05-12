from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, ArticleViewSet, UserBookRelationViewSet, ReviewViewSet, DiscussionViewSet, \
    UserCommentRelationViewSet, CommentViewSet, UserDiscussionRelationViewSet, UserArticleRelationViewSet, \
    UserReviewRelationViewSet

store_router = SimpleRouter()

store_router.register('book', BookViewSet)
store_router.register('article', ArticleViewSet)
store_router.register('review', ReviewViewSet)
store_router.register('discussion', DiscussionViewSet)
store_router.register('comment', CommentViewSet)

store_router.register('book_relation', UserBookRelationViewSet)
store_router.register('comment_relation', UserCommentRelationViewSet)
store_router.register('discussion_relation', UserDiscussionRelationViewSet)
store_router.register('article_relation', UserArticleRelationViewSet)
store_router.register('review_relation', UserReviewRelationViewSet)
