from pydantic import BaseModel

class CommentGenRequest(BaseModel):
    post_title: str
    post_content: str
