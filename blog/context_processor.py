from blog.models import Category, Author, CustomUser, Comment


def asd(request):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    usr = users.filter(id__in=user_list)

    params = {'categories': categories, 'authors': authors,
              'users': usr}
    return params