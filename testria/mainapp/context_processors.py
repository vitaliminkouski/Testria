from .models import Folder

def get_user_folders(request):
    folders=[]
    if request.user.is_authenticated:
        folders = Folder.objects.filter(author=request.user, parent_folder__isnull=True).order_by('name')
    return {"user_folders": folders}