from cloudinary import uploader

def upload(user_id, file_name, text):
    response = uploader.upload(file_name, context={'text':text}, tags=user_id)
    print response
    return response['secure_url'], response['public_id']
